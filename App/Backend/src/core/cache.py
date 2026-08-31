import os

from dotenv import load_dotenv
from redis import Redis

load_dotenv()

VALKEY_HOST = os.getenv("VALKEY_HOST")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", "6379"))
VALKEY_USERNAME = os.getenv("VALKEY_USERNAME", "default")
VALKEY_PASSWORD = os.getenv("VALKEY_PASSWORD")
VALKEY_SSL = os.getenv("VALKEY_SSL", "true").lower() == "true"

CACHE_TTL = int(os.getenv("VALKEY_CACHE_TTL", "600"))


redis_client = Redis(
    host=VALKEY_HOST,
    port=VALKEY_PORT,
    username=VALKEY_USERNAME,
    password=VALKEY_PASSWORD,
    ssl=VALKEY_SSL,
    decode_responses=True,
)


def check_cache_connection() -> bool:
    try:
        return redis_client.ping()
    except Exception as e:
        print(f"Valkey connection failed: {e}")
        return False