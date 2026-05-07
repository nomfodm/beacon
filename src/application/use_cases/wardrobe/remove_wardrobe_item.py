from dataclasses import dataclass

from application.decorators.auth import require_login, require_not_banned
from application.dtos.common import StatusResponse
from domain.entities.user import User
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass
class RemoveWardrobeItemRequest:
    id: int


class RemoveWardrobeItemUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @require_not_banned
    async def execute(self, *, dto: RemoveWardrobeItemRequest, user: User) -> StatusResponse:
        async with self._uow:
            item = await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(id=dto.id, user_id=user.id)
            await self._uow.minecraft_profiles.clear_active_cosmetics_for_wardrobe_items(wardrobe_item_ids=[item.id])
            await self._uow.wardrobe.delete(item=item)
            await self._uow.commit()
            return StatusResponse()
