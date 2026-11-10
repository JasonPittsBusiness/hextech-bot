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


async def add_player(puuid, game_name, game_tag, discord_id):
    data = (puuid, game_name, game_tag, discord_id)
    async with aiosqlite.connect("hextech.db") as db:
        await db.execute(
            "INSERT INTO players VALUES(?, ?, ?, ?) ON CONFLICT(puuid) DO UPDATE SET game_name = excluded.game_name, game_tag = excluded.game_tag",
            data,
        )
        await db.commit()


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(add_player("your_puuid", "your_game_name", "your_game_tag", 1234))
