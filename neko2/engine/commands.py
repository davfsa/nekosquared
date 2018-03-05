#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Provides some bits and pieces that are overridden from the default command
definitions provided by Discord.py.

This has been altered so that command errors are not dispatched from here
anymore. Instead, they are to be dispatched by the client.
"""
import typing  # Type checking

import cached_property    # Caching properties
# Used internally.
from discord.ext import commands as discord_commands
# Ensures these modules are in the same namespace.
# noinspection PyUnresolvedReferences
from discord.ext.commands.context import Context
# noinspection PyUnresolvedReferences
from discord.ext.commands.core import *
# noinspection PyUnresolvedReferences
from discord.ext.commands.converter import *
# noinspection PyUnresolvedReferences
from discord.ext.commands.cooldowns import *
# noinspection PyUnresolvedReferences
from discord.ext.commands.errors import *

BaseCommand = discord_commands.Command
BaseGroup = discord_commands.Group
BaseGroupMixin = discord_commands.GroupMixin


class CommandMixin:
    """
    Basic command implementation override.
    """
    name: property
    aliases: property
    full_parent_name: property
    qualified_name: property
    usage: property
    clean_params: property
    examples: list

    def __init__(self, *args, **kwargs):
        self.examples = kwargs.pop('examples', [])

    @cached_property.cached_property
    def names(self) -> typing.FrozenSet[str]:
        """Gets all command names."""
        return frozenset({self.name, *self.aliases})

    @cached_property.cached_property
    def qualified_aliases(self) -> typing.FrozenSet[str]:
        """Gets all qualified aliases."""
        parent_fqcn = self.full_parent_name
        if parent_fqcn:
            parent_fqcn += ' '
        return frozenset({parent_fqcn + alias for alias in self.aliases})

    @cached_property.cached_property
    def qualified_names(self) -> typing.FrozenSet[str]:
        """Gets all qualified names."""
        return frozenset({self.qualified_name, *self.qualified_aliases})


class Command(discord_commands.Command, CommandMixin):
    """Neko command: tweaks some stuff Discord.py provides."""
    def __init__(self, *args, **kwargs):
        discord_commands.Command.__init__(self, *args, **kwargs)
        CommandMixin.__init__(self, *args, **kwargs)


class Group(discord_commands.Group, CommandMixin):
    """Neko command group: tweaks some stuff Discord.py provides."""
    def __init__(self, *args, **kwargs):
        discord_commands.Group.__init__(self, *args, **kwargs)
        CommandMixin.__init__(self, *args, **kwargs)


def command(**kwargs):
    """Decorator for a command."""
    # Ensure the class is set correctly.
    cls = kwargs.pop('cls', Command)
    kwargs['cls'] = cls
    return discord_commands.command(**kwargs)


def group(**kwargs):
    """Decorator for a command group."""
    # Ensure the class is set correctly.
    cls = kwargs.pop('cls', Group)
    kwargs['cls'] = cls
    return discord_commands.command(**kwargs)
