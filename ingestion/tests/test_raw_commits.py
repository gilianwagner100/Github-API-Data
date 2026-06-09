import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from ingestion.raw_commits import get_next_url, get_commit_data

MOCK_COMMIT_ITEM = {
    "sha": "abc123",
    "commit": {
        "author": {
            "date": "2024-01-01T00:00:00Z"
        }
    },
    "author": {
        "id": 12345,
        "login": "testuser"
    },
    "committer": {
        "id": 67890,
        "login": "testcommitter"
    }
}

MOCK_COMMIT_ITEM_NULL_AUTHOR = {
    "sha": "def456",
    "commit": {
        "author": {
            "date": "2024-01-01T00:00:00Z"
        }
    },
    "author": None,
    "committer": None
}


def make_response(status_code, headers=None, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.headers = headers or {}
    mock.json.return_value = json_data or []
    return mock


# get_next_url tests
def test_get_next_url_returns_next():
    header = '<https://api.github.com/repos/x/y/commits?page=2>; rel="next", <https://api.github.com/repos/x/y/commits?page=40>; rel="last"'
    result = get_next_url(header)
    assert result == "https://api.github.com/repos/x/y/commits?page=2"


def test_get_next_url_returns_none_on_last_page():
    header = '<https://api.github.com/repos/x/y/commits?page=40>; rel="last"'
    result = get_next_url(header)
    assert result is None


def test_get_next_url_returns_none_when_no_header():
    result = get_next_url(None)
    assert result is None


# get_commit_data tests
def test_get_commit_data_successful_response():
    """Happy path — returns a list of CommitRecord objects."""
    mock_200 = make_response(200, json_data=[MOCK_COMMIT_ITEM])

    with patch("ingestion.github_client.requests.get", return_value=mock_200):
        result = get_commit_data("AutoViML/AutoViz", repo_id=197432079)

    assert len(result) == 1
    assert result[0].sha == "abc123"
    assert result[0].author_login == "testuser"
    assert result[0].repo_id == 197432079


def test_get_commit_data_null_author():
    """Null author and committer — nullable fields are None without raising."""
    mock_200 = make_response(200, json_data=[MOCK_COMMIT_ITEM_NULL_AUTHOR])

    with patch("ingestion.github_client.requests.get", return_value=mock_200):
        result = get_commit_data("AutoViML/AutoViz", repo_id=197432079)

    assert len(result) == 1
    assert result[0].author_id is None
    assert result[0].author_login is None
    assert result[0].committer_id is None
    assert result[0].committer_login is None


def test_get_commit_data_since_passed_as_param():
    """since parameter is passed to the API as a query param."""
    mock_200 = make_response(200, json_data=[MOCK_COMMIT_ITEM])
    since = datetime(2024, 1, 1, tzinfo=timezone.utc)

    with patch("ingestion.github_client.requests.get", return_value=mock_200) as mock_get:
        get_commit_data("AutoViML/AutoViz", repo_id=197432079, since=since)

    call_kwargs = mock_get.call_args
    assert "since" in call_kwargs.kwargs.get("params", {}) or \
           "since" in (call_kwargs.args[1] if len(call_kwargs.args) > 1 else {})


def test_get_commit_data_none_response_returns_empty():
    """None response from make_request — returns empty list without raising."""
    with patch("ingestion.raw_commits.make_request", return_value=None):
        result = get_commit_data("AutoViML/AutoViz", repo_id=197432079)

    assert result == []