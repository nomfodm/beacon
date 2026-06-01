from typing import Annotated

from fastapi import Depends
from redis import Redis

from application.services.auth import AuthService
from application.services.minecraft_profile import MinecraftProfileService
from application.use_cases.auth.login import LoginUseCase
from application.use_cases.auth.logout import LogoutUseCase
from application.use_cases.auth.logout_from_others import LogoutFromOthersUseCase
from application.use_cases.auth.refresh_session import RefreshSessionUseCase
from application.use_cases.launcher.add_release_asset import AddReleaseAssetUseCase
from application.use_cases.launcher.check_update import CheckUpdateUseCase
from application.use_cases.launcher.get_latest_platform_release import GetLatestPlatformReleaseUseCase
from application.use_cases.launcher.minecraft_session.create_minecraft_session import CreateMinecraftSessionUseCase
from application.use_cases.launcher.minecraft_session.has_joined_server import HasJoinedServerUseCase
from application.use_cases.launcher.minecraft_session.join_server import JoinServerUseCase
from application.use_cases.launcher.minecraft_session.profile import ProfileUseCase
from application.use_cases.launcher.publish_release import PublishReleaseUseCase
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork
from infrastructure.redis.refresh_idempotency_repo import RedisRefreshIdempotencyRepository
from presentation.dependencies.db import get_redis_client
from presentation.dependencies.services import get_auth_service, get_minecraft_profile_service, get_string_hasher
from presentation.dependencies.uow import get_uow

UOW = Annotated[UnitOfWork, Depends(get_uow)]
AUTH_SERVICE = Annotated[AuthService, Depends(get_auth_service)]
STRING_HASHER = Annotated[StringHasher, Depends(get_string_hasher)]
MC_PROFILE_SERVICE = Annotated[MinecraftProfileService, Depends(get_minecraft_profile_service)]


def get_check_update_uc(uow: UOW) -> CheckUpdateUseCase:
    return CheckUpdateUseCase(uow=uow)


def get_latest_platform_release_uc(uow: UOW) -> GetLatestPlatformReleaseUseCase:
    return GetLatestPlatformReleaseUseCase(uow=uow)


def get_create_mc_session_uc(uow: UOW) -> CreateMinecraftSessionUseCase:
    return CreateMinecraftSessionUseCase(uow=uow)


def get_join_server_uc(uow: UOW) -> JoinServerUseCase:
    return JoinServerUseCase(uow=uow)


def get_has_joined_uc(uow: UOW, mc_profile_service: MC_PROFILE_SERVICE) -> HasJoinedServerUseCase:
    return HasJoinedServerUseCase(uow=uow, mc_profile_service=mc_profile_service)


def get_profile_uc(uow: UOW, mc_profile_service: MC_PROFILE_SERVICE) -> ProfileUseCase:
    return ProfileUseCase(uow=uow, mc_profile_service=mc_profile_service)


def get_publish_release_uc(uow: UOW) -> PublishReleaseUseCase:
    return PublishReleaseUseCase(uow=uow)


def get_add_release_asset_uc(uow: UOW) -> AddReleaseAssetUseCase:
    return AddReleaseAssetUseCase(uow=uow)


def get_login_uc(uow: UOW, auth_service: AUTH_SERVICE, string_hasher: STRING_HASHER) -> LoginUseCase:
    return LoginUseCase(uow=uow, auth_service=auth_service, hasher=string_hasher)


def get_logout_uc(uow: UOW, auth_service: AUTH_SERVICE) -> LogoutUseCase:
    return LogoutUseCase(uow=uow, auth_service=auth_service)


def get_logout_from_others_uc(
    uow: UOW,
    auth_service: AUTH_SERVICE,
    string_hasher: STRING_HASHER,
) -> LogoutFromOthersUseCase:
    return LogoutFromOthersUseCase(uow=uow, auth_service=auth_service, hasher=string_hasher)


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
