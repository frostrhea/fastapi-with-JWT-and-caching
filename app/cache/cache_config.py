import os
from dotenv import load_dotenv
from aiocache import Cache

load_dotenv()

ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"

cache = Cache(
    Cache.REDIS,
    endpoint=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    namespace="fastapi-cache",
    timeout=5,
    db=int(os.getenv("REDIS_DB", 0)),
)
