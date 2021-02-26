# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import utils
import re


mystbin_url = re.compile(
    r"(?:(?:https?://)?mystb\.in/)?(?P<ID>[a-zA-Z]+)(?:\.(?P<syntax>[a-zA-Z0-9]+))?"
) # Thanks to Umbra's mystbin wrapper repo for this.


class Bottom(commands.Cog):
    """The two actual commands that make this bot, lol."""

    def __init__(self, bot):
        self.bot = bot

    async def bottomify(self, txt: str):
        """Helper method to reduce repetition."""

        if match := mystbin_url.match(txt):
            paste_id = match.group("ID")
            try:
                async with self.bot.session.get(f"https://mystb.in/api/pastes/{paste_id}") as resp:
                    if resp.status != 200:
                        return utils.to_bottom(txt)
                    data = await resp.json()
                    return utils.to_bottom(data["data"])
            except:
                return utils.to_bottom(txt)
        return utils.to_bottom(txt)

    async def unbottomify(self, txt: str):
        """Helper method to reduce repetition."""

        if match := mystbin_url.match(txt):
            paste_id = match.group("ID")
            try:
                async with self.bot.session.get(f"https://mystb.in/api/pastes/{paste_id}") as resp:
                    if resp.status != 200:
                        return utils.from_bottom(txt)
                    data = await resp.json()
                    return utils.from_bottom(data["data"])
            except:
                return utils.to_bottom(txt)
        return utils.from_bottom(txt)

    @commands.command()
    async def encode(self, ctx: commands.Context, *, text: str):
        """Encodes given text into bottom language."""

        encoded = await self.bottomify(text)

        if len(encoded) > 750:
            encoded = await self.bot.mystbin(encoded)

        content = f"```py\n{encoded}```"
        await ctx.send(content)

    @commands.command()
    async def decode(self, ctx: commands.Context, *, text: str):
        """Decodes bottom language into normal text."""

        try:
            decoded = await self.unbottomify(text)
        except TypeError:
            return await (ctx << "This bottom text doesn't seem right.")

        if len(decoded) > 750:
            decoded = await self.bot.mystbin(decoded)

        content = f"```py\n{decoded}```"
        await ctx.send(content)


def setup(bot):
    bot.add_cog(Bottom(bot))
