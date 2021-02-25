#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import aiohttp
import discord
import config
import utils
import time


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

    async def get_context(self, message: discord.Message, *, cls: utils.Context = None):
        return await super().get_context(message, cls=cls or utils.Context)

    async def mystbin(self, data: str):
        data = bytes(data, 'utf-8')
        async with self.session.post('https://mystb.in/documents', data=data) as r:
            res = await r.json()
            key = res["key"]
            return f"https://mystb.in/{key}"

    def embed(self, ctx: commands.Context = None, **kwargs):
        kwargs.setdefault("colour", discord.Colour.red())
        fields = kwargs.pop("fields", [])
        embed = discord.Embed(**kwargs)

        if fields:
            if isinstance(fields, dict):
                fields = [fields,]

            for field in fields:
                embed.add_field(**field)

        embed.set_footer(
            text=f"Requested by {ctx.author}" if ctx else discord.Embed.Empty,
            icon_url=str(ctx.author.avatar_url) if ctx else discord.Embed.Empty
        )
        return embed

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))

    async def close(self):
        await self.session.close()
        await super().close()

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        ignored = (commands.CommandNotFound, commands.NotOwner)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(ctx.command)

        await (ctx << f"{type(error).__name__} - {error}")
        raise error


bot = Bot(allowed_mentions=discord.AllowedMentions.none())


@bot.command()
async def ping(ctx: commands.Context):
    """Basic ping command."""

    s = time.perf_counter()
    message = await (ctx << "Pong.")
    f = round((time.perf_counter() - s) * 1000, 2)
    await message.edit(content=f"{f} ms.")


@bot.command(aliases=["src", "git"])
async def source(ctx: commands.Context):
    """Sends the bots source code."""

    await (ctx << "<https://github.com/kal-byte/bottom-bot>")


bot.run(config.token)
