import dataclasses
import json
import uuid
from unittest.mock import AsyncMock

import pytest

from application.dtos.auth import SessionCredentials, TokenPairResponse
from application.services.auth import AuthService
from application.use_cases.auth.refresh_session import RefreshSessionUseCase
from domain.entities.session import Session
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def mock_idempotency_cache(mocker):
    cache = mocker.AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.save = AsyncMock()
    return cache


@pytest.fixture
def uc(mock_auth_service: AuthService, mock_uow: UnitOfWork, mock_idempotency_cache):
    return RefreshSessionUseCase(uow=mock_uow, auth_service=mock_auth_service, idempotency_cache=mock_idempotency_cache)


@pytest.fixture
def dto():
    return SessionCredentials(id=uuid.uuid4(), refresh_token="refresh_token")


@pytest.fixture
def mock_uow(mock_uow: UnitOfWork, fake_session: Session):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=fake_session)
    return mock_uow


@pytest.mark.asyncio
async def test_refresh_session_success(
    mock_uow: UnitOfWork,
    uc: RefreshSessionUseCase,
    mock_auth_service: AuthService,
    mock_idempotency_cache,
    dto: SessionCredentials,
    fake_session: Session,
):
    result = await uc.execute(dto=dto)

    mock_auth_service.generate_access_token.assert_called_once_with(user_id=1)
    mock_auth_service.generate_refresh_token.assert_called_once()

    assert result.access_token == "access_token"
    assert result.refresh_split_token == f"{fake_session.id}.refresh_token"

    assert fake_session.refresh_token_hash == "refresh_token_hash"
    mock_uow.sessions.save.assert_awaited_once_with(session=fake_session)
    mock_uow.commit.assert_called_once()

    mock_idempotency_cache.save.assert_awaited_once()
    save_kwargs = mock_idempotency_cache.save.call_args.kwargs
    assert save_kwargs["token"] == dto.refresh_token
    assert json.loads(save_kwargs["payload"]) == dataclasses.asdict(result)


@pytest.mark.asyncio
async def test_refresh_session_returns_cached_response_on_retry(
    mock_uow: UnitOfWork,
    mock_auth_service: AuthService,
    mock_idempotency_cache,
    dto: SessionCredentials,
):
    cached_response = TokenPairResponse(access_token="cached_access", refresh_split_token="uuid.cached_refresh")
    mock_idempotency_cache.get = AsyncMock(return_value=json.dumps(dataclasses.asdict(cached_response)))

    uc = RefreshSessionUseCase(uow=mock_uow, auth_service=mock_auth_service, idempotency_cache=mock_idempotency_cache)
    result = await uc.execute(dto=dto)

    assert result == cached_response
    mock_uow.sessions.get_by_id_or_raise.assert_not_called()
    mock_auth_service.generate_refresh_token.assert_not_called()
    mock_uow.commit.assert_not_called()
    mock_idempotency_cache.save.assert_not_called()
