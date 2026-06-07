import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from ingestion.raw_star_history import get_next_url, get_star_data

MOCK_STAR_ITEM = {
    "starred_at": "2024-01-01T00:00:00Z",
    "user": {
        "id": 12345,
        "login": "testuser"
    }
}


def make_response(status_code, headers=None, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.headers = headers or {}
    mock.json.return_value = json_data or []
    return mock


# get_next_url tests
def test_get_next_url_returns_next():
    header = '<https://api.github.com/repos/x/y/stargazers?page=2>; rel="next", <https://api.github.com/repos/x/y/stargazers?page=40>; rel="last"'
    result = get_next_url(header)
    assert result == "https://api.github.com/repos/x/y/stargazers?page=2"

def test_get_next_url_returns_none_on_last_page():
    header = '<https://api.github.com/repos/x/y/stargazers?page=40>; rel="last"'
    result = get_next_url(header)
    assert result is None

def test_get_next_url_returns_none_when_no_header():
    result = get_next_url(None)
    assert result is None


# get_star_data tests
def test_get_star_data_successful_response():
    """Happy path — returns a list of StarRecord objects."""
    mock_200 = make_response(200, json_data=[MOCK_STAR_ITEM])

    with patch("ingestion.github_client.requests.get", return_value=mock_200):
        result = get_star_data("pytorch/pytorch", repo_id=65600975)

    assert len(result) == 1
    assert result[0].repo_full_name == "pytorch/pytorch"
    assert result[0].user_login == "testuser"


def test_get_star_data_stops_at_since():
    """since parameter — stops fetching when starred_at <= since."""
    mock_200 = make_response(200, json_data=[MOCK_STAR_ITEM])
    since = datetime(2025, 1, 1, tzinfo=timezone.utc)  # newer than the mock item

    with patch("ingestion.github_client.requests.get", return_value=mock_200):
        result = get_star_data("pytorch/pytorch", repo_id=65600975, since=since)

    assert len(result) == 0


def test_get_star_data_422_returns_empty():
    """422 response — make_request returns None, get_star_data returns empty list."""
    with patch("ingestion.raw_star_history.make_request", return_value=None):
        result = get_star_data("pytorch/pytorch", repo_id=65600975)

    assert result == []


def test_get_star_data_none_response_returns_empty():
    """None response from make_request — returns empty list without raising."""
    with patch("ingestion.raw_star_history.make_request", return_value=None):
        result = get_star_data("pytorch/pytorch", repo_id=65600975)

    assert result == []