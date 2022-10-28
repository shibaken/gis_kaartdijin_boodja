"""Provides unit tests for the DBCA middleware module."""


# Third-Party
from django import http
import pytest

# Local
from govapp import middleware

# Typing
from typing import Optional


@pytest.mark.parametrize(
    (
        "path",
        "result",
    ),
    [
        ("/api/something", "private, no-store"),
        ("/static/something", "public, max-age=86400"),
        ("/media/something", "public, max-age=86400"),
        ("/fake/something", None),
        ("", None),
    ]
)
def test_middleware_cache(path: str, result: Optional[str]) -> None:
    """Tests that the cache middleware works correctly for endpoints.

    Args:
        path (str): Path to test.
        result (Optional[str]): Expected result.
    """
    # Create middleware with mock `get_response` function
    cache = middleware.CacheControl(lambda r: http.HttpResponse())

    # Create mock request
    request = http.HttpRequest()
    request.path = path

    # Test caching
    assert cache(request).get("Cache-Control") == result
