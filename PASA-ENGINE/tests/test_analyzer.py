# -*- coding: utf-8 -*-

"""
Unit tests for the Analyzer.
"""

import unittest
from pasa.analyzer.analyzer import Analyzer
from pasa.checker.checker_manager import CheckerManager
from pasa.parser.python_parser import PythonParser
from pasa.result_manager import ResultManager

class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up a fresh analyzer for each test."""
        # We need a real ResultManager to test finding generation
        result_manager = ResultManager()
        # The CheckerManager orchestrates this
        checker_manager = CheckerManager(result_manager)
        self.analyzer = Analyzer(checker_manager)

    def _analyze_code(self, code):
        """Helper function to parse and run analysis on a code snippet."""
        parser = PythonParser(code, filepath="test_snippet.py")
        uast = parser.parse()
        self.analyzer.uast_cache["test_snippet.py"] = uast
        self.analyzer.perform_taint_analysis()
        return self.analyzer.checker_manager.get_result_manager().get_findings()

    def test_simple_taint_propagation(self):
        """Test basic taint flow from source to sink."""
        code = """
user_input = user_input()
execute_query(user_input)
        """
        findings = self._analyze_code(code)
        self.assertEqual(len(findings["Taint-SQL-Injection"]), 1)
        finding = findings["Taint-SQL-Injection"][0]
        self.assertIn("Tainted data from variable 'user_input'", finding["message"])

    def test_no_taint_no_finding(self):
        """Test that clean data does not trigger a finding."""
        code = """
safe_input = "some_static_string"
execute_query(safe_input)
        """
        findings = self._analyze_code(code)
        self.assertNotIn("Taint-SQL-Injection", findings)

    def test_transitive_taint_propagation(self):
        """Test taint flow through an intermediate variable."""
        code = """
a = user_input()
b = a
c = b
execute_query(c)
        """
        findings = self._analyze_code(code)
        self.assertEqual(len(findings["Taint-SQL-Injection"]), 1)
        finding = findings["Taint-SQL-Injection"][0]
        self.assertIn("Tainted data from variable 'c'", finding["message"])

if __name__ == '__main__':
    unittest.main()