from discord.ext import commands


class Context(commands.Context):

    def __truediv__(self, content: str = None):
        return self.bot.loop.run_until_complete(self.send(content))

    def __repr__(self):
        return "<NoOneCares at 0xShutUp"