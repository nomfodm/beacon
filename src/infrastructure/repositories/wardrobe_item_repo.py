from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.entities.wardrobe import WardrobeItem
from domain.exceptions.wardrobe import WardrobeItemNotFoundError
from domain.interfaces.repositories.wardrobe_item_repo import WardrobeItemRepository
from infrastructure.database.models.wardrobe_model import WardrobeItemModel


class SqlWardrobeItemRepository(WardrobeItemRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id_from_user_wardrobe(self, id: int, user_id: int) -> WardrobeItem | None:
        result = await self._session.execute(
            select(WardrobeItemModel)
            .where(WardrobeItemModel.id == id, WardrobeItemModel.user_id == user_id)
            .options(selectinload(WardrobeItemModel.texture))
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_id_from_user_wardrobe_or_raise(self, id: int, user_id: int) -> WardrobeItem:
        item = await self.get_by_id_from_user_wardrobe(id, user_id)
        if item is None:
            raise WardrobeItemNotFoundError("Предмет гардероба не найден.")
        return item

    async def save(self, item: WardrobeItem) -> WardrobeItem:
        merged = await self._session.merge(WardrobeItemModel.from_domain(item))
        await self._session.flush()
        await self._session.refresh(merged, ["texture"])
        return merged.to_domain()

    async def delete(self, item: WardrobeItem) -> None:
        await self._session.execute(delete(WardrobeItemModel).where(WardrobeItemModel.id == item.id))

    async def get_user_wardrobe(self, user_id: int) -> list[WardrobeItem]:
        result = await self._session.execute(
            select(WardrobeItemModel)
            .where(WardrobeItemModel.user_id == user_id)
            .options(selectinload(WardrobeItemModel.texture))
        )
        return [m.to_domain() for m in result.scalars().all()]

    async def get_ids_by_texture_id_except_user(self, texture_id: int, except_user_id: int) -> list[int]:
        result = await self._session.execute(
            select(WardrobeItemModel.id).where(
                WardrobeItemModel.texture_id == texture_id, WardrobeItemModel.user_id != except_user_id
            )
        )
        return list(result.scalars().all())

    async def delete_by_texture_id_except_user(self, texture_id: int, except_user_id: int) -> None:
        await self._session.execute(
            delete(WardrobeItemModel).where(
                WardrobeItemModel.texture_id == texture_id, WardrobeItemModel.user_id != except_user_id
            )
        )
