from discord.ext import commands

import database

TIER_ORDER = [
    "IRON",
    "BRONZE",
    "SILVER",
    "GOLD",
    "PLATINUM",
    "EMERALD",
    "DIAMOND",
    "MASTER",
    "GRANDMASTER",
    "CHALLENGER",
]

RANK_ORDER = ["IV", "III", "II", "I"]


def _rank_sorter(player_rank):
    """Helper function to return tuple of ranked values for sorting on leaderboard"""
    tier, rank, league_points = player_rank[2:]
    if tier is None:
        return -1, -1, -1
    tier = TIER_ORDER.index(tier)
    rank = RANK_ORDER.index(rank)
    return tier, rank, league_points


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(usage="pass")
    async def leaderboard(self, ctx):
        leaderboard_players = await database.get_leaderboard_players(ctx.guild.id)
        leaderboard_players_sorted = sorted(
            leaderboard_players, key=_rank_sorter, reverse=True
        )
        await ctx.send(leaderboard_players_sorted)

    @leaderboard.command(usage="<name#tag>")
    async def add(self, ctx, *, message: str):
        try:
            game_name, tag_line = message.split("#")
        except ValueError:
            await ctx.send(
                f"{ctx.message.content} is not a valid format. Use !leaderboard add name#tag"
            )
            return
        player = await database.get_player(game_name, tag_line)
        if player is None:
            await ctx.send(
                f"{game_name}#{tag_line} was not found. Use !rank to add a player to the database"
            )
            return
        puuid, game_name, tag_line = player
        result = await database.insert_leaderboard_player(puuid, ctx.guild.id)
        if result > 0:
            await ctx.send(f"{game_name}#{tag_line} was added to the !leaderboard")
            return
        await ctx.send(f"{game_name}#{tag_line} is already on the !leaderboard")


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
