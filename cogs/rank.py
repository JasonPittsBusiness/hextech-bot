import discord
from discord.ext import commands

import database
import riot_api


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(usage="<name#tag> [queue]")
    async def rank(self, ctx, *, message: str):
        """Returns the rank of a player in a specified queue.
        Use the format !rank \"name#tag\" solo, flex, premade, or 5s"""
        try:
            game_name, tag_line = message.split("#")
            tag_parts = tag_line.split()
            queue = "solo"
            if len(tag_parts) > 1:
                tag_line, queue = tag_parts
            queue_type = riot_api.RIOT_QUEUES[queue]
        except (ValueError, KeyError):
            await ctx.send(
                f"'{message}' is not a valid format. Use !rank \"name#tag\" solo, flex, premade, or 5s"
            )
            return
        # TODO handle case sensistivity
        player = await database.get_player(game_name, tag_line)
        if player is None:
            account = await riot_api.get_puuid(game_name, tag_line)
            puuid = account["puuid"]
            game_name = account["gameName"]
            tag_line = account["tagLine"]
            if account is not None:
                await database.upsert_player(
                    account["puuid"],
                    account["gameName"],
                    account["tagLine"],
                )
            if account is None:
                await ctx.send(
                    f"'{message}' not found. Check the name or try again later."
                )
                return
        else:
            puuid, game_name, tag_line = player
        rank_data = await database.get_rank(puuid, queue_type)
        if rank_data is None:
            rank_data = await riot_api.get_rank_data(puuid)
            for rank in rank_data:
                old_rank_data = await database.get_rank(
                    puuid, rank["queueType"], stale_check=False
                )
                await database.upsert_rank(
                    puuid,
                    rank["queueType"],
                    rank["tier"],
                    rank["rank"],
                    rank["leaguePoints"],
                )
                new_rank_data = await database.get_rank(puuid, rank["queueType"])
                if new_rank_data != old_rank_data:
                    await database.insert_rank_history(
                        puuid, rank["queueType"], *new_rank_data
                    )
        rank_data = await database.get_rank(puuid, queue_type)
        if rank_data is None:
            await ctx.send(f"{message} is currently unranked in {queue}")
            return
        tier, rank, leaguepoints = rank_data
        await ctx.send(
            f"{game_name}#{tag_line} is currently {tier} {rank} {leaguepoints} LP in {queue}"
        )

    @commands.hybrid_command(usage="<discord_user> <name#tag>")
    async def claim(self, ctx, mention: discord.Member, *, message: str):
        """Claim an account that has already checked with !rank
        !claim @discord_mention name#tag"""
        try:
            game_name, tag_line = message.split("#")
        except ValueError:
            await ctx.send(
                f"'{message}' is not a valid format. Please use !claim @discord_mention name#tag"
            )
            return
        player = await database.get_player(game_name, tag_line)
        if player is None:
            await ctx.send(
                f"'{message}' not found. Check the name or try !rank to add the user to the database first"
            )
            return
        puuid, game_name, tag_line = player
        await ctx.send(
            f"The League account {game_name}#{tag_line} was claimed by {mention.mention}"
        )
        await database.update_player_discord_owner(puuid, mention.id)

    @claim.error
    async def claim_error(self, ctx: commands.Context, error: commands.CommandError):
        """Gives the user an error message on CommandError"""
        await ctx.send(
            f"{ctx.message.content} is not a valid format. Please use !claim @discord_mention name#tag"
        )


async def setup(bot):
    await bot.add_cog(Rank(bot))
