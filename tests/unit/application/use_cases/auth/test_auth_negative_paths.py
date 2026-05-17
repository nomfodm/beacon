import uuid
from unittest.mock import AsyncMock

import pytest

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from application.use_cases.auth.logout import LogoutUseCase
from application.use_cases.auth.logout_from_others import LogoutFromOthersRequest, LogoutFromOthersUseCase
from application.use_cases.auth.refresh_session import RefreshSessionUseCase
from domain.entities.session import Session
from domain.entities.user import User
from domain.exceptions.session import SessionExpiredError, SessionRevokedError, TokenAuthenticityError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [SessionRevokedError("x"), SessionExpiredError("x"), TokenAuthenticityError("x")])
async def test_refresh_session_fails_and_skips_commit(
    mock_uow: UnitOfWork, mock_auth_service: AuthService, fake_session: Session, error, mocker
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=fake_session)
    mock_auth_service.verify_session.side_effect = error
    mock_cache = mocker.AsyncMock()
    mock_cache.get = AsyncMock(return_value=None)
    uc = RefreshSessionUseCase(uow=mock_uow, auth_service=mock_auth_service, idempotency_cache=mock_cache)

    with pytest.raises(type(error)):
        await uc.execute(dto=SessionCredentials(id=uuid.uuid4(), refresh_token="refresh_token"))

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_logout_calls_delete_with_session(
    mock_uow: UnitOfWork, mock_auth_service: AuthService, fake_session: Session
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=fake_session)
    uc = LogoutUseCase(uow=mock_uow, auth_service=mock_auth_service)

    await uc.execute(dto=SessionCredentials(id=uuid.uuid4(), refresh_token="refresh_token"))

    mock_uow.sessions.delete.assert_awaited_once_with(session=fake_session)


@pytest.mark.asyncio
async def test_logout_from_others_calls_delete_others(
    mock_uow: UnitOfWork, mock_auth_service: AuthService, fake_session: Session, fake_user: User, mocker
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=fake_session)
    mock_uow.users.get_by_id = AsyncMock(return_value=fake_user)
    hasher = mocker.MagicMock()
    hasher.verify.return_value = True
    uc = LogoutFromOthersUseCase(uow=mock_uow, auth_service=mock_auth_service, hasher=hasher)

    await uc.execute(
        dto=LogoutFromOthersRequest(
            password="correct_password",
            session_credentials=SessionCredentials(id=uuid.uuid4(), refresh_token="refresh_token"),
        )
    )

    mock_uow.sessions.delete_others_by_user_id.assert_awaited_once_with(
        user_id=fake_session.user_id, exclude_session_id=fake_session.id
    )
