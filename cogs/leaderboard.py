import datetime
import logging
from zoneinfo import ZoneInfo

from discord.ext import commands, tasks

import database
import riot_api
import utils
from cogs import rank

logger = logging.getLogger(__name__)

CENTRAL_TZ = ZoneInfo("America/Chicago")
POST_TIME = [
    datetime.time(hour=11, tzinfo=CENTRAL_TZ),
    datetime.time(hour=23, tzinfo=CENTRAL_TZ),
]

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

LP_PER_TIER = 400

LP_PER_RANK = 100

CALENDAR = {"1 day": 24, "7 days": 168, "30 days": 720, "all time": 1000000}


def _rank_sorter(player_rank):
    """Helper function to return tuple of ranked values for sorting on leaderboard"""
    tier, rank, league_points = player_rank[2:5]
    if tier is None:
        return -1, -1, -1
    tier = TIER_ORDER.index(tier)
    rank = RANK_ORDER.index(rank)
    return tier, rank, league_points


def _get_rank_value(tier, rank, LP):
    """Returns the total LP value of a rank for change in rank calculations"""
    tier_value = TIER_ORDER.index(tier) * LP_PER_TIER
    if tier in ("MASTER", "GRANDMASTER", "CHALLENGER"):
        tier_value = TIER_ORDER.index("MASTER") * LP_PER_TIER
        return tier_value + LP
    rank_value = RANK_ORDER.index(rank) * LP_PER_RANK
    return tier_value + rank_value + LP


async def _build_leaderboard(guild_id):
    """Builds a leaderboard from a given guild_id"""
    leaderboard_players = await database.get_leaderboard_players(guild_id)
    if not leaderboard_players:
        return "No players have been added to the !leaderboard for this server"
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
        queue_type = riot_api.RIOT_QUEUES["solo"]
        for c in CALENDAR:
            changes_in_rank = []
            previous_rank_value = await database.get_rank_history(
                player[5], queue_type, CALENDAR[c]
            )
            if previous_rank_value is None:
                player_change_in_rank = 0
            else:
                tier, rank, lp = previous_rank_value
                player_prev_rank_value = _get_rank_value(tier, rank, lp)
                player_current_rank_value = _get_rank_value(
                    player[2], player[3], player[4]
                )
                player_change_in_rank = (
                    player_current_rank_value - player_prev_rank_value
                )
            player_name_padded += f" {player_change_in_rank:>+{len(c)}}"
        changes_in_rank.append(player_change_in_rank)
        player_list.append(player_name_padded)
    leaderboard_title = "Ranked Leaderboard"
    leaderboard_content = "\n".join(player_list)
    header_width = len(
        f"{'':{place_width + 1}} {'':{name_width}} {'':{TIER_WIDTH}} {'':{RANK_WIDTH}} {'':{LP_WIDTH}} LP"
    )
    # TODO loop to create header
    header = f"```\n{leaderboard_title:<{header_width}} {'1 day':>{len('1 day')}} {'7 days':>{len('7 days')}} {'30 days':>{len('30 days')}} {'all time':>{len('all time')}}\n{leaderboard_content}\n```"
    return header


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_leaderboard.start()
        self.update_leaderboard.start()

    def cog_unload(self):
        self.daily_leaderboard.cancel()
        self.update_leaderboard.cancel()

    @commands.hybrid_group()
    async def leaderboard(self, ctx):
        """Posts the ranked solo leaderboard for this server"""
        leaderboard_content = await _build_leaderboard(ctx.guild.id)
        await ctx.send(leaderboard_content)

    @leaderboard.command(usage="<name#tag>")
    async def add(self, ctx, *, message: str):
        """Add a player to the leaderboard in this server"""
        try:
            game_name, tag_line, _ = utils.parse_riot_id(message)
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

    @leaderboard.command()
    async def subscribe(self, ctx):
        """Subscribe the current channel to the daily leadboard"""
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        result = await database.insert_subscribed_channel(guild_id, channel_id)
        if result > 0:
            await ctx.send(
                f"{ctx.channel.mention} has been subscribed to the daily !leaderboard"
            )
            return
        await ctx.send(
            f"{ctx.channel.mention} is already subscribed to the daily !leaderboard"
        )

    @tasks.loop(time=POST_TIME)
    async def daily_leaderboard(self):
        await self.update_leaderboard()
        subscribed_channels = await database.get_suscribed_channels()
        for guild in subscribed_channels:
            try:
                leaderboard_content = await _build_leaderboard(guild[0])
                channel = self.bot.get_channel(guild[1])
                await channel.send(leaderboard_content)
            except Exception:
                logger.exception("Subscribed channel is not valid")

    @tasks.loop(minutes=20)
    async def update_leaderboard(self):
        update_players = await database.get_distinct_leaderboard_players()
        for update in update_players:
            (puuid,) = update
            await rank.update_ranks(puuid)
        logger.info(f"Updated {len(update_players)} leaderboard players")

    @daily_leaderboard.before_loop
    async def before_daily_leaderboard(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
