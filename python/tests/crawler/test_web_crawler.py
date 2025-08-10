from unittest.mock import AsyncMock, patch

import pytest

from src.crawler.web_crawler import WebCrawler


@pytest.mark.asyncio
@patch("src.crawler.web_crawler.Helpers")
@patch("src.crawler.web_crawler.aiohttp.ClientSession")
async def test_crawl_basic(mock_session_cls, mock_helpers):
    # Mock robots.txt parsing
    mock_helpers.parse_robots_txt.return_value = (set(), set())
    # Mock session and response
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = AsyncMock(return_value="<html><a href='http://test.com/page/'>link</a></html>")
    mock_session.get.return_value.__aenter__.return_value = mock_response
    mock_session_cls.return_value.__aenter__.return_value = mock_session

    crawler = WebCrawler("http://test.com")
    crawler.is_same_domain = lambda url: True  # Simplify for test

    await crawler.crawl()

    # Check that the base URL was visited
    assert "http://test.com" in crawler.visited
    # Check that the link was added to visited (after processing)
    assert "http://test.com/page" in crawler.visited or "http://test.com/page" in crawler.queue._queue