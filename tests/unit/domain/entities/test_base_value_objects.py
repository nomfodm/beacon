import pytest

from domain.entities.base import ContentLabel, MCAccessToken, MCServerID, Url
from domain.exceptions.base import ValidationError


def test_content_label_validation_success():
    value = ContentLabel("Title 123")
    assert str(value) == "Title 123"


def test_content_label_validation_fails():
    with pytest.raises(ValidationError):
        ContentLabel("ab")


def test_url_validation_success():
    value = Url("https://example.com/file.png")
    assert str(value) == "https://example.com/file.png"


def test_url_validation_fails():
    with pytest.raises(ValidationError):
        Url("bad-url")


def test_mc_access_token_length_validation():
    MCAccessToken("a" * 32)
    with pytest.raises(ValidationError):
        MCAccessToken("a" * 31)


def test_mc_server_id_length_validation():
    MCServerID("a" * 32)
    MCServerID("a" * 33)
    with pytest.raises(ValidationError):
        MCServerID("a" * 31)
