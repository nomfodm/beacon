from slowapi import Limiter
from slowapi.util import get_remote_address

from infrastructure.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.db}",
)
