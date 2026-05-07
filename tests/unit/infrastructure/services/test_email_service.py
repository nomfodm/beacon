import pytest

from domain.entities.base import Email
from infrastructure.services.email_service import SMTPEmailService


@pytest.fixture
def service() -> SMTPEmailService:
    return SMTPEmailService(
        host="smtp.example.com",
        port=587,
        username="user@example.com",
        password="secret",
        from_email="noreply@example.com",
        from_name="Infinity",
        use_tls=True,
    )


@pytest.mark.asyncio
async def test_send_verification_code_calls_smtp(service: SMTPEmailService, mocker):
    mock_send = mocker.patch("infrastructure.services.email_service.aiosmtplib.send", new_callable=mocker.AsyncMock)

    await service.send_verification_code(email=Email("player@example.com"), code="123456")

    mock_send.assert_awaited_once()
    _, kwargs = mock_send.call_args
    assert kwargs["hostname"] == "smtp.example.com"
    assert kwargs["port"] == 587
    assert kwargs["username"] == "user@example.com"
    assert kwargs["password"] == "secret"
    assert kwargs["use_tls"] is True


@pytest.mark.asyncio
async def test_send_verification_code_message_fields(service: SMTPEmailService, mocker):
    mock_send = mocker.patch("infrastructure.services.email_service.aiosmtplib.send", new_callable=mocker.AsyncMock)

    await service.send_verification_code(email=Email("player@example.com"), code="654321")

    message = mock_send.call_args.args[0]
    assert message["To"] == "player@example.com"
    assert "noreply@example.com" in message["From"]
    assert "Infinity" in message["From"]
    assert message["Subject"] == "[Infinity] Код подтверждения"


@pytest.mark.asyncio
async def test_send_verification_code_body_contains_code(service: SMTPEmailService, mocker):
    mock_send = mocker.patch("infrastructure.services.email_service.aiosmtplib.send", new_callable=mocker.AsyncMock)

    await service.send_verification_code(email=Email("player@example.com"), code="999888")

    message = mock_send.call_args.args[0]
    payload = message.get_payload(decode=False)
    body_text = payload[0].get_payload(decode=True).decode()
    assert "999888" in body_text
