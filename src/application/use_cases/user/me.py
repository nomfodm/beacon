import datetime
from dataclasses import dataclass
from uuid import UUID

from application.dtos.user import BanStatusResponse
from application.dtos.wardrobe import WardrobeItemResponse
from domain.entities.user import User
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class MinecraftProfileResponse:
    uuid: UUID
    nickname: str
    wardrobe: list[WardrobeItemResponse]
    id: int
    active_skin: WardrobeItemResponse | None = None
    active_cape: WardrobeItemResponse | None = None


@dataclass(frozen=True)
class UserResponse:
    id: int
    email: str
    username: str
    roles: list[str]
    ban_status: BanStatusResponse
    is_active: bool
    registered_at: datetime.datetime

    minecraft_profile: MinecraftProfileResponse


class MeUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    # @require_login
    async def execute(self, *, user: User) -> UserResponse:
        async with self._uow:
            mc_profile = await self._uow.minecraft_profiles.get_by_user_id_or_raise(user_id=user.id)

            wardrobe = await self._uow.wardrobe.get_user_wardrobe(user_id=user.id)

            active_skin = (
                await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(
                    id=mc_profile.active_skin_id, user_id=mc_profile.user_id
                )
                if mc_profile.active_skin_id is not None
                else None
            )

            active_cape = (
                await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(
                    id=mc_profile.active_cape_id, user_id=mc_profile.user_id
                )
                if mc_profile.active_cape_id is not None
                else None
            )

            return UserResponse(
                id=user.id,
                email=user.email.value,
                username=user.username.value,
                roles=list(user.roles),
                ban_status=BanStatusResponse(
                    is_banned=user.ban_status.is_banned,
                    is_permanent=user.ban_status.is_permanent,
                    banned_till=user.ban_status.banned_till,
                    admin_user_id=user.ban_status.admin_user_id,
                ),
                is_active=user.is_active,
                registered_at=user.registered_at,
                minecraft_profile=MinecraftProfileResponse(
                    id=mc_profile.id,
                    uuid=mc_profile.uuid,
                    nickname=mc_profile.nickname.value,
                    wardrobe=[WardrobeItemResponse.from_domain(item) for item in wardrobe],
                    active_cape=WardrobeItemResponse.from_domain(active_cape) if active_cape else None,
                    active_skin=WardrobeItemResponse.from_domain(active_skin) if active_skin else None,
                ),
            )
