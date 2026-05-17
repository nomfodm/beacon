from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.base import UserRelatedHandle
from domain.entities.minecraft_profile import MinecraftProfile
from infrastructure.database.models.base import Base


class MinecraftProfileModel(Base):
    __tablename__ = "minecraft_profiles"

    id: Mapped[int | None] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    uuid: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True)
    nickname: Mapped[str] = mapped_column(String, unique=True, index=True)

    active_skin_id: Mapped[int | None] = mapped_column(ForeignKey("wardrobe_items.id"), nullable=True)
    active_cape_id: Mapped[int | None] = mapped_column(ForeignKey("wardrobe_items.id"), nullable=True)

    def to_domain(self) -> MinecraftProfile:
        return MinecraftProfile(
            id=self.id,
            user_id=self.user_id,
            uuid=self.uuid,
            nickname=UserRelatedHandle(self.nickname),
            active_skin_id=self.active_skin_id,
            active_cape_id=self.active_cape_id,
        )

    @classmethod
    def from_domain(cls, mp: MinecraftProfile) -> "MinecraftProfileModel":
        return cls(
            id=mp.id,
            user_id=mp.user_id,
            uuid=mp.uuid,
            nickname=mp.nickname.value,
            active_skin_id=mp.active_skin_id,
            active_cape_id=mp.active_cape_id,
        )
