import datetime
from functools import wraps

from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError, UnauthenticatedError, UserBannedError, UserNeedsActivationError


def require_login(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        user = kwargs.get("user")

        if not isinstance(user, User):
            raise UnauthenticatedError("Объект пользователя невалиден или отсутствует.")

        if not user.is_active:
            raise UserNeedsActivationError("Подтвердите почту для активации аккаунта.")

        return await func(self, *args, **kwargs)

    return wrapper


def require_not_banned(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        user = kwargs.get("user")

        if not isinstance(user, User):
            raise UnauthenticatedError("Объект пользователя невалиден или отсутствует.")

        ban_status = user.ban_status
        if ban_status.is_banned:
            if ban_status.is_permanent:
                raise UserBannedError("Пользователь заблокирован бессрочно")
            if ban_status.banned_till and ban_status.banned_till > datetime.datetime.now(tz=datetime.UTC):
                raise UserBannedError(f"Пользователь временно заблокирован (до {ban_status.banned_till})")
        return await func(self, *args, **kwargs)

    return wrapper


def roles_allowed(*roles: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            user = kwargs.get("user")

            if not isinstance(user, User):
                raise UnauthenticatedError("Объект пользователя невалиден или отсутствует.")

            required_roles = set(roles)
            if not user.roles.intersection(required_roles):
                raise AccessDeniedError(f"Недостаточно прав. Требуется хотя бы одна из этих ролей: {required_roles}")

            return await func(self, *args, **kwargs)

        return wrapper

    return decorator
