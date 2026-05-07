from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from application.use_cases.launcher.add_release_asset import AddReleaseAssetRequest, AddReleaseAssetUseCase
from application.use_cases.launcher.publish_release import PublishReleaseRequest, PublishReleaseUseCase
from domain.entities.base import SemVer, Url
from domain.entities.launcher import LauncherRelease, LauncherReleaseAsset, Platform
from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def admin_user(active_user: User) -> User:
    active_user.roles = {Role.ADMIN}
    return active_user


@pytest.fixture
def release() -> LauncherRelease:
    return LauncherRelease(
        id=1,
        version=SemVer("2.0.0"),
        changelog=["First release"],
        released_at=datetime.now(UTC),
        is_mandatory=False,
        assets=[],
    )


@pytest.mark.asyncio
async def test_publish_release_success(mock_uow: UnitOfWork, admin_user: User, release: LauncherRelease):
    mock_uow.launcher_releases.save = AsyncMock(return_value=release)
    uc = PublishReleaseUseCase(uow=mock_uow)

    result = await uc.execute(
        dto=PublishReleaseRequest(version=SemVer("2.0.0"), changelog=["First release"], is_mandatory=False),
        user=admin_user,
    )

    assert result.id == 1
    assert result.version == "2.0.0"
    assert result.changelog == ["First release"]
    assert result.is_mandatory is False
    mock_uow.launcher_releases.save.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_publish_release_sets_released_at(mock_uow: UnitOfWork, admin_user: User, release: LauncherRelease):
    mock_uow.launcher_releases.save = AsyncMock(return_value=release)
    uc = PublishReleaseUseCase(uow=mock_uow)

    await uc.execute(
        dto=PublishReleaseRequest(version=SemVer("2.0.0"), changelog=[], is_mandatory=True),
        user=admin_user,
    )

    saved_release: LauncherRelease = mock_uow.launcher_releases.save.call_args.kwargs["release"]
    assert saved_release.released_at.tzinfo is not None
    assert saved_release.is_mandatory is True


@pytest.mark.asyncio
async def test_publish_release_requires_admin(mock_uow: UnitOfWork, active_user: User):
    uc = PublishReleaseUseCase(uow=mock_uow)

    with pytest.raises(AccessDeniedError):
        await uc.execute(
            dto=PublishReleaseRequest(version=SemVer("2.0.0"), changelog=[], is_mandatory=False),
            user=active_user,
        )

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_add_release_asset_success(mock_uow: UnitOfWork, admin_user: User):
    mock_uow.launcher_releases.get_by_id_or_raise = AsyncMock(return_value=SimpleNamespace(id=1))
    uc = AddReleaseAssetUseCase(uow=mock_uow)

    result = await uc.execute(
        dto=AddReleaseAssetRequest(
            release_id=1,
            platform=Platform.WINDOWS,
            download_url=Url("https://example.com/launcher.exe"),
            checksum="deadbeef",
            file_size=123456,
        ),
        user=admin_user,
    )

    assert result.ok is True
    mock_uow.launcher_releases.get_by_id_or_raise.assert_awaited_once_with(id=1)
    saved_asset: LauncherReleaseAsset = mock_uow.launcher_releases.save_launcher_release_asset.call_args.kwargs["asset"]
    assert saved_asset.platform == Platform.WINDOWS
    assert saved_asset.checksum == "deadbeef"
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_release_asset_requires_admin(mock_uow: UnitOfWork, active_user: User):
    uc = AddReleaseAssetUseCase(uow=mock_uow)

    with pytest.raises(AccessDeniedError):
        await uc.execute(
            dto=AddReleaseAssetRequest(
                release_id=1,
                platform=Platform.WINDOWS,
                download_url=Url("https://example.com/launcher.exe"),
                checksum="deadbeef",
                file_size=123456,
            ),
            user=active_user,
        )

    mock_uow.commit.assert_not_called()
