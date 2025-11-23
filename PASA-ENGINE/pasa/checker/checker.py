# -*- coding: utf-8 -*-

"""
Base Checker for PASA-ENGINE.

This module defines the base `Checker` class from which all specific security
checkers should inherit. It provides a common interface and structure for
implementing checker rules. Checkers inspect the code at various "checkpoints"
during the symbolic execution process.
"""

import logging

logger = logging.getLogger(__name__)


class Checker:
    """
    The base class for all security checkers.

    Subclasses should implement methods named with the prefix `check_at_`,
    which will be automatically discovered and registered by the CheckerManager.
    For example, `check_at_function_call_before` will be called before a
    function call is symbolically executed.
    """

    def __init__(self, checker_manager):
        """
        Initializes the Checker.

        Args:
            checker_manager: The manager to which this checker belongs.
        """
        self.checker_manager = checker_manager
        self.result_manager = checker_manager.get_result_manager()
        logger.info(f"Checker '{self.__class__.__name__}' initialized.")

    def report_finding(self, finding_data):
        """
        A helper method for checkers to report a new finding.

        Args:
            finding_data: A dictionary containing details about the finding.
        """
        if self.result_manager:
            self.result_manager.add_finding(finding_data)
        else:
            logger.error("ResultManager is not available. Cannot report finding.")
