from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from application.use_cases.launcher.add_release_asset import AddReleaseAssetRequest, AddReleaseAssetUseCase
from domain.entities.base import SemVer, Url
from domain.entities.launcher import LauncherRelease, Platform
from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError
from domain.exceptions.launcher import LauncherReleaseNotFoundError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def admin_user(active_user: User) -> User:
    active_user.roles = {Role.ADMIN}
    return active_user


@pytest.fixture
def uc(mock_uow: UnitOfWork) -> AddReleaseAssetUseCase:
    return AddReleaseAssetUseCase(uow=mock_uow)


@pytest.fixture
def release() -> LauncherRelease:
    return LauncherRelease(
        id=1,
        version=SemVer("1.3.0"),
        changelog=["Fix"],
        released_at=datetime.now(UTC),
    )


@pytest.fixture
def dto() -> AddReleaseAssetRequest:
    return AddReleaseAssetRequest(
        release_id=1,
        platform=Platform.WINDOWS,
        download_url=Url("https://example.com/launcher-1.3.0.exe"),
        checksum="abc123",
        file_size=1024,
    )


@pytest.mark.asyncio
async def test_add_release_asset_success(
    mock_uow: UnitOfWork,
    uc: AddReleaseAssetUseCase,
    admin_user: User,
    release: LauncherRelease,
    dto: AddReleaseAssetRequest,
):
    mock_uow.launcher_releases.get_by_id_or_raise = AsyncMock(return_value=release)

    result = await uc.execute(dto=dto, user=admin_user)

    assert result.ok is True
    mock_uow.launcher_releases.get_by_id_or_raise.assert_awaited_once_with(id=1)
    mock_uow.launcher_releases.save_launcher_release_asset.assert_awaited_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_add_release_asset_raises_when_release_not_found(
    mock_uow: UnitOfWork, uc: AddReleaseAssetUseCase, admin_user: User, dto: AddReleaseAssetRequest
):
    mock_uow.launcher_releases.get_by_id_or_raise = AsyncMock(
        side_effect=LauncherReleaseNotFoundError("Версия не найдена.")
    )

    with pytest.raises(LauncherReleaseNotFoundError):
        await uc.execute(dto=dto, user=admin_user)

    mock_uow.launcher_releases.save_launcher_release_asset.assert_not_called()
    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_add_release_asset_raises_for_non_admin(
    mock_uow: UnitOfWork, uc: AddReleaseAssetUseCase, active_user: User, dto: AddReleaseAssetRequest
):
    with pytest.raises(AccessDeniedError):
        await uc.execute(dto=dto, user=active_user)

    mock_uow.launcher_releases.save_launcher_release_asset.assert_not_called()
    mock_uow.commit.assert_not_called()
