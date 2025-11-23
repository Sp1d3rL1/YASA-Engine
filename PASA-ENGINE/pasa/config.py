# -*- coding: utf-8 -*-

"""
Configuration Management for PASA-ENGINE.

This module provides a centralized configuration object that holds all settings
for the static analysis process, such as file paths, analysis parameters, and
feature flags. It mirrors the functionality of `config.js` in the original
YASA-Engine.
"""

import os


class Config:
    """
    A singleton-like class to store all configuration settings.
    """

    def __init__(self):
        # --- Core Paths ---
        # The root directory of the project being analyzed.
        self.project_root = os.getcwd()
        # The directory where reports will be saved.
        self.report_dir = "reports"
        # The path to the rule configuration file.
        self.rule_path = None

        # --- Analysis Parameters ---
        # The target language for the analysis.
        self.language = "python"
        # The target framework, if any.
        self.framework = None
        # Maximum depth for recursive function calls during analysis.
        self.max_call_depth = 10

        # --- Feature Flags ---
        # Whether to invoke callbacks on unknown functions.
        self.invoke_callback_on_unknown_function = True
        # The algorithm to use for state union at branches.
        # 1: Basic (approximated), 2: BVT (accurate)
        self.state_union_level = 2

        # --- Logging ---
        # Logging level, e.g., 'INFO', 'DEBUG'
        self.log_level = "INFO"
        # Directory to store log files.
        self.log_dir = "logs/pasa.log"

    def load_from_args(self, args):
        """
        Update configuration from command-line arguments.

        Args:
            args: An object containing parsed command-line arguments.
        """
        if args.target:
            self.project_root = os.path.abspath(args.target)
        if args.rules:
            self.rule_path = args.rules
        if args.output:
            self.report_dir = os.path.dirname(args.output)
        if args.log_level:
            self.log_level = args.log_level

    def __str__(self):
        return str(self.__dict__)


# Create a default config instance to be used across the application.
config = Config()