from discord.ext import commands

import riot_api


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def rank(self, ctx, *, message: str):
        game_name, game_tag = message.split("#")
        account = await riot_api.get_puuid(game_name, game_tag)
        rank_data = await riot_api.get_rank_data(account["puuid"])
        for rank in rank_data:
            if rank["queueType"] == "RANKED_SOLO_5x5":
                await ctx.send(
                    f"{message} is currently {rank['tier']} {rank['rank']} {rank['leaguePoints']} LP"
                )


async def setup(bot):
    await bot.add_cog(Rank(bot))
