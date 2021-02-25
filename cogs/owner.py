# -*- coding: utf-8 -*-

from contextlib import redirect_stdout
from discord.ext import commands
import subprocess
import functools
import textwrap
import discord
import utils
import io

def git_pull():
    return subprocess.run(["git", "pull"], capture_output=True)

class Owner(commands.Cog):
    """Commands for development."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def pull(self, ctx: commands.Context):
        """Pulls the latest code from the repo."""

        func = functools.partial(git_pull)
        res = await self.bot.loop.run_in_executor(None, func)
        stdout = res.stdout.decode("utf-8")

        embed = discord.Embed()
        embed.description = f"```\n{stdout}```"
        await ctx.send(embed=embed)

    @commands.command()
    async def restart(self, ctx: commands.Context):
        """Restarts the bot."""

        await self.bot.close()

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(ctx: commands.Context, *, code: utils.get_code):
        """Evaluates python code."""

        env = {
            "ctx": ctx
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
            return await ctx.send(value)

        out.close()

        if isinstance(res, discord.Embed):
            return await ctx.send(embed=res)

        elif isinstance(res, (str, int)):
            return await ctx.send(res)

        else:
            return await ctx.send(repr(res))


def setup(bot):
    bot.add_cog(Owner(bot))
