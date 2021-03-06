#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Uses webhooks to substitute Discord-style binds such as `/shrug` into messages
sent from Android devices without the substitution available.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import random

import discord

from discomaton.factories import bookbinding
from neko2.shared import alg, commands, traits


class TableFlipCog(traits.CogTraits):
    """
    If the bot used can make webhooks, if a message containing /shrug
    is sent, or one of the other discord binds, then the bot will delete
    the message, produce a webhook that imitates the user, and then resend
    the message in the corrected state. This "kinda" allows users on mobile
    to use desktop binds.
    """

    webhook_avatar_res = 64

    binds = {
        "/shrug": "¯\\\_(ツ)\_/¯",
        "/tableflip": ("(╯°□°）╯︵ ┻━┻", "(ノಠ益ಠ)ノ︵ ┻━┻"),
        "/unflip": "┬──┬﻿ ノ(° - °ノ)",
        "/lenny": "( ͡° ͜ʖ ͡°)",
        "/confused": "(⊙＿☉)",
        "/wizard": "(∩ >-<)⊃━☆ﾟ.*･｡ﾟ",
        "/happy": "(　＾∇＾)",
        "/dancing": ("(∼‾▿‾)∼", "(ノ^o^)ノ", "(ﾉ≧∀≦)ﾉ", "∼(‾▿‾)∼"),
        "/yay": "(ง^ᗜ^)ง",
        "/ayy": "(☞⌐■\_■)☞",
        "/ahh": "(ʘᗝʘ)",
        "/spy": "┬┴┬┴┤ ͜ʖ ͡°) ├┬┴┬┴",
        "/cry": "(πᗣπ)",
        "/shy": "（⌒▽⌒ゞ",
    }

    @commands.guild_only()
    @commands.command(name="binds", brief="Shows available binds.")
    async def view_binds(self, ctx):
        if ctx.guild.me.guild_permissions.manage_webhooks:
            binder = bookbinding.StringBookBinder(ctx)
            for bind_command, value in self.binds.items():
                if isinstance(value, tuple):
                    value = ", ".join(value)

                binder.add_line(f"• `{bind_command}`: {value}")
            binder.start()
        else:
            await ctx.send(
                "I don't seem to have the MANAGE_WEBHOOKS "
                "permission required for this to work. Please "
                "grant me that "
            )

    @classmethod
    async def delete_and_copy_handle_with_webhook(cls, message):
        http = await cls.acquire_http()

        channel: discord.TextChannel = message.channel
        author: discord.User = message.author

        # Use bit inception to get the avatar.
        avatar_url = author.avatar_url_as(format="png", size=cls.webhook_avatar_res)

        avatar_resp = await http.get(avatar_url)

        name = message.author.display_name
        if len(name) < 2:
            # Webhook length restriction.
            name = str(message.author)

        # noinspection PyUnresolvedReferences
        wh: discord.Webhook = await channel.create_webhook(
            name=name, avatar=await avatar_resp.read()
        )

        try:
            await message.delete()
        except:
            pass
        finally:
            await wh.send(content=message.content)
            await wh.delete()

    @classmethod
    async def on_message(cls, message):
        """
        On message, check for any binds. If we have a valid bind, first
        check to see whether we can make webhooks or not. If we can, we should
        generate a webhook that impersonates the user context.
        """
        author = message.author
        content = message.content

        # Cases where we should refuse to run.
        if message.guild is None:
            return
        if not message.guild.me.guild_permissions.manage_webhooks:
            return
        elif author.bot:
            return

        def pred(bind):
            """Matches the use of a Discord bind."""
            bind_whitespace = (f"{bind}\n", f"{bind} ")
            return content == bind or any(
                content.startswith(b) for b in bind_whitespace
            )

        bind = alg.find(pred, cls.binds)

        if not bind:
            return

        bind_result = cls.binds[bind]
        if isinstance(bind_result, tuple):
            bind_result = random.choice(bind_result)

        # If we matched a bind, remove it.
        message.content = message.content[len(bind) :].lstrip()
        message.content += f" {bind_result}"
        await cls.delete_and_copy_handle_with_webhook(message)


def setup(bot):
    bot.add_cog(TableFlipCog())
