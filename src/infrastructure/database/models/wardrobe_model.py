from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.base import ContentLabel, Url
from domain.entities.wardrobe import SkinModel, Texture, TextureCatalogItem, TextureType, WardrobeItem
from infrastructure.database.models.base import Base


class TextureModel(Base):
    __tablename__ = "textures"

    id: Mapped[int | None] = mapped_column(primary_key=True, nullable=False)
    hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    type: Mapped[str]
    url: Mapped[str]
    model: Mapped[str | None]

    def to_domain(self) -> Texture:
        return Texture(
            id=self.id,
            hash=self.hash,
            type=TextureType(self.type),
            url=Url(self.url),
            model=SkinModel(self.model) if self.model else None,
        )

    @classmethod
    def from_domain(cls, t: Texture) -> "TextureModel":
        return cls(
            id=t.id,
            hash=t.hash,
            type=t.type.value,
            url=t.url.value,
            model=t.model.value if t.model else None,
        )


class WardrobeItemModel(Base):
    __tablename__ = "wardrobe_items"

    id: Mapped[int | None] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    texture_id: Mapped[int] = mapped_column(ForeignKey("textures.id"))
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    label: Mapped[str]

    texture: Mapped["TextureModel"] = relationship()

    def to_domain(self) -> WardrobeItem:
        return WardrobeItem(
            id=self.id,
            user_id=self.user_id,
            author_id=self.author_id,
            texture=self.texture.to_domain(),
            acquired_at=self.acquired_at,
            label=ContentLabel(self.label),
        )

    @classmethod
    def from_domain(cls, wi: WardrobeItem) -> "WardrobeItemModel":
        return cls(
            id=wi.id,
            user_id=wi.user_id,
            author_id=wi.author_id,
            texture_id=wi.texture.id,
            acquired_at=wi.acquired_at,
            label=wi.label.value,
        )


class TextureCatalogItemModel(Base):
    __tablename__ = "texture_catalog"

    id: Mapped[int | None] = mapped_column(primary_key=True, nullable=False)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    texture_id: Mapped[int] = mapped_column(ForeignKey("textures.id"))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    texture: Mapped["TextureModel"] = relationship()

    def to_domain(self) -> TextureCatalogItem:
        return TextureCatalogItem(
            id=self.id,
            title=ContentLabel(self.title),
            author_id=self.author_id,
            texture=self.texture.to_domain(),
            published_at=self.published_at,
        )

    @classmethod
    def from_domain(cls, tci: TextureCatalogItem) -> "TextureCatalogItemModel":
        return cls(
            id=tci.id,
            title=tci.title.value,
            author_id=tci.author_id,
            texture_id=tci.texture.id,
            published_at=tci.published_at,
        )
