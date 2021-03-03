# -*- coding: utf-8 -*-

from contextlib import redirect_stdout
from datetime import datetime as dt
from discord.ext import commands
from typing import NamedTuple
import subprocess
import functools
import datetime
import textwrap
import humanize
import asyncio
import discord
import string
import utils
import io
import re


class TimeReason(NamedTuple):
    reason: str
    time: dt

    def __repr__(self) -> str:
        return f"<TimeReason time={self.time!r} reason={self.reason!r}>"

    def __str__(self) -> str:
        then = self.time - dt.utcnow()


time_regex = re.compile(r"""(?:(?P<seconds>[0-9]+)\s*(seconds?|secs?|s))?
                            (?:(?P<minutes>[0-9]+)\s*(minutes?|mins?|m))?
                            (?:(?P<hours>[0-9]+)\s*(hours?|hr?s?))?
                            (?:(?P<days>[0-9]+)\s*(days?|d))?
                            (?:(?P<weeks>[0-9]+)\s*(weeks?|w))?
                            (?:(?P<months>[0-9]+)\s*(months?|mo))?
                            (?:(?P<years>[0-9]+)\s*(years?|yr?s?))?""",
                            re.I | re.X)


class TimeConverter(commands.Converter):
    async def convert(self, ctx: utils.Context, arg: str):
        conversions = {
            "seconds": 0,
            "minutes": 60,
            "hours": 3600,
            "days": 86400,
            "weeks": 604800,
            "years": 31557600
        }

        now = dt.utcnow()

        if match := time_regex.finditer(arg):
            times = {}
            matches = [m.groupdict() for m in match if m.group(0)]
            for match in matches:
                for k, v in match.items():
                    if v:
                        times[k] = int(v)

            if not times:
                raise commands.BadArgument(
                    "Could not find a given time here. "
                    "Try something like `5 hours`."
                )

            for k, v in times.items():
                amount = conversions.get(k)
                secs = v * amount
                delta = datetime.timedelta(seconds=secs)
                now += delta

            return TimeReason("Test", now)


async def run_shell(command: str) -> bytes:
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    return stderr if stderr else stdout


class Owner(commands.Cog):
    """Commands for development."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: utils.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def reload(self, ctx: utils.Context):
        """Reloads all the currently loaded extensions."""

        extensions = [*self.bot.extensions.keys()]

        for extension in extensions:
            try:
                self.bot.reload_extension(extension)
            except Exception as e:
                await (ctx << f"{type(e).__class__} - {e}")

        await (ctx << "Successfully reloaded all extensions.")

    @commands.command()
    async def pull(self, ctx: utils.Context):
        """Pulls the latest code from the repo."""

        async with ctx.typing():
            res = await run_shell("git pull")
            stdout = res.decode("utf-8")

            fields = {"name": "Output", "value": f"```\n{stdout}```"}
            embed = self.bot.embed(ctx, fields=fields)
            await (ctx << embed)

    @commands.command()
    async def restart(self, ctx: utils.Context):
        """Restarts the bot."""

        await (ctx << "\U0001f97a Bye Bye")
        await self.bot.close()

    @commands.command(aliases=["sh"])
    async def shell(self, ctx: utils.Context, *, command: str):
        """Runs given arguments into shell."""

        async with ctx.typing():
            res = await run_shell(command)
            stdout = res.decode("utf-8")

            syntax = command.split(".")[-1] if command.split()[0] == "cat" else ""

            content = f"```{syntax}\n{stdout}```"
            await (ctx << content)

    @commands.command(name="eval")
    async def _eval(self, ctx: utils.Context, *, code: utils.get_code):
        """Evaluates python code."""

        env = {
            "ctx": ctx,
            "bot": ctx.bot,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "author": ctx.author,
            "message": ctx.message,
            "codeblock": lambda c: f"```py\n{c}```"
        }
        env.update(globals())

        block = (
            "async def _eval_expr():\n" + \
            textwrap.indent(code, "  ")
        )
        out = io.StringIO()
        exec(block, env, locals())

        with redirect_stdout(out):
            res = await locals()["_eval_expr"]()

        if value := out.getvalue():
            out.close()
            return await (ctx << value)

        out.close()

        if not res:
            return

        if res == "":
            res = "\u200b"

        if isinstance(res, discord.Embed):
            return await (ctx << res)

        elif isinstance(res, (str, int)):
            return await (ctx << res)

        else:
            return await (ctx << repr(res))


def setup(bot):
    bot.add_cog(Owner(bot))
