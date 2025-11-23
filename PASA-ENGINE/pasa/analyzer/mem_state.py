# -*- coding: utf-8 -*-

"""
Memory and State Management for PASA-ENGINE.

This module provides utilities for managing the state of the symbolic execution,
especially for handling control flow branches (e.g., if statements, loops).
It includes functions to clone scopes and states, fork states at branches,
and union states after branches converge. This is the Python counterpart to
`memState.js` in the YASA-Engine.
"""

import logging
import copy

from pasa.analyzer.scope import Scope, ObjectValue

logger = logging.getLogger(__name__)


class MemState:
    """
    Manages the memory state for a specific path of symbolic execution.
    """

    def __init__(self, parent=None):
        self.pcond = []  # Path conditions
        self.callstack = []
        self.parent = parent # Parent state

    def clone(self):
        """
        Creates a deep copy of the current state.
        """
        # A deepcopy is a simple way to start, but can be slow.
        # YASA uses a more optimized, custom cloning approach (BVT).
        # We can optimize this later if performance becomes an issue.
        return copy.deepcopy(self)


def fork_states(state: MemState, num_forks: int = 2):
    """
    Forks the current memory state into multiple branches.

    Args:
        state: The current MemState.
        num_forks: The number of branches to create.

    Returns:
        A list of new MemState objects, one for each branch.
    """
    forked_states = []
    for _ in range(num_forks):
        new_state = state.clone()
        new_state.parent = state
        forked_states.append(new_state)
    return forked_states


def union_scopes(scope1: Scope, scope2: Scope) -> Scope:
    """
    Merges two scopes into a new scope.

    When fields conflict, their values are wrapped in a UnionValue.

    Args:
        scope1: The first scope.
        scope2: The second scope.

    Returns:
        A new Scope representing the union of the two inputs.
    """
    if not scope1:
        return scope2
    if not scope2:
        return scope1
    
    # For now, a simple strategy: prefer scope1's values in case of conflict.
    # A more advanced implementation would create UnionValue objects.
    # TODO: Implement proper unioning of values.
    
    new_scope = copy.copy(scope1) # Shallow copy
    new_scope.fields = copy.copy(scope1.fields) # Shallow copy of fields

    for field_name, value2 in scope2.fields.items():
        if field_name not in new_scope.fields:
            new_scope.fields[field_name] = value2
        else:
            value1 = new_scope.fields[field_name]
            if value1 != value2:
                # TODO: Create and use a UnionValue class
                logger.debug(f"Scope union conflict for '{field_name}'. Using value from first branch.")
                
    return new_scope


def union_states(states: list) -> MemState:
    """
    Merges a list of states into a single state.
    
    This is a placeholder for a more complex state-merging logic.
    For now, it just returns the first state in the list.

    Args:
        states: A list of MemState objects to merge.

    Returns:
        A single MemState representing the union.
    """
    if not states:
        return MemState()
    
    # TODO: Implement a proper state unioning logic.
    # This involves merging callstacks, path conditions, etc.
    return states[0]
