from discord.ext import commands


class Context(commands.Context):

    def __truediv__(self, content: str = None):
        return self.bot.loop.create_task(self.send(content))

    def __lshift__(self, content: str = None):
        return self.__truediv__(content)

    def __repr__(self):
        return "<NoOneCares at 0xShutUp"