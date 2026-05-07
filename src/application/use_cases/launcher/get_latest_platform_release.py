from dataclasses import dataclass

from application.dtos.launcher import LauncherReleaseResponse
from domain.entities.launcher import Platform
from domain.exceptions.launcher import LauncherReleaseNotFoundError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass
class GetLatestPlatformReleaseRequest:
    platform: Platform


class GetLatestPlatformReleaseUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, dto: GetLatestPlatformReleaseRequest) -> LauncherReleaseResponse:
        async with self._uow:
            latest = await self._uow.launcher_releases.get_latest_for_platform(platform=dto.platform)
            if latest is None:
                raise LauncherReleaseNotFoundError("Под эту платформу не было выпущено ни одной версии.")
            return LauncherReleaseResponse.from_domain(release=latest, platform=dto.platform)
