from discord.ext import commands


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def rank(self, ctx, *, message: str):
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Rank(bot))
