from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.login_history import LoginHistoryEntry
from infrastructure.database.models.base import Base


class LoginHistoryEntryModel(Base):
    __tablename__ = "login_history"

    id: Mapped[int | None] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ip_address: Mapped[str | None]
    user_agent: Mapped[str | None]

    def to_domain(self) -> LoginHistoryEntry:
        return LoginHistoryEntry(
            id=self.id,
            user_id=self.user_id,
            timestamp=self.timestamp,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
        )

    @classmethod
    def from_domain(cls, e: LoginHistoryEntry) -> "LoginHistoryEntryModel":
        return cls(
            id=e.id,
            user_id=e.user_id,
            timestamp=e.timestamp,
            ip_address=e.ip_address,
            user_agent=e.user_agent,
        )
