from discord.ext import commands

import database
import riot_api


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def rank(self, ctx, *, message: str):
        try:
            game_name, game_tag = message.split("#")
        except ValueError:
            await ctx.send(
                f"'{message}' is not a valid format. Please use !rank name#tag"
            )
            return
        puuid = await database.get_player(game_name, game_tag)
        if puuid is None:
            account = await riot_api.get_puuid(game_name, game_tag)
            if account is not None:
                puuid = account["puuid"]
            if account is None:
                await ctx.send(
                    f"'{message}' not found. Check the name or try again later."
                )
                return
        await database.upsert_player(puuid, game_name, game_tag, ctx.author.id)
        rank_data = await riot_api.get_rank_data(puuid)
        for rank in rank_data:
            await database.upsert_rank(
                puuid,
                rank["queueType"],
                rank["tier"],
                rank["rank"],
                rank["leaguePoints"],
            )
            if rank["queueType"] == "RANKED_SOLO_5x5":
                await ctx.send(
                    f"{message} is currently {rank['tier']} {rank['rank']} {rank['leaguePoints']} LP"
                )
                return
        await ctx.send(f"{message} is currently unranked")


async def setup(bot):
    await bot.add_cog(Rank(bot))
