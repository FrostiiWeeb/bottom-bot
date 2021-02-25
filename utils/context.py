import discord
import typing as t
from discord.ext import commands


class Context(commands.Context):

    def __truediv__(self, content: t.Union[str, discord.Embed] = None):
        if isinstance(content, discord.Embed):
            return self.bot.loop.create_task(self.send(embed=content))

        if isinstance(content, discord.File):
            return self.bot.loop.create_task(self.send(file=file))

        return self.bot.loop.create_task(self.send(content))

    def __lshift__(self, content: str = None):
        return self.__truediv__(content)

    def __repr__(self):
        return "<NoOneCares at 0xShutUp>"