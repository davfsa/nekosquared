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
MemberTypes = typing.Iterator[typing.Tuple[str, str, object]]


class ModuleWalker(scribe.Scribe):
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
                 skip_protected: bool=False) -> None:
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

        self.logger.setLevel('DEBUG')

    def __iter__(self) -> MemberTypes:
        """
        Gets an iterator across all members discovered and yields them as
        tuples of apparent names, real qualified names, and the respective
        object. The apparent name is respectful to the reference, while the
        real qualified name is what the reference points to. This enables us
        to differentiate between a type definition and a reference to a type in
        another module, say.
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

        This should return members in a mostly top-down manner.

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

                # Ensure we are in the defining module and it is not just a
                # reference.
                apparent_q_name = f'{root_name}.{name}'
                real_q_name = apparent_q_name

                try:
                    real_q_name = member.__module__ + '.' + member.__qualname__
                except:
                    pass

                if name.startswith('__'):
                    self.logger.debug(f'Skipping private member {name}')
                    continue
                elif name.startswith('_') and self._skip_protected:
                    self.logger.debug(f'Skipping protected member {name}')
                    continue
                else:
                    self.logger.debug(f'Inspecting {name}')

                # noinspection PyBroadException
                try:
                    if inspect.isclass(member):
                        self.logger.debug(f'{root_name}.{name} is a class')
                        module = member.__module__
                        if module.startswith(self.start.__name__):
                            yield (apparent_q_name, real_q_name, member)
                            yield from self._traverse(
                                real_q_name, member, already_indexed)
                    elif inspect.ismodule(member):
                        self.logger.debug(f'{root_name}.{name} is a class')
                        parent = member.__spec__.parent
                        if parent.startswith(self._root):
                            yield (apparent_q_name, real_q_name, member)
                            yield from self._traverse(
                                real_q_name, member, already_indexed)
                    elif inspect.isfunction(member):
                        # This ensures that decorated functions are undecorated
                        # first. Otherwise, for example, the presence of
                        # @asyncio.coroutine on a function would cause the
                        # function to report wrongly being defined in asyncio,
                        # not the actual file.
                        member = inspect.unwrap(member)

                    yield (apparent_q_name, real_q_name, member)

                except BaseException as ex:
                    self.logger.debug(f'ERROR {ex}')