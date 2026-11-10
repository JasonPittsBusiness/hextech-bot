import asyncio

import aiosqlite


async def init_db():
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS players(puuid TEXT PRIMARY KEY, game_name TEXT, game_tag TEXT, discord_id INTEGER)"
        )
        await db.execute(
            """CREATE TABLE IF NOT EXISTS rank(puuid TEXT, queue_type TEXT, tier TEXT, rank TEXT, 
            league_points INTEGER, updated_at TEXT DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(puuid, queue_type))"""
        )


if __name__ == "__main__":
    asyncio.run(init_db())
