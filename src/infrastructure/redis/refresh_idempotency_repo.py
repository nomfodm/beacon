from redis.asyncio import Redis


class RedisRefreshIdempotencyRepository:
    _PREFIX = "refresh_idempotency"

    def __init__(self, client: Redis) -> None:
        self._client = client

    def _key(self, token: str) -> str:
        return f"{self._PREFIX}:{token}"

    async def get(self, *, token: str) -> str | None:
        return await self._client.get(self._key(token))

    async def save(self, *, token: str, payload: str, ttl: int) -> None:
        await self._client.setex(self._key(token), ttl, payload)
