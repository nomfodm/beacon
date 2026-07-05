import re
from dataclasses import dataclass

from domain.exceptions.base import ValidationError


@dataclass(frozen=True)
class IdentName:
    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", self.value.strip())
        self._validate()

    def _validate(self):
        pass

    def __str__(self):
        return self.value


@dataclass(frozen=True)
class UserRelatedHandle(IdentName):
    _pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9]{3,11}$")

    def _validate(self):
        if not self._pattern.match(self.value):
            raise ValidationError(
                "Имя пользователя должно быть от 4 до 12 символов, состоять только из букв и не начинаться с цифры."
            )


@dataclass(frozen=True)
class ContentLabel(IdentName):
    _pattern = re.compile(r"^[a-zA-Zа-яА-Я0-9][a-zA-Zа-яА-Я0-9\s\-_!@#$%^&*()=+\[\]{}|;:',.<>?\"'\\/]{2,63}$")

    def _validate(self):
        if not self._pattern.match(self.value):
            raise ValidationError("Название должно быть от 3 до 64 символов и начинаться с буквы или цифры.")


@dataclass(frozen=True)
class Email(IdentName):
    _pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def _validate(self):
        if not self._pattern.match(self.value):
            raise ValidationError(f"Неверный формат E-mail ({self.value}).")


@dataclass(frozen=True)
class Url(IdentName):
    _pattern = re.compile(
        r"^(https?|ftp)://"  # протоколы
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # домен
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # или ip
        r"(?::\d+)?"  # порт
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    def _validate(self):
        if not self._pattern.match(self.value):
            raise ValidationError(f"Invalid URL format: {self.value}")


@dataclass(frozen=True)
class MCAccessToken(IdentName):
    def _validate(self):
        if len(self.value) != 32:
            raise ValidationError("Неверная длина токена авторизации (32).")


@dataclass(frozen=True)
class MCServerID(IdentName): ...
    # def _validate(self):
    #     if len(self.value) not in [32, 33]:
    #         raise ValidationError("Неверная длина serverID (32-33).")


@dataclass(frozen=True)
class SemVer(IdentName):
    def _validate(self) -> None:
        parts = self.value.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValidationError(f"Некорректная версия: {self.value!r}")

    def _as_tuple(self) -> tuple[int, ...]:
        return tuple(int(p) for p in self.value.split("."))

    def __gt__(self, other: "SemVer") -> bool:
        return self._as_tuple() > other._as_tuple()
