from typing import Annotated

from pydantic import AnyHttpUrl, EmailStr, Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    url: PostgresDsn


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: Annotated[int, Field(ge=1, le=65535)] = 6379
    db: Annotated[int, Field(ge=0, le=15)] = 0


class JWTSettings(BaseSettings):
    secret_key: SecretStr
    algorithm: str = "HS256"


class S3Settings(BaseSettings):
    endpoint_url: AnyHttpUrl
    access_key: str
    secret_key: SecretStr
    bucket: str
    public_base_url: AnyHttpUrl
    region: str = "us-east-1"


class SMTPSettings(BaseSettings):
    host: str
    port: Annotated[int, Field(ge=1, le=65535)] = 587
    username: str
    password: SecretStr
    from_email: EmailStr
    from_name: str = "Infinity Minecraft Server"
    use_tls: bool = True


class RSASettings(BaseSettings):
    private_key_pem: SecretStr


class SecretsSettings(BaseSettings):
    ci_token: SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    s3: S3Settings = Field(default_factory=S3Settings)
    smtp: SMTPSettings = Field(default_factory=SMTPSettings)
    rsa: RSASettings = Field(default_factory=RSASettings)
    secrets: SecretsSettings = Field(default_factory=SecretsSettings)


settings = Settings()
