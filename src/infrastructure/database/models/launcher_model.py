from datetime import datetime

from sqlalchemy import ARRAY, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.base import SemVer, Url
from domain.entities.launcher import LauncherRelease, LauncherReleaseAsset, Platform
from infrastructure.database.models.base import Base


class LauncherReleaseModel(Base):
    __tablename__ = "launcher_releases"

    id: Mapped[int | None] = mapped_column(primary_key=True, nullable=False)
    version: Mapped[str]
    released_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_mandatory: Mapped[bool] = mapped_column(default=False)
    changelog: Mapped[list[str]] = mapped_column(ARRAY(String), server_default="{}")

    assets: Mapped[list["LauncherReleaseAssetModel"]] = relationship()

    def to_domain(self) -> LauncherRelease:
        return LauncherRelease(
            id=self.id,
            version=SemVer(self.version),
            released_at=self.released_at,
            is_mandatory=self.is_mandatory,
            changelog=self.changelog,
            assets=[a.to_domain() for a in self.assets],
        )

    @classmethod
    def from_domain(cls, lr: LauncherRelease) -> "LauncherReleaseModel":
        return cls(
            id=lr.id,
            version=lr.version.value,
            released_at=lr.released_at,
            is_mandatory=lr.is_mandatory,
            changelog=lr.changelog,
        )


class LauncherReleaseAssetModel(Base):
    __tablename__ = "launcher_release_assets"

    id: Mapped[int | None] = mapped_column(primary_key=True, nullable=False)
    release_id: Mapped[int] = mapped_column(ForeignKey("launcher_releases.id"))
    platform: Mapped[str]
    download_url: Mapped[str]
    checksum: Mapped[str]
    file_size: Mapped[int]

    def to_domain(self) -> LauncherReleaseAsset:
        return LauncherReleaseAsset(
            id=self.id,
            release_id=self.release_id,
            platform=Platform(self.platform),
            download_url=Url(self.download_url),
            checksum=self.checksum,
            file_size=self.file_size,
        )

    @classmethod
    def from_domain(cls, lra: LauncherReleaseAsset) -> "LauncherReleaseAssetModel":
        return cls(
            id=lra.id,
            release_id=lra.release_id,
            platform=lra.platform.value,
            download_url=lra.download_url.value,
            checksum=lra.checksum,
            file_size=lra.file_size,
        )
