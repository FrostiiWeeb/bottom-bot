#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import aiohttp
import asyncio
import discord
import config
import time
import os


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"


prefixes = ["\U0001f97a ", "\U0000005c\U0001f97a ", "\U0001f97a", "\U0000005c\U0001f97a"]


async def get_prefix(bot: commands.Bot, message: discord.Message):
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        kwargs.setdefault("help_command", commands.MinimalHelpCommand())
        super().__init__(get_prefix, **kwargs)

        self.session: aiohttp.ClientSession

        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print('Could not load extension {0} due to {1.__class__.__name__}: {1}'.format(cog, exc))

        self.loop.create_task(self.after_on_ready())

    async def after_on_ready(self):
        """This is here just to stop aiohttp from complaining about deprecation."""

        await self.wait_until_ready()

        self.session = aiohttp.ClientSession()

    async def mystbin(self, data: str):
        data = bytes(data, 'utf-8')
        async with self.session.post('https://mystb.in/documents', data=data) as r:
            res = await r.json()
            key = res["key"]
            return f"https://mystb.in/{key}"

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        ignored = (commands.CommandNotFound, commands.NotOwner)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(ctx.command)

        await ctx.send(f"{type(error).__name__} - {error}")
        raise error


bot = Bot(allowed_mentions=discord.AllowedMentions.none())


@bot.command()
async def ping(ctx: commands.Context):
    """Basic ping command."""

    s = time.perf_counter()
    message = await ctx.send("Pong.")
    f = round((time.perf_counter() - s) * 1000, 2)
    await message.edit(content=f"{f} ms.")


bot.run(config.token)
