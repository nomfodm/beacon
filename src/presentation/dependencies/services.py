from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from application.services.auth import AuthService
from application.services.minecraft_profile import MinecraftProfileService
from domain.interfaces.services.code_generator import CodeGenerator
from domain.interfaces.services.email_service import EmailService
from domain.interfaces.services.file_storage import FileStorage
from domain.interfaces.services.profile_signer import ProfileSigner
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.services.texture_service import TextureService
from domain.interfaces.services.token_service import TokenService
from infrastructure.config import settings
from infrastructure.services.code_generator import DigitCodeGenerator
from infrastructure.services.email_service import SMTPEmailService
from infrastructure.services.file_storage import S3FileStorage
from infrastructure.services.profile_signer import RSAProfileSigner
from infrastructure.services.string_hasher import BcryptStringHasher
from infrastructure.services.texture_service import PillowTextureService
from infrastructure.services.token_service import JWTTokenService


@lru_cache
def get_code_generator() -> CodeGenerator:
    return DigitCodeGenerator()


@lru_cache
def get_email_service() -> EmailService:
    return SMTPEmailService(
        host=settings.smtp.host,
        port=settings.smtp.port,
        username=settings.smtp.username,
        password=settings.smtp.password.get_secret_value(),
        from_email=str(settings.smtp.from_email),
        from_name=settings.smtp.from_name,
        use_tls=settings.smtp.use_tls,
    )


@lru_cache
def get_file_storage() -> FileStorage:
    return S3FileStorage(
        endpoint_url=str(settings.s3.endpoint_url),
        access_key=settings.s3.access_key,
        secret_key=settings.s3.secret_key.get_secret_value(),
        bucket=settings.s3.bucket,
        public_base_url=str(settings.s3.public_base_url),
        region_name=settings.s3.region,
    )


@lru_cache
def get_profile_signer() -> ProfileSigner:
    return RSAProfileSigner(private_key_pem=settings.rsa.private_key_pem.get_secret_value())


@lru_cache
def get_string_hasher() -> StringHasher:
    return BcryptStringHasher()


@lru_cache
def get_texture_service() -> TextureService:
    return PillowTextureService()


@lru_cache
def get_token_service() -> TokenService:
    return JWTTokenService(
        secret_key=settings.jwt.secret_key.get_secret_value(),
        algorithm=settings.jwt.algorithm,
    )


def get_auth_service(
    token_service: Annotated[TokenService, Depends(get_token_service)],
    string_hasher: Annotated[StringHasher, Depends(get_string_hasher)],
) -> AuthService:
    return AuthService(
        token_service=token_service,
        token_hasher=string_hasher,
    )


def get_minecraft_profile_service(
    profile_signer: Annotated[ProfileSigner, Depends(get_profile_signer)],
) -> MinecraftProfileService:
    return MinecraftProfileService(
        profile_signer=profile_signer,
    )
