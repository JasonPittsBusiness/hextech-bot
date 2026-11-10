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
            tag_parts = game_tag.split()
            queue = "solo"
            if len(tag_parts) > 1:
                game_tag, queue = tag_parts
            queue_type = riot_api.RIOT_QUEUES[queue]
        except (ValueError, KeyError):
            await ctx.send(
                f"'{message}' is not a valid format. Please use !rank \"name#tag\" solo, flex, premade, or 5s"
            )
            return
        # TODO handle case sensistivity
        puuid = await database.get_player(game_name, game_tag)
        if puuid is None:
            account = await riot_api.get_puuid(game_name, game_tag)
            if account is not None:
                puuid = account["puuid"]
                await database.upsert_player(puuid, game_name, game_tag, ctx.author.id)
            if account is None:
                await ctx.send(
                    f"'{message}' not found. Check the name or try again later."
                )
                return
        rank_data = await database.get_rank(puuid, queue_type)
        if rank_data is None:
            rank_data = await riot_api.get_rank_data(puuid)
            for rank in rank_data:
                await database.upsert_rank(
                    puuid,
                    rank["queueType"],
                    rank["tier"],
                    rank["rank"],
                    rank["leaguePoints"],
                )
        rank_data = await database.get_rank(puuid, queue_type)
        if rank_data is None:
            await ctx.send(f"{message} is currently unranked in {queue}")
            return
        tier, rank, leaguepoints = rank_data
        await ctx.send(
            f"{message} is currently {tier} {rank} {leaguepoints} LP in {queue}"
        )


async def setup(bot):
    await bot.add_cog(Rank(bot))
