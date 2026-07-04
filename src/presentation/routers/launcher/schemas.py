from uuid import UUID

from pydantic import BaseModel

from domain.entities.launcher import Platform


class CheckUpdateRequest(BaseModel):
    platform: Platform
    version: str


class JoinServerRequest(BaseModel):
    accessToken: str
    selectedProfile: UUID
    serverId: str


class PublishReleaseRequest(BaseModel):
    version: str
    changelog: list[str]
    is_mandatory: bool = False


class AddReleaseAssetRequest(BaseModel):
    platform: Platform
    download_url: str
    checksum: str
    file_size: int


class LauncherSessionRequest(BaseModel):
    refresh_token: str


class LauncherLogoutFromOthersRequest(BaseModel):
    refresh_token: str
    password: str
