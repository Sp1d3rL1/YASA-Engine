# PASA-ENGINE: A Python Static Analyzer

PASA-ENGINE is a static analysis tool designed to find security vulnerabilities in Python code. It is a Python-based re-implementation of the core concepts from the YASA-Engine, focusing on accessibility and clarity for Python developers.

## Core Design

The engine is built on a taint analysis model, which tracks the flow of untrusted data through the application. The key components are:

*   **Parser (`pasa/parser`)**: Converts Python source code into a language-agnostic Unified Abstract Syntax Tree (UAST). This allows the analyzer to work with a consistent data structure, regardless of the source language.
*   **Analyzer (`pasa/analyzer`)**: Traverses the UAST and performs taint propagation. It identifies sources (where tainted data enters the application), sinks (where tainted data can cause harm), and tracks the flow between them.
*   **Taint State (`pasa/analyzer/taint_state.py`)**: A simple state manager that keeps track of which variables are considered "tainted" at any point in the program's control flow.
*   **Checker & Result Management (`pasa/checker`, `pasa/result_manager.py`)**: A system for defining security rules (sources, sinks, sanitizers) and managing the findings reported by the analyzer.

## Project Structure

```
PASA-ENGINE/
├── pasa/
│   ├── analyzer/         # Core taint analysis logic
│   │   ├── analyzer.py
│   │   └── taint_state.py
│   ├── checker/          # Manages rules and findings
│   │   ├── checker_manager.py
│   │   └── ...
│   ├── parser/           # Code parsing and UAST generation
│   │   ├── python_parser.py
│   │   └── uast.py
│   ├── config.py         # Configuration management
│   ├── main.py           # Main entry point
│   └── result_manager.py # Handles findings
├── tests/                # Test suite
│   ├── test_analyzer.py
│   └── test_taint.py
└── setup.py              # Project setup for installation
```

## How to Run

1.  **Installation**:
    Install the project in editable mode to ensure all dependencies and paths are set up correctly.
    ```bash
    pip install -e PASA-ENGINE/
    ```

2.  **Running Analysis**:
    Use the main entry point `pasa/main.py` to run the analysis on a target file.
    ```bash
    python3 PASA-ENGINE/pasa/main.py <path_to_your_python_file.py>
    ```
    For example, to run the included taint test:
    ```bash
    python3 PASA-ENGINE/pasa/main.py PASA-ENGINE/tests/test_taint.py --log-level INFO
    ```

    The analysis will output any findings to the console.

## Current Status

The engine successfully implements a basic taint analysis workflow. It can parse Python code, propagate taint from predefined sources to sinks, and report vulnerabilities. The core logic is supported by a unit test suite to ensure its correctness.

This provides a solid foundation for understanding the principles of static analysis and can be extended with more sophisticated features, such as:
*   Inter-procedural analysis (tracking taint across function calls).
*   A formal rule engine for defining sources and sinks.
*   Support for more complex language features and frameworks.