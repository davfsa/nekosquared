#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementation of an ordered set data type.
"""
import collections
import typing

__all__ = ('OrderedSet', 'MutableOrderedSet', 'Stack')


SetType = typing.TypeVar('SetType')


class OrderedSet(collections.Set, typing.Generic[SetType]):
    """
    A set data-type that maintains insertion order. This implementation
    is immutable for the most part.
    """
    def __init__(self, iterable: typing.Iterable=None):
        """Initialise the set."""

        # This implementation is just a dictionary that only utilises the keys.
        # We use the OrderedDict implementation underneath.
        if iterable:
            self._dict = collections.OrderedDict({k: None for k in iterable})
        else:
            self._dict = collections.OrderedDict()

    def __contains__(self, x: SetType) -> bool:
        """Return true if the given object is present in the set."""
        return x in self._dict

    def __len__(self) -> int:
        """Get the length of the set."""
        return len(self._dict)

    def __iter__(self) -> typing.Iterator[SetType]:
        """Return an iterator across the set."""
        return iter(self._dict)

    def __getitem__(self, index: int) -> SetType:
        """Access the element at the given index in the set."""
        return list(self._dict.keys())[index]

    def __str__(self) -> str:
        """Get the string representation of the set."""
        return f'{{{",".join(repr(k) for k in self)}}}'

    __repr__ = __str__


# noinspection PyProtectedMember
class MutableOrderedSet(OrderedSet, collections.MutableSet):
    """An ordered set that allows mutation."""
    def add(self, x: SetType) -> None:
        """Adds a new element to the set."""
        self._dict[x] = None

    def discard(self, x: SetType) -> None:
        """Removes an element from the set."""
        self._dict.pop(x)


StackType = typing.TypeVar('StackType')


class Stack(collections.Sequence, typing.Generic[StackType]):
    """Implementation of a stack."""
    def __init__(self,
                 items: typing.Optional[typing.Sequence[StackType]] = None) \
            -> None:
        """
        Initialise the stack.
        :param items: the items to add to the stack initially.
        """
        self._stack = []
        if items:
            self._stack.extend(items)

    def __len__(self) -> int:
        """Get the stack length."""
        return len(self._stack)

    def __iter__(self) -> typing.Iterator[StackType]:
        """Get an iterator across the stack."""
        return iter(self._stack)

    def __contains__(self, x: object) -> bool:
        """Determine if the given object is in the stack."""
        return x in self._stack

    def __getitem__(self, index: int) -> StackType:
        """
        Get the item at the given index in the stack. Zero implies
        the bottom of the stack (first in).
        """
        return self._stack[index]

    def __setitem__(self, index: int, value: object) -> None:
        """
        Sets the value of the item in the given position in the stack.
        :param index: the index to edit at.
        :param value: the value to edit at.
        """
        self._stack[index] = value

    def push(self, x: StackType) -> StackType:
        """Pushes the item onto the stack and returns it."""
        self._stack.append(x)
        return x

    def pop(self) -> StackType:
        """Pops from the stack."""
        return self._stack.pop()

    def flip(self) -> None:
        """Flips the stack into reverse order in place."""
        self._stack = list(reversed(self._stack))

    def __str__(self) -> str:
        """Gets the string representation of the stack."""
        return str(self._stack)

    def __repr__(self) -> str:
        """Gets the string representation of the stack."""
        return repr(self._stack)

    def __bool__(self) -> bool:
        """Returns true if the stack is non-empty."""
        return bool(self._stack)
