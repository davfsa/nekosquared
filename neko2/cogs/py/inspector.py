#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Handles extracting anything exposed by a module.
"""
import builtins
import importlib
import inspect
import typing
from neko2.shared import scribe


ModuleType = type(builtins)
MemberTypes = typing.Iterator[typing.Tuple[str, object]]


class InspectionWalker(scribe.Scribe):
    """
    Walks across all members exposed in a module directly or indirectly, and
    yields tuples of their fully qualified name, and the actual object
    represented.

    This should not jump to modules and class definitions that are outside the
    start module provided. Function references and variables redefined inside
    a module that refer to a module outside of the tree will be yielded but not
    explored.
    """
    def __init__(self,
                 module: str,
                 relative_to: str=None,
                 skip_protected: bool=False):
        """
        Init the walker.
        :param module: the module name to explore.
        :param relative_to: the relative module path.
        :param skip_protected: true if we should ignore protected members.
                Defaults to false.
        """

        self.start = importlib.import_module(module, relative_to)
        self._root = self.start.__spec__.name
        self._skip_protected = skip_protected

        # self.logger.setLevel('DEBUG')

    def __iter__(self) -> MemberTypes:
        """
        Gets an iterator across all members discovered and yields them as
        tuples of names and the respective object.
        """
        yield from self._traverse(self.start.__name__, self.start)

    def _traverse(self,
                  root_name: str,
                  root: object,
                  already_indexed: set=None) -> MemberTypes:
        """
        Traverses the given object, yielding each child and their children,
        etc, recursively until we exhaust the tree. If a child is not defined
        in the same module as the parent passed to this function, we just
        yield that member and do not traverse it.

        Each child is a tuple of the fully qualified member name, and the
        representative object.

        Due to this algorithm, this returns results in a bottom-up order.

        (``already_indexed`` is only provided on recursive calls to this. This
        is a set of all modules already indexed, that way, we do not reference
        members multiple times. If you are calling this from anywhere except
        inside ``_traverse``, it should be left as None)
        """
        already_indexed = already_indexed if already_indexed else set()

        self.logger.debug(f'Inspecting members in {root_name}')
        if root not in already_indexed:
            already_indexed.add(root)

            for name, member in inspect.getmembers(root):
                qname = f'{root_name}.{name}'

                if name.startswith('__'):
                    self.logger.debug(f'Skipping private member {qname}')
                    continue
                elif name.startswith('_') and self._skip_protected:
                    self.logger.debug(f'Skipping protected member {qname}')
                    continue
                else:
                    self.logger.debug(f'Inspecting {qname}')

                # noinspection PyBroadException
                try:
                    if inspect.isclass(member):
                        self.logger.debug(f'{root_name}.{name} is a class')
                        module = member.__module__
                        if module.startswith(self.start.__name__):
                            yield from self._traverse(
                                qname, member, already_indexed)
                            yield (qname, member)
                    elif inspect.ismodule(member):
                        self.logger.debug(f'{root_name}.{name} is a class')
                        parent = member.__spec__.parent
                        if parent.startswith(self._root):
                            yield from self._traverse(
                                qname, member, already_indexed)
                            yield (qname, member)
                    else:
                        yield (qname, member)

                except BaseException as ex:
                    self.logger.debug(f'ERROR {ex}')