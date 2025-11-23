# -*- coding: utf-8 -*-

"""
Scope and Symbolic Value Management for PASA-ENGINE.

This module defines the classes for managing scopes and representing symbolic
values during the analysis. A `Scope` holds the state of variables, functions,
and objects within a particular lexical context (e.g., global, function, block).
`SymbolicValue` and its subclasses represent the values of variables, which
might be concrete (like a Literal) or abstract (like a symbol representing
an unknown value). This corresponds to `scope.js` and the various value
types in YASA-Engine.
"""

import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class SymbolicValue:
    """
    Base class for all symbolic values in the analysis.
    """
    def __init__(self, vtype, **kwargs):
        self.vtype = vtype  # e.g., 'primitive', 'object', 'function'
        self.qid = kwargs.get('qid', f'sym_{uuid4().hex}')  # Unique identifier for the value
        self.ast_node = kwargs.get('ast_node') # Link back to the UAST node

    def __repr__(self):
        return f"<{self.vtype} qid={self.qid}>"


class PrimitiveValue(SymbolicValue):
    """
    Represents a primitive value, such as a number, string, or boolean.
    """
    def __init__(self, value, **kwargs):
        super().__init__('primitive', **kwargs)
        self.value = value

    def __repr__(self):
        return f"<Primitive value={self.value!r}>"


class UndefinedValue(SymbolicValue):
    """
    Represents an undefined or uninitialized value.
    """
    def __init__(self, **kwargs):
        super().__init__('undefined', **kwargs)


class Scope(SymbolicValue):
    """
    Represents a lexical scope, containing a symbol table (value map).
    """
    def __init__(self, scope_id, parent=None, **kwargs):
        """
        Initializes a Scope.

        Args:
            scope_id: A unique identifier for the scope (e.g., '<global>', 'my_function_scope').
            parent: The parent scope in the scope chain.
        """
        super().__init__('scope', qid=scope_id, **kwargs)
        self.id = scope_id
        self.parent = parent
        self.fields = {}  # Symbol table for this scope

    def get_member(self, name):
        """
        Retrieves a member's value from this scope or its parents.

        Args:
            name: The name of the member (variable, function, etc.) to find.

        Returns:
            The SymbolicValue associated with the name, or None if not found.
        """
        if name in self.fields:
            return self.fields[name]
        if self.parent:
            return self.parent.get_member(name)
        return None

    def set_member(self, name, value):
        """
        Sets a member's value in the current scope.

        Args:
            name: The name of the member.
            value: The SymbolicValue to assign.
        """
        if not isinstance(value, SymbolicValue):
            logger.warning(f"Attempted to set a non-symbolic value for '{name}'. Wrapping in PrimitiveValue.")
            value = PrimitiveValue(value)
        self.fields[name] = value

    def __repr__(self):
        return f"<Scope id='{self.id}' fields={list(self.fields.keys())}>"


class ObjectValue(Scope):
    """
    Represents an object, which is a specialized scope.
    """
    def __init__(self, scope_id='<object>', **kwargs):
        super().__init__(scope_id, **kwargs)
        self.vtype = 'object'


class FunctionValue(Scope):
    """
    Represents a function closure, which includes its definition and parent scope.
    """
    def __init__(self, fdef_node, parent_scope, **kwargs):
        scope_id = fdef_node.name.name if fdef_node.name else '<anonymous>'
        super().__init__(scope_id, parent=parent_scope, **kwargs)
        self.vtype = 'function'
        self.fdef = fdef_node  # The UAST node for the function definition

    def __repr__(self):
        return f"<Function id='{self.id}'>"
