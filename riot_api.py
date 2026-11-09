import asyncio
import os

import aiohttp
from dotenv import load_dotenv

AMERICAS_BASE_URL = "https://americas.api.riotgames.com"
NA1_BASE_URL = "https://na1.api.riotgames.com"


async def get_puuid(game_name, tag_line):
    riot_api_key = os.getenv("RIOT_API_KEY")

    headers = {"X-Riot-Token": riot_api_key}
    async with (
        aiohttp.ClientSession(headers=headers) as session,
        session.get(
            f"{AMERICAS_BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        ) as resp,
    ):
        if resp.status != 200:
            return None
        account = await resp.json()
        return account


async def get_rank_data(puuid):
    riot_api_key = os.getenv("RIOT_API_KEY")

    headers = {"X-Riot-Token": riot_api_key}
    async with (
        aiohttp.ClientSession(headers=headers) as session,
        session.get(f"{NA1_BASE_URL}/lol/league/v4/entries/by-puuid/{puuid}") as resp,
    ):
        rank_data = await resp.json()
        return rank_data


async def main():
    load_dotenv()
    account = await get_puuid("FlSHlE", "memes")
    rank_data = await get_rank_data(account["puuid"])
    return rank_data


if __name__ == "__main__":
    asyncio.run(main())
