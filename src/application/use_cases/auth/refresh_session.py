import dataclasses
import json

from application.constants import REFRESH_IDEMPOTENCY_TTL_SECONDS
from application.dtos.auth import SessionCredentials, TokenPairResponse
from application.services.auth import AuthService
from domain.interfaces.repositories.refresh_idempotency_repo import RefreshIdempotencyRepository
from domain.interfaces.unit_of_work import UnitOfWork


class RefreshSessionUseCase:
    def __init__(self, *, uow: UnitOfWork, auth_service: AuthService, idempotency_cache: RefreshIdempotencyRepository):
        self._uow = uow
        self._auth_service = auth_service
        self._idempotency_cache = idempotency_cache

    async def execute(self, *, dto: SessionCredentials) -> TokenPairResponse:
        cached = await self._idempotency_cache.get(token=dto.refresh_token)
        if cached is not None:
            return TokenPairResponse(**json.loads(cached))

        async with self._uow:
            session = await self._uow.sessions.get_by_id_or_raise(uuid=dto.id)
            self._auth_service.verify_session(refresh_token=dto.refresh_token, session=session)

            access_token = self._auth_service.generate_access_token(user_id=session.user_id)
            refresh_token, refresh_token_expires_at, refresh_token_hash = self._auth_service.generate_refresh_token()

            session.expires_at = refresh_token_expires_at
            session.refresh_token_hash = refresh_token_hash

            await self._uow.sessions.save(session=session)
            await self._uow.commit()

            result = TokenPairResponse(access_token=access_token, refresh_split_token=f"{session.id}.{refresh_token}")

        await self._idempotency_cache.save(
            token=dto.refresh_token,
            payload=json.dumps(dataclasses.asdict(result)),
            ttl=REFRESH_IDEMPOTENCY_TTL_SECONDS,
        )
        return result
