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

TIER_WIDTH = len(max(TIER_ORDER, key=len))

RANK_WIDTH = len(max(RANK_ORDER, key=len))

LP_WIDTH = 4


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
        name_width = 0
        place_width = len(str(len(leaderboard_players_sorted)))
        for player in leaderboard_players_sorted:
            player_name_len = len(player[0]) + 1 + len(player[1])
            name_width = max(name_width, player_name_len)
        player_list = []
        for place, player in enumerate(leaderboard_players_sorted, start=1):
            player_name = f"{player[0]}#{player[1]}"
            if player[2] is None:
                player_name_padded = (
                    f"{place:>{place_width}}. {player_name:<{name_width}} Unranked"
                )
                player_list.append(player_name_padded)
                continue
            player_name_padded = f"{place:>{place_width}}. {player_name:<{name_width}} {player[2]:<{TIER_WIDTH}} {player[3]:<{RANK_WIDTH}} {player[4]:>{LP_WIDTH}} LP"
            player_list.append(player_name_padded)
        header_width = len(max(player_list, key=len))
        leaderboard_title = "Ranked Leaderboard"
        leaderboard_content = "\n".join(player_list)
        await ctx.send(
            f"```\n{leaderboard_title:^{header_width}}\n{leaderboard_content}\n```"
        )

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
