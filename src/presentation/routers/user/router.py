from typing import Annotated

from fastapi import APIRouter, Depends, Request

from application.dtos.common import StatusResponse
from application.dtos.login_history import LoginHistoryEntryResponse
from application.use_cases.user.activate_user import ActivateUserRequest, ActivateUserUseCase
from application.use_cases.user.change_email import ChangeEmailRequest, ChangeEmailUseCase
from application.use_cases.user.change_password import ChangePasswordRequest, ChangePasswordUseCase
from application.use_cases.user.change_username import ChangeUsernameRequest, ChangeUsernameUseCase
from application.use_cases.user.get_login_history import GetLoginHistoryUseCase
from application.use_cases.user.me import MeUseCase, UserResponse
from application.use_cases.user.minecraft_profile.change_nickname import ChangeNicknameRequest, ChangeNicknameUseCase
from application.use_cases.user.send_verification_code import (
    SendVerificationCodeRequest,
    SendVerificationCodeUseCase,
    VerificationCodeResponse,
)
from domain.entities.base import Email, UserRelatedHandle
from presentation.dependencies.auth import CURRENT_USER
from presentation.limiter import limiter
from presentation.routers.user.dependencies import (
    get_activate_user_uc,
    get_change_email_uc,
    get_change_nickname_uc,
    get_change_password_uc,
    get_change_username_uc,
    get_login_history_uc,
    get_me_uc,
    get_send_verification_code_uc,
)
from presentation.routers.user.schemas import (
    ActivateUserRequest as ActivateUserSchema,
)
from presentation.routers.user.schemas import (
    ChangeEmailRequest as ChangeEmailSchema,
)
from presentation.routers.user.schemas import (
    ChangeNicknameRequest as ChangeNicknameSchema,
)
from presentation.routers.user.schemas import (
    ChangePasswordRequest as ChangePasswordSchema,
)
from presentation.routers.user.schemas import (
    ChangeUsernameRequest as ChangeUsernameSchema,
)
from presentation.routers.user.schemas import (
    SendVerificationCodeRequest as SendVerificationCodeSchema,
)

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/me", response_model=UserResponse)
async def me(
    user: CURRENT_USER,
    uc: Annotated[MeUseCase, Depends(get_me_uc)],
):
    return await uc.execute(user=user)


@user_router.get("/me/login-history", response_model=list[LoginHistoryEntryResponse])
async def login_history(
    user: CURRENT_USER,
    uc: Annotated[GetLoginHistoryUseCase, Depends(get_login_history_uc)],
):
    return await uc.execute(user=user)


@user_router.post("/me/verification-code", response_model=VerificationCodeResponse)
@limiter.limit("10/minute")
async def send_verification_code(
    request: Request,
    data: SendVerificationCodeSchema,
    user: CURRENT_USER,
    uc: Annotated[SendVerificationCodeUseCase, Depends(get_send_verification_code_uc)],
):
    return await uc.execute(dto=SendVerificationCodeRequest(purpose=data.purpose), user=user)


@user_router.post("/activate", response_model=StatusResponse)
@limiter.limit("10/minute")
async def activate_user(
    request: Request,
    data: ActivateUserSchema,
    uc: Annotated[ActivateUserUseCase, Depends(get_activate_user_uc)],
):
    return await uc.execute(
        dto=ActivateUserRequest(
            email=Email(str(data.email)),
            verification_code=data.verification_code,
        )
    )


@user_router.patch("/me/email", response_model=StatusResponse)
@limiter.limit("10/minute")
async def change_email(
    request: Request,
    data: ChangeEmailSchema,
    user: CURRENT_USER,
    uc: Annotated[ChangeEmailUseCase, Depends(get_change_email_uc)],
):
    return await uc.execute(dto=ChangeEmailRequest(new_email=Email(str(data.new_email))), user=user)


@user_router.patch("/me/password", response_model=StatusResponse)
@limiter.limit("10/minute")
async def change_password(
    request: Request,
    data: ChangePasswordSchema,
    user: CURRENT_USER,
    uc: Annotated[ChangePasswordUseCase, Depends(get_change_password_uc)],
):
    return await uc.execute(
        dto=ChangePasswordRequest(
            old_password=data.old_password,
            new_password=data.new_password,
        ),
        user=user,
    )


@user_router.patch("/me/username", response_model=StatusResponse)
async def change_username(
    data: ChangeUsernameSchema,
    user: CURRENT_USER,
    uc: Annotated[ChangeUsernameUseCase, Depends(get_change_username_uc)],
):
    return await uc.execute(dto=ChangeUsernameRequest(new_username=UserRelatedHandle(data.new_username)), user=user)


@user_router.patch("/me/nickname", response_model=StatusResponse)
async def change_nickname(
    data: ChangeNicknameSchema,
    user: CURRENT_USER,
    uc: Annotated[ChangeNicknameUseCase, Depends(get_change_nickname_uc)],
):
    return await uc.execute(dto=ChangeNicknameRequest(new_nickname=UserRelatedHandle(data.new_nickname)), user=user)
