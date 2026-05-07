import datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import Role, User
from domain.exceptions.user import UserNotFoundError
from domain.interfaces.services.token_service import TokenService
from domain.interfaces.unit_of_work import UnitOfWork
from infrastructure.config import settings
from presentation.dependencies.services import get_token_service
from presentation.dependencies.uow import get_uow

_http_bearer = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_http_bearer)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> User:
    payload = token_service.decode_access_token(token=credentials.credentials)
    user_id = int(payload["sub"])
    async with uow:
        user = await uow.users.get_by_id(id=user_id)
    if user is None:
        raise UserNotFoundError("Пользователь не найден.")
    return user


CURRENT_USER = Annotated[User, Depends(get_current_user)]


async def get_ci_admin_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_http_bearer)],
) -> User:
    if credentials.credentials != settings.secrets.ci_token.get_secret_value():
        raise HTTPException(status_code=401, detail="Неверный токен.")
    return User(
        email=Email("ci@ci.internal"),
        username=UserRelatedHandle("cibot"),
        password_hash="",
        registered_at=datetime.datetime.min,
        roles={Role.ADMIN},
        is_active=True,
    )


CI_ADMIN_USER = Annotated[User, Depends(get_ci_admin_user)]
