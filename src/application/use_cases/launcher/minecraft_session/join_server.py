import datetime
import uuid
from dataclasses import dataclass

from application.constants import MC_SESSION_TTL_SECONDS
from application.dtos.common import StatusResponse
from domain.entities.base import MCAccessToken, MCServerID
from domain.exceptions.minecraft import InvalidMCAccessToken
from domain.interfaces.unit_of_work import UnitOfWork
from src.domain.exceptions.auth import UserBannedError
from src.domain.exceptions.user import UserNotFoundError


@dataclass(frozen=True)
class JoinServerRequest:
    access_token: MCAccessToken
    selected_profile: uuid.UUID
    server_id: MCServerID


class JoinServerUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, *, dto: JoinServerRequest) -> StatusResponse:
        async with self._uow:
            mc_session = await self._uow.minecraft_sessions.get_by_profile_uuid_or_raise(
                profile_uuid=dto.selected_profile
            )
            user = await self._uow.users.get_by_id(id=mc_session.user_id)
            if not user:
                raise UserNotFoundError("Пользователь не найден")
            ban_status = user.ban_status
            if ban_status.is_banned:
                if ban_status.is_permanent:
                    raise UserBannedError("Пользователь заблокирован бессрочно")
                if ban_status.banned_till and ban_status.banned_till > datetime.datetime.now(tz=datetime.UTC):
                    raise UserBannedError(f"Пользователь временно заблокирован (до {ban_status.banned_till})")

            if mc_session.access_token != dto.access_token:
                raise InvalidMCAccessToken("Неверный токен доступа.")

            mc_session.server_id = dto.server_id

            await self._uow.minecraft_sessions.save(mc_session=mc_session, ttl=MC_SESSION_TTL_SECONDS)

            await self._uow.commit()
            return StatusResponse()
