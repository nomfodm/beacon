from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from domain.entities.base import Email
from domain.interfaces.services.email_service import EmailService


class SMTPEmailService(EmailService):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        from_email: str,
        from_name: str,
        use_tls: bool,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_email = from_email
        self._from_name = from_name
        self._use_tls = use_tls

    async def send_verification_code(self, *, email: Email, code: str) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = "[Infinity] Код подтверждения"
        message["From"] = f"{self._from_name} <{self._from_email}>"
        message["To"] = email.value
        message.attach(MIMEText(f"Ваш код подтверждения: {code}", "plain", "utf-8"))

        await aiosmtplib.send(
            message,
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            use_tls=self._use_tls,
        )
