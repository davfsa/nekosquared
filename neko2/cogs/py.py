#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Gets information on various Python modules.

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
import contextlib
import io
from urllib import parse
import xmlrpc.client as xmlrpcclient

import discord

from discomaton.factories import bookbinding
from neko2.shared import alg, commands, string, traits


class PyCog(traits.CogTraits):
    @commands.command(brief="Shows Python documentation.")
    async def py(self, ctx, member):
        """Gets some help regarding the given Python member, if it exists..."""

        def executor():
            with io.StringIO() as buff:
                with contextlib.redirect_stdout(buff):
                    with contextlib.redirect_stderr(buff):
                        help(member)
                data = buff.getvalue().splitlines()

                return data

        data = await self.run_in_io_executor(executor)

        bb = bookbinding.StringBookBinder(
            ctx, max_lines=20, prefix="```markdown", suffix="```"
        )

        for line in data:
            line = line.replace("`", "′")
            bb.add_line(line)

        bb.start()

    @commands.group(
        invoke_without_command=True,
        aliases=["pip", "pip3"],
        brief="Searches PyPI for the given package name.",
    )
    async def pypi(self, ctx, package):
        """
        Input must be two or more characters wide.
        """
        if len(package) < 2:
            return await ctx.send(
                "Please provide at least two characters.", delete_after=10
            )

        def executor():
            # https://wiki.python.org/moin/PyPIXmlRpc
            # TODO: find a less shit way to do this
            # This is deprecated.
            client = xmlrpcclient.ServerProxy("https://pypi.python.org/pypi")
            return client.search({"name": package})

        with ctx.typing():
            results = await self.run_in_io_executor(executor)

        book = bookbinding.StringBookBinder(ctx, max_lines=None)

        head = f"**__Search results for `{package}`__**\n"
        for i, result in enumerate(results[:50]):
            if not i % 5:
                book.add_break()
                book.add_line(head)

            name = result["name"]
            link = f"<https://pypi.org/project/{parse.quote(name)}>"
            ver = result["version"]
            summary = result["summary"]
            summary = summary and f"- _{summary}_" or ""
            book.add_line(f"**{name}** ({ver}) {summary}\n\t{link}")

        try:
            booklet = book.build()
            if len(booklet) > 1:
                booklet.start()
            else:
                await ctx.send(booklet[0])
        except IndexError:
            await ctx.send("No results were found...", delete_after=10)

    @pypi.command(brief="Shows info for a specific PyPI package.")
    async def info(self, ctx, package):
        """
        Shows a summary for the given package name on PyPI, if there is one.
        """
        url = f"https://pypi.org/pypi/{parse.quote(package)}/json"

        # Seems like aiohttp is screwed up and will not parse these URLS.
        # Requests is fine though. Guess I have to use that...
        with ctx.typing():
            conn = await self.acquire_http()
            resp = await conn.get(url=url)
            result = (await resp.json()) if 200 <= resp.status < 300 else None

        if result:
            data = result["info"]

            name = f'{data["name"]} v{data["version"]}'
            url = data["package_url"]
            summary = data.get("summary", "_No summary was provided_")
            author = data.get("author", "Unknown")
            serial = result.get("last_serial", "No serial")
            if isinstance(serial, int):
                serial = f"Serial #{serial}"

            # Shortens the classifier strings.
            classifiers = data.get("classifiers", [])
            if classifiers:
                fixed_classifiers = []
                for classifier in classifiers:
                    print()
                    if "::" in classifier:
                        _, _, classifier = classifier.rpartition("::")
                    classifier = f"`{classifier.strip()}`"
                    fixed_classifiers.append(classifier)
                classifiers = ", ".join(sorted(fixed_classifiers))

            other_attrs = {
                "License": data.get("license"),
                "Platform": data.get("platform"),
                "Homepage": data.get("home_page"),
                "Requires Python version": data.get("requires_python"),
                "Classifiers": classifiers,
            }

            embed = discord.Embed(
                title=name,
                description=string.trunc(summary, 2048),
                url=url,
                colour=alg.rand_colour(),
            )

            embed.set_author(name=f"{author}")
            embed.set_footer(text=f"{serial}")

            for attr, value in other_attrs.items():
                if not value:
                    continue

                embed.add_field(name=attr, value=value)

            await ctx.send(embed=embed)

        else:
            await ctx.send(f"PyPI said: {resp.reason}", delete_after=10)


def setup(bot):
    bot.add_cog(PyCog())
