import datetime
import uuid
from dataclasses import dataclass

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from domain.entities.session import Session
from domain.interfaces.unit_of_work import UnitOfWork

_utc = datetime.UTC


@dataclass(frozen=True)
class SessionResponse:
    created_at: datetime.datetime | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    last_used_at: datetime.datetime | None = None
    is_current: bool = False
    id: uuid.UUID | None = None

    @classmethod
    def from_domain(cls, session: Session, is_current: bool = False):
        return cls(
            created_at=session.created_at,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
            last_used_at=session.last_used_at,
            id=session.id,
            is_current=is_current,
        )


class GetSessionsUseCase:
    def __init__(self, *, uow: UnitOfWork, auth_service: AuthService):
        self._uow = uow
        self._auth_service = auth_service

    async def execute(self, *, dto: SessionCredentials) -> list[SessionResponse]:
        async with self._uow:
            session = await self._uow.sessions.get_by_id_or_raise(uuid=dto.id)
            self._auth_service.verify_session(refresh_token=dto.refresh_token, session=session)

            all_sessions = await self._uow.sessions.get_all_by_user_id(user_id=session.user_id)

            now = datetime.datetime.now(_utc)
            return [
                SessionResponse.from_domain(session=s, is_current=s.id == session.id)
                for s in all_sessions
                if not s.is_revoked and s.expires_at > now
            ]
