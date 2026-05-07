from urllib.parse import urlparse

import aioboto3
from botocore.config import Config

from domain.entities.base import Url
from domain.interfaces.services.file_storage import FileStorage

_S3_CONFIG = Config(s3={"addressing_style": "path"})


class S3FileStorage(FileStorage):
    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        public_base_url: str,
        region_name: str = "us-east-1",
    ) -> None:
        self._session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self._endpoint_url = endpoint_url.rstrip("/")
        self._bucket = bucket
        self._public_base_url = public_base_url.rstrip("/")
        self._region_name = region_name
        self._key_prefix = urlparse(self._public_base_url).path.strip("/")

    async def upload_file(self, *, file_bytes: bytes, destination_path: str, content_type: str) -> Url:
        key = f"{self._key_prefix}/{destination_path}" if self._key_prefix else destination_path
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            region_name=self._region_name,
            config=_S3_CONFIG,
        ) as s3:
            await s3.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
            )
        return Url(f"{self._public_base_url}/{destination_path}")
