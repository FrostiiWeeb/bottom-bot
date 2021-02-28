# -*- coding: utf-8 -*-

from contextlib import redirect_stdout
from discord.ext import commands
from datetime import datetime as dt
from typing import NamedTuple
import subprocess
import functools
import datetime
import textwrap
import discord
import utils
import io
import re


class TimeReason(NamedTuple):
    reason: str
    time: dt

    def __repr__(self) -> str:
        return f"<TimeReason {reason} time={time!r}>"

    def __str__(self) -> str:
        now = dt.utcnow()
        in_time = self.time - now
        fmt = []

        if y := in_time.year:
            plural = "years" if y > 1 else "year"
            fmt.append(f"{y} {plural}")

        if m := in_time.month:
            plural = "month" if y > 1 else "month"
            fmt.append(f"{m} {plural}")

        if d := in_time.day:
            plural = "days" if y > 1 else "day"
            fmt.append(f"{d} {plural}")

        if h := in_time.hour:
            plural = "hours" if y > 1 else "hour"
            fmt.append(f"{h} {plural}")

        if m := in_time.minute:
            plural = "minutes" if y > 1 else "minute"
            fmt.append(f"{m} {plural}")

        return ", ".join(fmt)


time_regex = re.compile(r"""(?:(?P<seconds>([0-9]+))\s*?(s|sec|secs|second|seconds))?
                            (?:(?P<minutes>([0-9]+))\s*?(m|min|mins|minute|minutes))?
                            (?:(?P<hours>([0-9]+))\s*?(h|hr|hrs|hour|hours))?
                            (?:(?P<days>([0-9]+))\s*?(d|day|days))?
                            (?:(?P<weeks>([0-9]+))\s*?(w|week|weeks))?
                            (?:(?P<months>([0-9]+))\s*?(mo|month|months))?
                            (?:(?P<years>([0-9]+))\s*?(y|yr|yrs|year|years))?""", re.I | re.X)


def git_pull():
    return subprocess.run(["git", "pull"], capture_output=True)


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
                        times[k] = v

            for k, v in times.items():
                amount = conversions.get(k)
                secs = v * amount
                delta = datetime.timedelta(seconds=secs)
                now += delta

            return TimeReason("Test", now)


class Owner(commands.Cog):
    """Commands for development."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: utils.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def reload(self, ctx: utils.Context):
        """Realoads all the currently loaded extensions."""

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
            func = functools.partial(git_pull)
            res = await self.bot.loop.run_in_executor(None, func)
            stdout = res.stdout.decode("utf-8")

            fields = {"name": "Output", "value": f"```\n{stdout}```"}
            embed = self.bot.embed(ctx, fields=fields)
            await (ctx << embed)

    @commands.command()
    async def restart(self, ctx: utils.Context):
        """Restarts the bot."""

        await (ctx << "\U0001f97a Bye Bye")
        await self.bot.close()

    @commands.command(aliases=["sh"])
    async def shell(self, ctx: utils.Context, *args):
        """Runs given arguments into shell."""

        async with ctx.typing():
            func = functools.partial(subprocess.run, args, capture_output=True)
            res = await self.bot.loop.run_in_executor(None, func)
            stdout = res.stdout.decode("utf-8")

            syntax = args[-1].split(".")[-1] if args[0] == "cat" else ""

            content = f"```{syntax}\n{stdout}```"
            await (ctx << content)

    @commands.command(name="eval")
    async def _eval(self, ctx: utils.Context, *, code: utils.get_code):
        """Evaluates python code."""

        env = {
            "ctx": ctx,
            "codeblock": lambda c, l: f"```{l}\n{c}```"
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
