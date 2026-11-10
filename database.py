import asyncio

import aiosqlite


async def init_db():
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS players(
            puuid TEXT PRIMARY KEY, 
            game_name TEXT, 
            game_tag TEXT, 
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


async def get_player(game_name, game_tag):
    async with aiosqlite.connect("hextech.db") as db:
        data = (game_name, game_tag)
        cursor = await db.execute(
            """SELECT puuid 
            FROM players 
            WHERE game_name = ? 
            AND game_tag = ?""",
            data,
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return row[0]


async def upsert_player(puuid, game_name, game_tag, discord_id):
    data = (puuid, game_name, game_tag, discord_id)
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            """INSERT INTO players 
            VALUES(?, ?, ?, ?) 
            ON CONFLICT(puuid) 
            DO UPDATE SET 
                game_name = excluded.game_name, 
                game_tag = excluded.game_tag""",
            data,
        )
        await db.commit()


async def get_rank(puuid, queue_type):
    async with aiosqlite.connect("hextech.db") as db:
        data = (puuid, queue_type)
        cursor = await db.execute(
            """SELECT tier, rank, league_points 
            FROM ranks 
            WHERE puuid = ? 
            AND queue_type = ? 
            AND updated_at > datetime('now', '-60 seconds')""",
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


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(upsert_player("your_puuid", "your_game_name", "your_game_tag", 1234))
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
    asyncio.run(get_player("your_game_name", "your_game_tag"))
    asyncio.run(get_rank("your_puuid", "RANKED_DUO_5X5"))
