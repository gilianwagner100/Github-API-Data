import pytest
from unittest.mock import patch, MagicMock
from ingestion.raw_repositories import get_repository_data

def make_response(status_code, headers=None, json_data=None):
    "Helper to make response to avoid repeated response for every test"
    mock = MagicMock()
    mock.status_code = status_code
    mock.headers = headers or {}
    mock.json.return_value = json_data or {}
    return mock

def test_successful_response():
    "Test successful 200 response"
    mock_200 = make_response(200, json_data={"full_name": "pytorch/pytorch"})

    with patch("ingestion.raw_repositories.requests.get", return_value = mock_200):
        result = get_repository_data("pytorch/pytorch")
    
    assert result["full_name"] == "pytorch/pytorch"

def test_403_retry_after_response():
    "Test behavior with 403 response and 'retry-after' header — sleeps for the specified duration then retries."
    mock_403 = make_response(403, headers = {"retry-after": "30", "x-ratelimit-remaining": "10"})
    mock_200 = make_response(200, json_data={"full_name": "pytorch/pytorch"})

    with patch("ingestion.raw_repositories.requests.get", side_effect=[mock_403, mock_200]):
        with patch("time.sleep") as mock_sleep:
            result = get_repository_data("pytorch/pytorch")

    mock_sleep.assert_called_once_with(30)
    assert result["full_name"] == "pytorch/pytorch"
    

def test_403_ratelimit_reset():
    "Test behavior with 403 response and 'ratelimit-reset' header - sleeps until reset timestamp"
    reset_timestamp = 9999999999  # far future so sleep_for is always positive
    mock_403 = make_response(403, headers = {
        "x-ratelimit-remaining": "0",
        "x-ratelimit-reset": str(reset_timestamp)
    })
    mock_200 = make_response(200, json_data={"full_name": "pytorch/pytorch"})

    with patch("ingestion.raw_repositories.requests.get", side_effect=[mock_403, mock_200]):
        with patch("time.sleep") as mock_sleep:
            with patch("time.time", return_value=0):  # fixes time so sleep_for is predictable
                result = get_repository_data("pytorch/pytorch")

    mock_sleep.assert_called_once_with(reset_timestamp)
    assert result["full_name"] == "pytorch/pytorch"

def test_max_retries_exceeded():
    "Test behavior with secondary rate limit exceeded"
    mock_403 = make_response(403, headers={"x-ratelimit-remaining": "10"})

    with patch("ingestion.raw_repositories.requests.get", return_value=mock_403):
        with patch("time.sleep"):
            with pytest.raises(Exception, match="max retries"):
                get_repository_data("pytorch/pytorch", max_retries=3)