from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends
from redis.asyncio import Redis

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from application.use_cases.auth.get_sessions import GetSessionsUseCase
from application.use_cases.auth.login import LoginUseCase
from application.use_cases.auth.logout import LogoutUseCase
from application.use_cases.auth.logout_from_others import LogoutFromOthersUseCase
from application.use_cases.auth.refresh_session import RefreshSessionUseCase
from application.use_cases.auth.register_user_and_login import RegisterUserAndLoginUseCase
from application.use_cases.auth.reset_password import ResetPasswordUseCase
from application.use_cases.auth.revoke_session import RevokeSessionUseCase
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork
from infrastructure.redis.refresh_idempotency_repo import RedisRefreshIdempotencyRepository
from presentation.dependencies.db import get_redis_client
from presentation.dependencies.services import get_auth_service, get_string_hasher
from presentation.dependencies.uow import get_uow

UOW = Annotated[UnitOfWork, Depends(get_uow)]
AUTH_SERVICE = Annotated[AuthService, Depends(get_auth_service)]
STRING_HASHER = Annotated[StringHasher, Depends(get_string_hasher)]


def get_session_credentials(refresh_token: str = Cookie(...)) -> SessionCredentials:
    session_id, token = refresh_token.split(".", 1)
    return SessionCredentials(id=UUID(session_id), refresh_token=token)


SESSION_CREDENTIALS = Annotated[SessionCredentials, Depends(get_session_credentials)]


def get_login_uc(uow: UOW, auth_service: AUTH_SERVICE, string_hasher: STRING_HASHER) -> LoginUseCase:
    return LoginUseCase(uow=uow, auth_service=auth_service, hasher=string_hasher)


def get_register_user_and_login_uc(
    uow: UOW,
    auth_service: AUTH_SERVICE,
    string_hasher: STRING_HASHER,
) -> RegisterUserAndLoginUseCase:
    return RegisterUserAndLoginUseCase(uow=uow, auth_service=auth_service, hasher=string_hasher)


def get_logout_uc(uow: UOW, auth_service: AUTH_SERVICE) -> LogoutUseCase:
    return LogoutUseCase(uow=uow, auth_service=auth_service)


def get_logout_from_others_uc(
    uow: UOW,
    auth_service: AUTH_SERVICE,
    string_hasher: STRING_HASHER,
) -> LogoutFromOthersUseCase:
    return LogoutFromOthersUseCase(uow=uow, auth_service=auth_service, hasher=string_hasher)


def get_sessions_uc(uow: UOW, auth_service: AUTH_SERVICE) -> GetSessionsUseCase:
    return GetSessionsUseCase(uow=uow, auth_service=auth_service)


def get_refresh_session_uc(
    uow: UOW,
    auth_service: AUTH_SERVICE,
    redis: Annotated[Redis, Depends(get_redis_client)],
) -> RefreshSessionUseCase:
    return RefreshSessionUseCase(
        uow=uow,
        auth_service=auth_service,
        idempotency_cache=RedisRefreshIdempotencyRepository(redis),
    )


def get_revoke_session_uc(uow: UOW, auth_service: AUTH_SERVICE) -> RevokeSessionUseCase:
    return RevokeSessionUseCase(uow=uow, auth_service=auth_service)


def get_reset_password_uc(uow: UOW, string_hasher: STRING_HASHER) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(uow=uow, hasher=string_hasher)
