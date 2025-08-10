import pytest
from unittest.mock import patch, MagicMock
from src.util.helpers import Helpers

@patch("src.util.helpers.requests.get")
def test_parse_robots_txt_basic(mock_get):
    mock_response = MagicMock()
    mock_response.text = """
    User-agent: *
    Allow: /public
    Disallow: /private
    """
    mock_get.return_value = mock_response

    allow, disallow = Helpers.parse_robots_txt("http://example.com")
    assert "/public" in allow
    assert "/private" in disallow

def test_normalize_url_absolute():
    url = "http://example.com/page"
    current_url = "http://example.com"
    result = Helpers.normalize_url(url, current_url)
    assert result == "http://example.com/page"

def test_normalize_url_relative():
    url = "/about"
    current_url = "http://example.com/home"
    result = Helpers.normalize_url(url, current_url)
    assert result == "http://example.com/about"

def test_normalize_url_with_query():
    url = "/search?q=test"
    current_url = "http://example.com"
    result = Helpers.normalize_url(url, current_url)
    assert result == "http://example.com/search?q=test"
