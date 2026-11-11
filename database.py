import asyncio

import aiosqlite


async def init_db():
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS players(
            puuid TEXT PRIMARY KEY, 
            game_name TEXT COLLATE NOCASE, 
            tag_line TEXT COLLATE NOCASE, 
            discord_id INTEGER
            )"""
        )
        await db.execute(
            """CREATE TABLE IF NOT EXISTS ranks(
            puuid TEXT, 
            queue_type TEXT, 
            tier TEXT, 
            rank TEXT, 
            league_points INTEGER, 
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(puuid, queue_type)
            )"""
        )
        await db.execute(
            """CREATE TABLE IF NOT EXISTS rank_history(
            puuid TEXT, 
            queue_type TEXT, 
            tier TEXT, 
            rank TEXT, 
            league_points INTEGER, 
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(puuid, queue_type, updated_at)
            )"""
        )
        await db.execute(
            """CREATE TABLE IF NOT EXISTS leaderboard_players(
            puuid TEXT, 
            guild_id INTEGER,
            PRIMARY KEY(puuid, guild_id)
            )"""
        )


async def get_player(game_name, tag_line):
    async with aiosqlite.connect("hextech.db") as db:
        data = (game_name, tag_line)
        cursor = await db.execute(
            """SELECT puuid, game_name, tag_line 
            FROM players 
            WHERE game_name = ? 
            AND tag_line = ?""",
            data,
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return row


async def upsert_player(puuid, game_name, tag_line):
    data = (puuid, game_name, tag_line)
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            """INSERT INTO players (puuid, game_name, tag_line)
            VALUES(?, ?, ?) 
            ON CONFLICT(puuid) 
            DO UPDATE SET 
                game_name = excluded.game_name, 
                tag_line = excluded.tag_line""",
            data,
        )
        await db.commit()


async def update_player_discord_owner(puuid, discord_id):
    data = (discord_id, puuid)
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            """UPDATE players 
            SET discord_id = ? 
            WHERE puuid = ? 
            """,
            data,
        )
        await db.commit()


async def get_rank(puuid, queue_type, stale_check=True):
    async with aiosqlite.connect("hextech.db") as db:
        data = (puuid, queue_type)
        query = """SELECT tier, rank, league_points 
                    FROM ranks 
                    WHERE puuid = ? 
                    AND queue_type = ?"""
        if stale_check:
            query += " AND updated_at > datetime('now', '-60 seconds')"
        cursor = await db.execute(
            query,
            data,
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return row


async def upsert_rank(puuid, queue_type, tier, rank, league_points):
    data = (puuid, queue_type, tier, rank, league_points)
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            """INSERT INTO ranks (puuid, queue_type, tier, rank, league_points) 
            VALUES(?, ?, ?, ?, ?) 
            ON CONFLICT(puuid, queue_type) 
            DO UPDATE SET tier = 
                excluded.tier, 
                rank = excluded.rank, 
                league_points = excluded.league_points, 
                updated_at = CURRENT_TIMESTAMP""",
            data,
        )
        await db.commit()


async def insert_rank_history(puuid, queue_type, tier, rank, league_points):
    data = (puuid, queue_type, tier, rank, league_points)
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            """INSERT INTO rank_history (puuid, queue_type, tier, rank, league_points) 
            VALUES(?, ?, ?, ?, ?)""",
            data,
        )
        await db.commit()


async def get_leaderboard_players(guild_id):
    data = (guild_id,)
    async with aiosqlite.connect("hextech.db") as db:
        cursor = await db.execute(
            """
        SELECT game_name, tag_line, tier, rank, league_points
        FROM leaderboard_players
        LEFT OUTER JOIN ranks
        ON leaderboard_players.puuid = ranks.puuid
        AND ranks.queue_type = 'RANKED_SOLO_5x5'
        JOIN players
        ON leaderboard_players.puuid = players.puuid
        WHERE guild_id = ?""",
            data,
        )
        return await cursor.fetchall()


async def insert_leaderboard_player(puuid, guild_id):
    data = (puuid, guild_id)
    async with aiosqlite.connect("hextech.db") as db:
        cursor = await db.execute(
            """INSERT INTO leaderboard_players (puuid, guild_id)
            VALUES (?, ?)
            ON CONFLICT(puuid, guild_id)
            DO NOTHING
            """,
            data,
        )
        await db.commit()
        return cursor.rowcount


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(upsert_player("your_puuid", "your_game_name", "your_tag_line"))
    asyncio.run(
        upsert_rank(
            "your_puuid",
            "RANKED_DUO_5X5",
            "your_tier",
            "your_rank",
            75,
        )
    )
    asyncio.run(
        insert_rank_history(
            "your_puuid",
            "RANKED_DUO_5X5",
            "your_last_tier",
            "your_last_rank",
            68,
        )
    )
    asyncio.run(get_player("your_game_name", "your_tag_line"))
    asyncio.run(get_rank("your_puuid", "RANKED_DUO_5X5"))
