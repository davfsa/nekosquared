#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Provides some natural language translations.

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

import googletrans
from discomaton.factories import bookbinding
from neko2.shared import traits, commands, fuzzy


class TransCog(traits.CogTraits):
    @commands.group(
        brief="Translate between languages.",
        aliases=["trans", "t"],
        invoke_without_command=True,
    )
    async def translate(self, ctx, source_lang, dest_lang, *, phrase):
        """
        Required arguments:

        `source_lang` - ISO 3166 country code or name to translate from.
        `dest_lang` - ISO 3166 country code or name to translate to.
        `phrase` - a string to attempt to translate.

        If you specify `\*`, `.` or `auto` for a language, it will detect
        automatically. The default destination language is English.

        To view a list of supported languages, run `n.t list`

        To translate the previous sent message, you can run `n.t ^`.
        """
        if source_lang in ("*", "."):
            source_lang = "auto"
        if dest_lang in ("*", "."):
            dest_lang = "en"

        def fuzzy_wuzzy_match(input_name):
            match = fuzzy.extract_best(input_name, googletrans.LANGUAGES.values())
            if match is None:
                raise NameError("Not a recognised language")
            else:
                return googletrans.LANGCODES[match[0]]

        try:
            acceptable_langs = (*googletrans.LANGUAGES.keys(), "auto")

            source_lang = source_lang.lower()
            dest_lang = dest_lang.lower()
            if source_lang not in acceptable_langs:
                source_lang = fuzzy_wuzzy_match(source_lang)
            if dest_lang not in acceptable_langs:
                dest_lang = fuzzy_wuzzy_match(dest_lang)

            def pool():
                return googletrans.Translator().translate(
                    phrase, dest_lang, source_lang
                )

            result = await self.run_in_io_executor(pool)

            if result is None:
                await ctx.send("No response...", delete_after=10)
            else:
                source = googletrans.LANGUAGES[result.src].title()
                dest = googletrans.LANGUAGES[result.dest].title()

                book = bookbinding.StringBookBinder(ctx, max_lines=10)
                book.add_line(f"_From **{source}** to **{dest}**_", empty_after=True)

                book.add(result.text)

                book = book.build()

                if len(book) > 1:
                    await book.start()
                else:
                    await ctx.send(book.pages[0])

        except Exception as ex:
            await ctx.send(str(ex).title(), delete_after=10)

    @translate.command(brief="View a list of supported languages")
    async def list(self, ctx):
        langs = [
            f"`{code}` - {lang.title()}" for code, lang in googletrans.LANGUAGES.items()
        ]

        book = bookbinding.StringBookBinder(ctx)
        for line in langs:
            book.add_line(line)

        await book.start()

    @translate.command(
        brief="Translate whatever was just sent previously.",
        name="that",
        aliases=["this", "^", "^^"],
    )
    async def translate_that(self, ctx, to="en"):
        """
        Pass an optional language to translate to. If nothing is specified,
        I will assume you want English: the best language of them all 😉
        """
        # Get the previous message.
        history = await ctx.channel.history(limit=2).flatten()

        if len(history) < 2 or not history[-1].content:
            await ctx.send("I can't seem to find a message...", delete_after=10)
        else:
            await self.translate.callback(
                self, ctx, "*", to, phrase=history[-1].content
            )


def setup(bot):
    bot.add_cog(TransCog())
