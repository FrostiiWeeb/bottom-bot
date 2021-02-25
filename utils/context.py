from discord.ext import commands


class Context(commands.Context):

    def __truediv__(self, content: str = None):
        return self.bot.loop.create_task(self.send(content))