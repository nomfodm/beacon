import pytest

from infrastructure.services.file_storage import S3FileStorage


@pytest.fixture
def storage(mocker) -> S3FileStorage:
    mocker.patch("infrastructure.services.file_storage.aioboto3.Session")
    return S3FileStorage(
        endpoint_url="https://s3.example.com",
        access_key="key",
        secret_key="secret",
        bucket="textures",
        public_base_url="https://cdn.example.com",
    )


@pytest.mark.asyncio
async def test_upload_file_calls_put_object(storage: S3FileStorage, mocker):
    mock_s3 = mocker.AsyncMock()
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_s3
    mock_client.__aexit__.return_value = None
    storage._session.client.return_value = mock_client

    await storage.upload_file(
        file_bytes=b"image-data",
        destination_path="skins/abc.png",
        content_type="image/png",
    )

    mock_s3.put_object.assert_awaited_once_with(
        Bucket="textures",
        Key="skins/abc.png",
        Body=b"image-data",
        ContentType="image/png",
    )


@pytest.mark.asyncio
async def test_upload_file_returns_public_url(storage: S3FileStorage, mocker):
    mock_s3 = mocker.AsyncMock()
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_s3
    mock_client.__aexit__.return_value = None
    storage._session.client.return_value = mock_client

    result = await storage.upload_file(
        file_bytes=b"data",
        destination_path="capes/xyz.png",
        content_type="image/png",
    )

    assert result.value == "https://cdn.example.com/capes/xyz.png"


@pytest.mark.asyncio
async def test_upload_file_strips_trailing_slash_from_base_url(mocker):
    mocker.patch("infrastructure.services.file_storage.aioboto3.Session")
    storage = S3FileStorage(
        endpoint_url="https://s3.example.com",
        access_key="key",
        secret_key="secret",
        bucket="textures",
        public_base_url="https://cdn.example.com/",
    )
    mock_s3 = mocker.AsyncMock()
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_s3
    mock_client.__aexit__.return_value = None
    storage._session.client.return_value = mock_client

    result = await storage.upload_file(file_bytes=b"d", destination_path="a/b.png", content_type="image/png")

    assert result.value == "https://cdn.example.com/a/b.png"


@pytest.mark.asyncio
async def test_upload_file_uses_correct_endpoint(storage: S3FileStorage, mocker):
    mock_s3 = mocker.AsyncMock()
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_s3
    mock_client.__aexit__.return_value = None
    storage._session.client.return_value = mock_client

    await storage.upload_file(file_bytes=b"d", destination_path="x.png", content_type="image/png")

    storage._session.client.assert_called_once_with(
        "s3",
        endpoint_url="https://s3.example.com",
        region_name="us-east-1",
        config=mocker.ANY,
    )
