from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from application.dtos.auth import SessionCredentials
from application.dtos.launcher import CheckUpdateResponse, LauncherReleaseResponse
from application.dtos.minecraft_session import MinecraftSessionResponse, ProfileResponse
from application.use_cases.auth.login import LoginUseCase, UserLoginRequest
from application.use_cases.auth.logout import LogoutUseCase
from application.use_cases.auth.logout_from_others import LogoutFromOthersRequest, LogoutFromOthersUseCase
from application.use_cases.auth.refresh_session import RefreshSessionUseCase
from application.use_cases.launcher.add_release_asset import AddReleaseAssetRequest, AddReleaseAssetUseCase
from application.use_cases.launcher.check_update import CheckUpdateRequest, CheckUpdateUseCase
from application.use_cases.launcher.get_latest_platform_release import (
    GetLatestPlatformReleaseRequest,
    GetLatestPlatformReleaseUseCase,
)
from application.use_cases.launcher.minecraft_session.create_minecraft_session import CreateMinecraftSessionUseCase
from application.use_cases.launcher.minecraft_session.has_joined_server import HasJoinedRequest, HasJoinedServerUseCase
from application.use_cases.launcher.minecraft_session.join_server import JoinServerRequest, JoinServerUseCase
from application.use_cases.launcher.minecraft_session.profile import ProfileRequest, ProfileUseCase
from application.use_cases.launcher.publish_release import (
    CreateReleaseResponse,
    PublishReleaseRequest,
    PublishReleaseUseCase,
)
from domain.entities.base import MCAccessToken, MCServerID, SemVer, Url, UserRelatedHandle
from domain.entities.launcher import Platform
from domain.interfaces.services.profile_signer import ProfileSigner
from presentation.dependencies.auth import CI_ADMIN_USER, CURRENT_USER
from presentation.dependencies.services import get_profile_signer
from presentation.routers.auth.schemas import LauncherLoginResponse, LoginRequest
from presentation.routers.launcher.dependencies import (
    get_add_release_asset_uc,
    get_check_update_uc,
    get_create_mc_session_uc,
    get_has_joined_uc,
    get_join_server_uc,
    get_latest_platform_release_uc,
    get_login_uc,
    get_logout_from_others_uc,
    get_logout_uc,
    get_profile_uc,
    get_publish_release_uc,
    get_refresh_session_uc,
)
from presentation.routers.launcher.schemas import (
    AddReleaseAssetRequest as AddReleaseAssetSchema,
)
from presentation.routers.launcher.schemas import (
    CheckUpdateRequest as CheckUpdateSchema,
)
from presentation.routers.launcher.schemas import (
    JoinServerRequest as JoinServerSchema,
)
from presentation.routers.launcher.schemas import (
    LauncherLogoutFromOthersRequest as LauncherLogoutFromOthersSchema,
)
from presentation.routers.launcher.schemas import (
    LauncherSessionRequest,
)
from presentation.routers.launcher.schemas import (
    PublishReleaseRequest as PublishReleaseSchema,
)


def _parse_refresh_token(refresh_token: str) -> SessionCredentials:
    session_id, token = refresh_token.split(".", 1)
    return SessionCredentials(id=UUID(session_id), refresh_token=token)


launcher_router = APIRouter(prefix="/launcher", tags=["launcher"])


@launcher_router.get("/update", response_model=CheckUpdateResponse)
async def check_update(
        query: Annotated[CheckUpdateSchema, Depends()],
        uc: Annotated[CheckUpdateUseCase, Depends(get_check_update_uc)],
):
    return await uc.execute(
        dto=CheckUpdateRequest(
            platform=query.platform,
            version=SemVer(query.version),
        )
    )


@launcher_router.post("/session", response_model=MinecraftSessionResponse, status_code=201)
async def create_minecraft_session(
        user: CURRENT_USER,
        uc: Annotated[CreateMinecraftSessionUseCase, Depends(get_create_mc_session_uc)],
):
    return await uc.execute(user=user)


@launcher_router.post("/sessionserver/session/minecraft/join", status_code=204)
async def join_server(
        data: JoinServerSchema,
        uc: Annotated[JoinServerUseCase, Depends(get_join_server_uc)],
):
    await uc.execute(
        dto=JoinServerRequest(
            access_token=MCAccessToken(data.access_token),
            selected_profile=data.selected_profile,
            server_id=MCServerID(data.server_id),
        )
    )


@launcher_router.get("/sessionserver/session/minecraft/has-joined", response_model=ProfileResponse)
async def has_joined(
        username: str,
        server_id: str,
        uc: Annotated[HasJoinedServerUseCase, Depends(get_has_joined_uc)],
):
    return await uc.execute(
        dto=HasJoinedRequest(
            username=UserRelatedHandle(username),
            server_id=MCServerID(server_id),
        )
    )


@launcher_router.get("/sessionserver/session/minecraft/profile/{profile_uuid}", response_model=ProfileResponse)
async def get_profile(
        profile_uuid: UUID,
        uc: Annotated[ProfileUseCase, Depends(get_profile_uc)],
):
    return await uc.execute(dto=ProfileRequest(uuid=profile_uuid))


@launcher_router.get("/releases/latest", response_model=LauncherReleaseResponse)
async def get_latest_release(
        platform: Platform,
        uc: Annotated[GetLatestPlatformReleaseUseCase, Depends(get_latest_platform_release_uc)],
):
    return await uc.execute(dto=GetLatestPlatformReleaseRequest(platform=platform))


@launcher_router.post("/releases", response_model=CreateReleaseResponse, status_code=201)
async def publish_release(
        data: PublishReleaseSchema,
        user: CI_ADMIN_USER,
        uc: Annotated[PublishReleaseUseCase, Depends(get_publish_release_uc)],
):
    return await uc.execute(
        dto=PublishReleaseRequest(
            version=SemVer(data.version),
            changelog=data.changelog,
            is_mandatory=data.is_mandatory,
        ),
        user=user,
    )


@launcher_router.post("/releases/{release_id}/assets", status_code=201)
async def add_release_asset(
        release_id: int,
        data: AddReleaseAssetSchema,
        user: CI_ADMIN_USER,
        uc: Annotated[AddReleaseAssetUseCase, Depends(get_add_release_asset_uc)],
):
    await uc.execute(
        dto=AddReleaseAssetRequest(
            release_id=release_id,
            platform=data.platform,
            download_url=Url(data.download_url),
            checksum=data.checksum,
            file_size=data.file_size,
        ),
        user=user,
    )


@launcher_router.post("/auth/login", response_model=LauncherLoginResponse)
async def launcher_login(
        request: Request,
        data: LoginRequest,
        uc: Annotated[LoginUseCase, Depends(get_login_uc)],
):
    result = await uc.execute(
        dto=UserLoginRequest(
            username=UserRelatedHandle(data.username),
            password=data.password,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    )
    return LauncherLoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_split_token,
    )


@launcher_router.post("/auth/logout", status_code=204)
async def launcher_logout(
        data: LauncherSessionRequest,
        uc: Annotated[LogoutUseCase, Depends(get_logout_uc)],
):
    await uc.execute(dto=_parse_refresh_token(data.refresh_token))


@launcher_router.post("/auth/logout/others", status_code=204)
async def launcher_logout_from_others(
        data: LauncherLogoutFromOthersSchema,
        uc: Annotated[LogoutFromOthersUseCase, Depends(get_logout_from_others_uc)],
):
    await uc.execute(
        dto=LogoutFromOthersRequest(
            password=data.password,
            session_credentials=_parse_refresh_token(data.refresh_token),
        )
    )


@launcher_router.post("/auth/refresh", response_model=LauncherLoginResponse)
async def launcher_refresh(
        data: LauncherSessionRequest,
        uc: Annotated[RefreshSessionUseCase, Depends(get_refresh_session_uc)],
):
    result = await uc.execute(dto=_parse_refresh_token(data.refresh_token))
    return LauncherLoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_split_token,
    )


@launcher_router.get("")
async def authlib_injector_metadata(
        profile_signer: Annotated[ProfileSigner, Depends(get_profile_signer)]
):
    return JSONResponse(
        {
            "meta": {
                "serverName": "Infinity Server",
                "implementationName": "infinity-auth",
                "implementationVersion": "1.0.0"
            },
            "skinDomains": ["storage.infinityserver.ru"],
            "signaturePublickey": f"-----BEGIN PUBLIC KEY-----\n{profile_signer.get_public_key()}\n-----END PUBLIC KEY-----\n"
        }
    )
