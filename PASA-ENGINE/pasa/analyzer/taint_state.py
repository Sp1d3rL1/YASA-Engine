# -*- coding: utf-8 -*-

"""
Manages the taint state of variables during analysis.
"""

import logging

logger = logging.getLogger(__name__)

class TaintState:
    """
    Tracks which variables are tainted.
    """
    def __init__(self):
        self.tainted_variables = set()

    def add_taint(self, var_name: str):
        """Marks a variable as tainted."""
        if var_name not in self.tainted_variables:
            logger.debug(f"Tainting variable: {var_name}")
            self.tainted_variables.add(var_name)

    def remove_taint(self, var_name: str):
        """Removes taint from a variable (e.g., after sanitization)."""
        if var_name in self.tainted_variables:
            logger.debug(f"Sanitizing variable: {var_name}")
            self.tainted_variables.discard(var_name)

    def is_tainted(self, var_name: str) -> bool:
        """Checks if a variable is tainted."""
        return var_name in self.tainted_variables

    def propagate(self, dest_var: str, src_vars: list):
        """Propagates taint from source variables to a destination variable."""
        for src_var in src_vars:
            if self.is_tainted(src_var):
                self.add_taint(dest_var)
                return # Taint is propagated, no need to check other sources