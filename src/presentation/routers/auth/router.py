from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from application.use_cases.auth.get_sessions import GetSessionsUseCase, SessionResponse
from application.use_cases.auth.login import LoginUseCase, UserLoginRequest
from application.use_cases.auth.logout import LogoutUseCase
from application.use_cases.auth.logout_from_others import LogoutFromOthersRequest, LogoutFromOthersUseCase
from application.use_cases.auth.refresh_session import RefreshSessionUseCase
from application.use_cases.auth.register_user_and_login import RegisterUserAndLoginUseCase, UserRegisterRequest
from application.use_cases.auth.reset_password import ResetPasswordRequest, ResetPasswordUseCase
from application.use_cases.auth.revoke_session import RevokeSessionRequest, RevokeSessionUseCase
from domain.entities.base import Email, UserRelatedHandle
from presentation.limiter import limiter
from presentation.routers.auth.dependencies import (
    SESSION_CREDENTIALS,
    get_login_uc,
    get_logout_from_others_uc,
    get_logout_uc,
    get_refresh_session_uc,
    get_register_user_and_login_uc,
    get_reset_password_uc,
    get_revoke_session_uc,
    get_sessions_uc,
)
from presentation.routers.auth.schemas import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
)
from presentation.routers.auth.schemas import (
    LogoutFromOthersRequest as LogoutFromOthersSchema,
)
from presentation.routers.auth.schemas import (
    ResetPasswordRequest as ResetPasswordSchema,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_PARAMS = {
    "key": "refresh_token",
    "httponly": True,
    "secure": True,
    "samesite": "strict",
    "max_age": 60 * 60 * 24 * 15,
}


@auth_router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
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
    response.set_cookie(value=result.refresh_split_token, **REFRESH_COOKIE_PARAMS)
    return LoginResponse(access_token=result.access_token)


@auth_router.post("/signup", response_model=LoginResponse, status_code=201)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    response: Response,
    data: SignupRequest,
    uc: Annotated[RegisterUserAndLoginUseCase, Depends(get_register_user_and_login_uc)],
):
    result = await uc.execute(
        dto=UserRegisterRequest(
            username=UserRelatedHandle(data.username),
            password=data.password,
            email=Email(str(data.email)),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    )
    response.set_cookie(value=result.refresh_split_token, **REFRESH_COOKIE_PARAMS)
    return LoginResponse(access_token=result.access_token)


@auth_router.post("/logout", status_code=204)
async def logout(
    response: Response,
    credentials: SESSION_CREDENTIALS,
    uc: Annotated[LogoutUseCase, Depends(get_logout_uc)],
):
    await uc.execute(dto=credentials)
    response.delete_cookie("refresh_token")


@auth_router.post("/logout/others", status_code=204)
async def logout_from_others(
    data: LogoutFromOthersSchema,
    credentials: SESSION_CREDENTIALS,
    uc: Annotated[LogoutFromOthersUseCase, Depends(get_logout_from_others_uc)],
):
    await uc.execute(
        dto=LogoutFromOthersRequest(
            password=data.password,
            session_credentials=credentials,
        )
    )


@auth_router.get("/sessions", response_model=list[SessionResponse])
async def get_sessions(
    credentials: SESSION_CREDENTIALS,
    uc: Annotated[GetSessionsUseCase, Depends(get_sessions_uc)],
):
    return await uc.execute(dto=credentials)


@auth_router.post("/sessions/refresh", response_model=LoginResponse)
async def refresh_session(
    response: Response,
    credentials: SESSION_CREDENTIALS,
    uc: Annotated[RefreshSessionUseCase, Depends(get_refresh_session_uc)],
):
    result = await uc.execute(dto=credentials)
    response.set_cookie(value=result.refresh_split_token, **REFRESH_COOKIE_PARAMS)
    return LoginResponse(access_token=result.access_token)


@auth_router.delete("/sessions/{session_id}", status_code=204)
async def revoke_session(
    session_id: UUID,
    credentials: SESSION_CREDENTIALS,
    uc: Annotated[RevokeSessionUseCase, Depends(get_revoke_session_uc)],
):
    await uc.execute(
        dto=RevokeSessionRequest(
            session_credentials=credentials,
            session_id_to_revoke=session_id,
        )
    )


@auth_router.post("/password/reset", status_code=204)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    data: ResetPasswordSchema,
    uc: Annotated[ResetPasswordUseCase, Depends(get_reset_password_uc)],
):
    await uc.execute(
        dto=ResetPasswordRequest(
            email=Email(str(data.email)),
            verification_code=data.verification_code,
            new_password=data.new_password,
        )
    )
