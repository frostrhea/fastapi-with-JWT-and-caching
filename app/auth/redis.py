from redis import asyncio as aioredis
from fastapi import FastAPI

redis = aioredis.from_url("redis://localhost", decode_responses=True)


async def add_to_blacklist(refresh_token: str, expiration: int):
    # Add a refresh token to the Redis blacklist.
    await redis.setex(f"blacklist_{refresh_token}", expiration, refresh_token)

async def is_token_blacklisted(refresh_token: str) -> bool:
    # Check if a refresh token is in the blacklist.
    return await redis.exists(f"blacklist_{refresh_token}")
