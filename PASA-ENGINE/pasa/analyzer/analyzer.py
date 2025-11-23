# -*- coding: utf-8 -*-

"""
The Core Analyzer for PASA-ENGINE.

This module contains the main Analyzer class, which is responsible for
traversing the Unified Abstract Syntax Tree (UAST) and performing symbolic
execution. It manages the analysis state, invokes checkers at appropriate
AST nodes, and drives the entire vulnerability detection process. This class
is the Python counterpart to `analyzer.js` in the YASA-Engine.
"""

import logging
import os
from pasa.checker.checker_manager import CheckerManager
from pasa.parser.python_parser import PythonParser
from .taint_state import TaintState

logger = logging.getLogger(__name__)


class Analyzer:
    """
    The main AST analyzer that performs taint propagation analysis.
    """

    def __init__(self, checker_manager: CheckerManager, options: dict = None):
        """
        Initializes the Analyzer.

        Args:
            checker_manager: The manager responsible for invoking registered checkers.
            options: A dictionary of analysis options.
        """
        self.checker_manager = checker_manager
        self.options = options or {}
        self.source_code_cache = {}  # Caches source code for files
        self.uast_cache = {}  # Caches UAST for files
        self.statistics = {
            "num_processed_instructions": 0
        }

    def analyze_project(self, project_path: str):
        """
        Starts the analysis of a given project directory.

        Args:
            project_path: The absolute path to the project to be analyzed.
        """
        logger.info(f"Starting analysis for project: {project_path}")

        # --- Analysis Workflow ---
        # 1. Pre-process: Discover files, build call graphs if necessary.
        self.pre_process(project_path)

        # 2. Trigger 'start_analyze' checkpoint.
        self.checker_manager.check_at_start_of_analyze(self)

        # 3. Taint Analysis: Traverse UAST for each entry point.
        self.perform_taint_analysis()

        # 4. Trigger 'end_analyze' checkpoint.
        self.checker_manager.check_at_end_of_analyze(self)

        # 5. Record and return findings.
        return self.record_checker_findings()

    def pre_process(self, project_path: str):
        """
        Performs pre-processing steps, such as file discovery and parsing.
        This method will be language-specific.
        """
        logger.info("Performing pre-processing...")
        if os.path.isfile(project_path):
            self._process_file(project_path)
        elif os.path.isdir(project_path):
            for root, _, files in os.walk(project_path):
                for file in files:
                    if file.endswith(".py"):
                        self._process_file(os.path.join(root, file))

    def _process_file(self, file_path: str):
        """
        Reads, parses, and caches a single source file.
        """
        logger.info(f"Processing file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                self.source_code_cache[file_path] = source_code
                parser = PythonParser(source_code, filepath=file_path)
                uast = parser.parse()
                # Store UAST for later interpretation
                self.uast_cache[file_path] = uast
                logger.debug(f"UAST for {file_path}:\n{uast}")
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")

    def perform_taint_analysis(self):
        """
        Performs the main taint analysis loop over the parsed UASTs.
        """
        logger.info("Starting taint analysis...")
        for file_path, uast in self.uast_cache.items():
            logger.info(f"Analyzing file for taints: {file_path}")
            # Each file analysis starts with a fresh taint state.
            taint_state = TaintState()
            self.process_instruction(uast, taint_state)

    def process_instruction(self, node, taint_state):
        """
        Processes a single UAST node (instruction) for taint propagation.

        Args:
            node: The UAST node to process.
            taint_state: The current taint state.
        """
        if not node:
            return

        node_type = node.type
        handler_method_name = f"process_{node_type}"
        handler = getattr(self, handler_method_name, self.process_unhandled)

        self.statistics["num_processed_instructions"] += 1
        handler(node, taint_state)

    def process_unhandled(self, node, taint_state):
        """
        Handles UAST node types for which a specific handler is not implemented.
        """
        logger.warning(f"No handler for UAST node type: {node.type}")

    def process_File(self, node, taint_state):
        """
        Handles the top-level 'File' UAST node.
        """
        logger.debug(f"Processing File node: {node.loc.get('sourcefile', 'Unknown')}")
        for instruction in node.body:
            self.process_instruction(instruction, taint_state)

    def process_FunctionDefinition(self, node, taint_state):
        """
        Handles function definitions. For now we store/ignore; functions are
        analyzed when invoked. Here we can optionally scan default parameter
        expressions; currently skip body to avoid over-approximation.
        """
        return None

    def process_IfStatement(self, node, taint_state):
        """
        Processes if statements by executing both branches conservatively.
        """
        # Evaluate test expression for sources (even though we don't branch)
        self._get_source_vars(node.test, taint_state)
        for stmt in node.consequent:
            self.process_instruction(stmt, taint_state)
        for stmt in node.alternate:
            self.process_instruction(stmt, taint_state)

    def process_ImportStatement(self, node, taint_state):
        """Imports do not affect taint directly but must be handled."""
        return None

    def process_ImportFromStatement(self, node, taint_state):
        """from ... import ..."""
        return None

    def process_AssignmentExpression(self, node, taint_state):
        """
        Handles assignment to propagate taints.
        e.g., x = y
        If y is tainted, x becomes tainted.
        """
        dest_var = node.left.name if node.left.type == 'Identifier' else None
        if not dest_var:
            return

        src_vars = self._get_source_vars(node.right, taint_state)

        if '<TAINTED_SOURCE>' in src_vars:
            taint_state.add_taint(dest_var)
        else:
            taint_state.propagate(dest_var, src_vars)

    def process_CallExpression(self, node, taint_state):
        """
        Handles call expressions to identify sources and sinks.
        """
        # Simplistic source identification
        if node.callee.type == 'Identifier' and node.callee.name == 'user_input': # Example source
            # We return a tainted marker to AssignmentExpression through the call expression node.
            return '<TAINTED_SOURCE>'

        # Simplistic sink identification
        if node.callee.type == 'Identifier' and node.callee.name == 'execute_query': # Example sink
            for arg in node.arguments:
                if arg.type == 'Identifier' and taint_state.is_tainted(arg.name):
                    logger.critical(f"Tainted data reached a sink at {node.loc}!")
                    # Report a finding
                    finding = {
                        "type": "Taint-SQL-Injection",
                        "message": f"Tainted data from variable '{arg.name}' reached a SQL query sink.",
                        "sourcefile": node.loc.get("sourcefile"),
                        "line": node.loc.get("start", {}).get("line")
                    }
                    self.checker_manager.get_result_manager().add_finding(finding)

    def _get_source_vars(self, node, taint_state):
        """
        Recursively extracts variable names from an expression node and checks for new taints.
        """
        if node is None:
            return []
        if node == '<TAINTED_SOURCE>':
            return ['<TAINTED_SOURCE>']
        if node.type == 'Identifier':
            return [node.name]
        if node.type == 'BinaryExpression':
            return self._get_source_vars(node.left, taint_state) + self._get_source_vars(node.right, taint_state)
        if node.type == 'CallExpression':
            call_result = self.process_CallExpression(node, taint_state)
            if call_result == '<TAINTED_SOURCE>':
                return ['<TAINTED_SOURCE>']
            collected = []
            for arg in node.arguments:
                collected.extend(self._get_source_vars(arg, taint_state))
            return collected
        if node.type == 'Attribute':
            return self._get_source_vars(node.value, taint_state)
        if node.type == 'Subscript':
            return self._get_source_vars(node.value, taint_state)
        if node.type in ('Tuple', 'List'):
            collected = []
            elements = getattr(node, 'elements', [])
            for element in elements:
                collected.extend(self._get_source_vars(element, taint_state))
            return collected
        if node.type == 'Dict':
            collected = []
            values = getattr(node, 'values', [])
            for value in values:
                collected.extend(self._get_source_vars(value, taint_state))
            return collected
        # TODO: Add handlers for other expression types
        return []

    def record_checker_findings(self):
        """
        Retrieves and returns the findings collected by the checkers.
        """
        result_manager = self.checker_manager.get_result_manager()
        if result_manager:
            return result_manager.get_findings()
        return {}
