# -*- coding: utf-8 -*-

"""
Python Parser for PASA-ENGINE.

This module is responsible for parsing Python source code and converting it
into the Unified Abstract Syntax Tree (UAST) format defined in `uast.py`.
It uses Python's built-in `ast` module to generate a native Abstract Syntax
Tree, which is then traversed and transformed into our language-agnostic UAST.
"""

import ast
import logging
from pasa.parser.uast import *

logger = logging.getLogger(__name__)


class PythonParser:
    """
    A parser that converts Python source code into UAST.
    """

    def __init__(self, source_code, filepath="<string>"):
        """
        Initializes the parser.

        Args:
            source_code: The Python source code to parse.
            filepath: The name of the file being parsed.
        """
        self.source_code = source_code
        self.filepath = filepath

    def parse(self):
        """
        Parses the source code and returns the root of the UAST.

        Returns:
            The root UASTNode of the parsed code, or None on failure.
        """
        try:
            native_ast = ast.parse(self.source_code, filename=self.filepath)
            return self.transform(native_ast)
        except SyntaxError as e:
            logger.error(f"Failed to parse Python code in {self.filepath}: {e}")
            return None

    def transform(self, node):
        """
        Recursively transforms a native Python AST node into a UAST node.

        Args:
            node: A node from Python's `ast` module.

        Returns:
            A corresponding UASTNode.
        """
        if node is None:
            return None

        # Get the class name of the node (e.g., 'Module', 'FunctionDef')
        node_class_name = node.__class__.__name__
        transform_method_name = f"transform_{node_class_name}"
        transformer = getattr(self, transform_method_name, self.transform_unhandled)

        return transformer(node)

    def _get_location(self, node):
        """
        Extracts location information from a native AST node.
        """
        if hasattr(node, 'lineno'):
            return {
                "sourcefile": self.filepath,
                "start": {"line": node.lineno, "column": node.col_offset},
                "end": {"line": node.end_lineno, "column": node.end_col_offset}
            }
        return None

    def transform_unhandled(self, node):
        """
        Handles AST nodes that don't have a specific transformation method.
        """
        logger.warning(f"No transformer for Python AST node type: {node.__class__.__name__}")
        # Return a generic node to avoid crashing the traversal
        generic_node = UASTNode(f"Unhandled_{node.__class__.__name__}", loc=self._get_location(node))
        # Attempt to transform children generically if they exist
        if hasattr(node, 'body') and isinstance(node.body, list):
            generic_node.body = [self.transform(child) for child in node.body]
        elif hasattr(node, 'value'):
            generic_node.value = self.transform(node.value)
        return generic_node

    # --- AST Node Transformers ---

    def transform_Module(self, node):
        body = [self.transform(child) for child in node.body]
        # A Module node itself doesn't have line numbers in the same way statements do.
        # We can create a location that spans the whole file.
        start_loc = {"line": 1, "column": 0}
        end_loc = {"line": len(self.source_code.splitlines()), "column": 0} # Approximate
        loc = {"sourcefile": self.filepath, "start": start_loc, "end": end_loc}
        return FileNode(body, loc=loc)

    def transform_Import(self, node):
        names = [self.transform(alias) for alias in node.names]
        return UASTNode('ImportStatement', names=names, loc=self._get_location(node))

    def transform_ImportFrom(self, node):
        module = node.module
        names = [self.transform(alias) for alias in node.names]
        return UASTNode('ImportFromStatement', module=module, names=names, loc=self._get_location(node))

    def transform_alias(self, node):
        # Handles import aliases (ast.alias)
        return UASTNode('ImportAlias', name=node.name, asname=node.asname, loc=self._get_location(node))

    def transform_FunctionDef(self, node):
        name = Identifier(node.name, loc=self._get_location(node))
        # TODO: Transform parameters (node.args)
        params = []
        body = [self.transform(child) for child in node.body]
        return FunctionDefinition(name, params, body, loc=self._get_location(node))

    def transform_Expr(self, node):
        # An expression statement, we just transform its value
        return self.transform(node.value)

    def transform_Call(self, node):
        callee = self.transform(node.func)
        args = [self.transform(arg) for arg in node.args]
        # TODO: Transform keywords
        return CallExpression(callee, args, loc=self._get_location(node))

    def transform_Name(self, node):
        return Identifier(node.id, loc=self._get_location(node))

    def transform_Constant(self, node):
        # For Python 3.8+
        return Literal(node.value, loc=self._get_location(node))
        
    def transform_Num(self, node):
        # For older Python versions (before 3.8)
        return Literal(node.n, loc=self._get_location(node))

    def transform_Str(self, node):
        # For older Python versions (before 3.8)
        return Literal(node.s, loc=self._get_location(node))

    def transform_Assign(self, node):
        # Note: Python's Assign can have multiple targets.
        # For simplicity, we'll handle the first target for now.
        left = self.transform(node.targets[0])
        right = self.transform(node.value)
        return AssignmentExpression(left, right, loc=self._get_location(node))

    def transform_BinOp(self, node):
        from .uast import BinaryExpression # Late import to avoid circular dependency if uast grows
        left = self.transform(node.left)
        right = self.transform(node.right)
        op_map = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.Mod: '%', ast.Pow: '**', ast.LShift: '<<', ast.RShift: '>>',
            ast.BitOr: '|', ast.BitXor: '^', ast.BitAnd: '&', ast.FloorDiv: '//'
        }
        operator = op_map.get(type(node.op), '?')
        return BinaryExpression(left, right, operator, loc=self._get_location(node))

    def transform_If(self, node):
        from .uast import IfStatement # Late import
        test = self.transform(node.test)
        body = [self.transform(child) for child in node.body]
        orelse = [self.transform(child) for child in node.orelse] if node.orelse else []
        return IfStatement(test, body, orelse, loc=self._get_location(node))
        
    def transform_Compare(self, node):
        # Handles comparisons like __name__ == "__main__"
        from .uast import BinaryExpression
        # Simplifies to the first comparison for now
        left = self.transform(node.left)
        right = self.transform(node.comparators[0])
        op_map = {
            ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=',
            ast.Gt: '>', ast.GtE: '>=', ast.Is: 'is', ast.IsNot: 'is not',
            ast.In: 'in', ast.NotIn: 'not in'
        }
        operator = op_map.get(type(node.ops[0]), '?')
        return BinaryExpression(left, right, operator, loc=self._get_location(node))

    def transform_Return(self, node):
        argument = self.transform(node.value)
        return ReturnStatement(argument, loc=self._get_location(node))

    def transform_JoinedStr(self, node):
        # f-string in Python
        parts = [self.transform(value) for value in node.values]
        return FormattedString(parts, loc=self._get_location(node))

    def transform_FormattedValue(self, node):
        # This is part of a JoinedStr (f-string).
        # We transform the inner value.
        return self.transform(node.value)

    def transform_Attribute(self, node):
        value = self.transform(node.value)
        attr = node.attr
        return UASTNode('Attribute', value=value, attr=attr, loc=self._get_location(node))

    def transform_Subscript(self, node):
        value = self.transform(node.value)
        slice_node = self.transform(node.slice)
        return UASTNode('Subscript', value=value, slice=slice_node, loc=self._get_location(node))

    def transform_Tuple(self, node):
        elements = [self.transform(elt) for elt in node.elts]
        return UASTNode('Tuple', elements=elements, loc=self._get_location(node))

    def transform_List(self, node):
        elements = [self.transform(elt) for elt in node.elts]
        return UASTNode('List', elements=elements, loc=self._get_location(node))

    def transform_Dict(self, node):
        keys = [self.transform(key) for key in node.keys]
        values = [self.transform(value) for value in node.values]
        return UASTNode('Dict', keys=keys, values=values, loc=self._get_location(node))

    # ... other transform methods for different ast node types will be added here.
