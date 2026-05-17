from datetime import datetime

from sqlalchemy import ARRAY, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import BanStatus, Role, User
from infrastructure.database.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int | None] = mapped_column(primary_key=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str]
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(default=False)

    roles: Mapped[list[str]] = mapped_column(ARRAY(String), server_default="{}")

    is_banned: Mapped[bool] = mapped_column(default=False)
    is_permanent: Mapped[bool] = mapped_column(default=False)
    banned_till: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    admin_user_id: Mapped[int | None] = mapped_column(nullable=True)

    def to_domain(self) -> User:
        return User(
            id=self.id,
            email=Email(self.email),
            username=UserRelatedHandle(self.username),
            password_hash=self.password_hash,
            registered_at=self.registered_at,
            is_active=self.is_active,
            roles={Role(r) for r in self.roles},
            ban_status=BanStatus(
                is_banned=self.is_banned,
                is_permanent=self.is_permanent,
                banned_till=self.banned_till,
                admin_user_id=self.admin_user_id,
            ),
        )

    @classmethod
    def from_domain(cls, u: User) -> "UserModel":
        return cls(
            id=u.id,
            email=u.email.value,
            username=u.username.value,
            password_hash=u.password_hash,
            registered_at=u.registered_at,
            is_active=u.is_active,
            roles=[r.value for r in u.roles],
            is_banned=u.ban_status.is_banned,
            is_permanent=u.ban_status.is_permanent,
            banned_till=u.ban_status.banned_till,
            admin_user_id=u.ban_status.admin_user_id,
        )
