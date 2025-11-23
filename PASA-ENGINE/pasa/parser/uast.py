# -*- coding: utf-8 -*-

"""
Unified Abstract Syntax Tree (UAST) for PASA-ENGINE.

This module defines the node structure for the UAST, a language-agnostic
representation of source code. By converting language-specific ASTs (e.g.,
from Python's `ast` module) into this common format, the analysis engine can
operate on a single, unified structure. This mirrors the UAST concept in the
original YASA-Engine.
"""

import logging

logger = logging.getLogger(__name__)


class UASTNode:
    """
    The base class for all nodes in the Unified Abstract Syntax Tree.
    """

    def __init__(self, node_type, **kwargs):
        """
        Initializes a UAST node.

        Args:
            node_type: The type of the node (e.g., 'FunctionDefinition', 'CallExpression').
            **kwargs: A dictionary of attributes for the node, such as `loc`, `name`, etc.
        """
        self.type = node_type
        self.loc = kwargs.get('loc')  # Location info: { 'sourcefile': str, 'start': {'line': int, 'column': int}, ... }
        self.parent = kwargs.get('parent') # Reference to the parent node

        # Assign all other keyword arguments as attributes
        for key, value in kwargs.items():
            if key not in ('loc', 'parent'):
                setattr(self, key, value)

    def __repr__(self):
        """
        Provides a developer-friendly representation of the node.
        """
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items() if not k.startswith('_') and k != 'parent')
        return f"UASTNode(type='{self.type}', {attrs})"


# --- Example UAST Node Types (to be expanded) ---

class FileNode(UASTNode):
    def __init__(self, body, **kwargs):
        super().__init__('File', body=body, **kwargs)

class FunctionDefinition(UASTNode):
    def __init__(self, name, parameters, body, **kwargs):
        super().__init__('FunctionDefinition', name=name, parameters=parameters, body=body, **kwargs)

class CallExpression(UASTNode):
    def __init__(self, callee, arguments, **kwargs):
        super().__init__('CallExpression', callee=callee, arguments=arguments, **kwargs)

class Identifier(UASTNode):
    def __init__(self, name, **kwargs):
        super().__init__('Identifier', name=name, **kwargs)

class Literal(UASTNode):
    def __init__(self, value, **kwargs):
        super().__init__('Literal', value=value, **kwargs)

class AssignmentExpression(UASTNode):
    def __init__(self, left, right, operator='=', **kwargs):
        super().__init__('AssignmentExpression', left=left, right=right, operator=operator, **kwargs)

class BinaryExpression(UASTNode):
    def __init__(self, left, right, operator, **kwargs):
        super().__init__('BinaryExpression', left=left, right=right, operator=operator, **kwargs)

class IfStatement(UASTNode):
    def __init__(self, test, consequent, alternate, **kwargs):
        super().__init__('IfStatement', test=test, consequent=consequent, alternate=alternate, **kwargs)

class ReturnStatement(UASTNode):
    def __init__(self, argument, **kwargs):
        super().__init__('ReturnStatement', argument=argument, **kwargs)

class FormattedString(UASTNode):
    """Represents a formatted string, like an f-string in Python."""
    def __init__(self, parts, **kwargs):
        super().__init__('FormattedString', parts=parts, **kwargs)