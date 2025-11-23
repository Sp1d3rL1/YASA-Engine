# -*- coding: utf-8 -*-

"""
PASA-ENGINE
-----------

PASA-ENGINE is the Python implementation of YASA-Engine, a static analysis tool
for detecting security vulnerabilities in source code.

This module serves as the command-line entry point for the analysis process.
"""

import argparse
import logging
import os
import sys

# 将项目根目录添加到Python路径中，以便导入其他模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pasa.config import config
from pasa.analyzer.analyzer import Analyzer
from pasa.checker.checker_manager import CheckerManager

def main():
    """
    Main function to parse command-line arguments and initiate the analysis.
    """
    parser = argparse.ArgumentParser(description="PASA-ENGINE: Python Static Analyzer")
    parser.add_argument("target", help="The target file or directory to analyze.")
    parser.add_argument("-r", "--rules", help="Path to the rule configuration file.", required=True)
    parser.add_argument("-o", "--output", help="Path to the output report file.", default="report.json")
    parser.add_argument("-l", "--log-level", help="Set the logging level.",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')

    args = parser.parse_args()

    # 配置日志
    level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        stream=sys.stdout) # Explicitly set stream to stdout

    logging.info("Starting analysis...")
    logging.info(f"Target: {args.target}")
    logging.info(f"Rules: {args.rules}")
    logging.info(f"Output: {args.output}")

    # 1. 加载配置
    config.load_from_args(args)
    logging.info(f"Loaded config: {config}")

    # 2. 初始化 CheckerManager
    checker_manager = CheckerManager(config)
    # TODO: 从规则文件加载检查器
    # checker_manager.load_checkers_from_config(config.rule_path)

    # 3. 初始化 Analyzer
    analyzer = Analyzer(checker_manager)

    # 4. 启动分析
    findings = analyzer.analyze_project(config.project_root)

    # 5. 生成报告
    # TODO: 将 findings 写入输出文件
    result_manager = checker_manager.get_result_manager()
    # report = result_manager.get_sarif_format()
    logging.info(f"Findings: {findings}")
    
    logging.info("Analysis finished.")


if __name__ == '__main__':
    main()