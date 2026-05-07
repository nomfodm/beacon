from dataclasses import dataclass

from application.decorators.auth import require_not_banned
from application.dtos.common import StatusResponse
from domain.entities.base import Email
from domain.entities.user import User
from domain.exceptions.auth import EmailTakenError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ChangeEmailRequest:
    new_email: Email


class ChangeEmailUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_not_banned
    async def execute(self, *, dto: ChangeEmailRequest, user: User) -> StatusResponse:
        async with self._uow:
            if user.email == dto.new_email:
                raise EmailTakenError("Вы ввели такой же E-mail.")

            existing_email = await self._uow.users.get_by_email(email=dto.new_email)
            if existing_email and existing_email.id != user.id:
                raise EmailTakenError("Этот E-mail занят.")

            user.email = dto.new_email
            user.is_active = False  # надо заново активировать аккаунт

            await self._uow.users.save(user=user)
            await self._uow.commit()
            return StatusResponse()
