"""Kaartdijin Boodja Catalogue Django Application Webhook Utilities."""


# Standard
import logging
import pathlib

# Third-Party
import httpx

# Typing
from typing import Any


# Logging
log = logging.getLogger(__name__)


def post_geojson(*webhooks: Any, geojson: pathlib.Path) -> None:
    """Posts a GeoJSON individually to many webhook URLs.

    Args:
        *webhook (Any): List of webhooks to post the GeoJSON to.
        geojson (pathlib.Path): GeoJSON filepath to post.
    """
    # Filter the supplied webhooks to only objects that have a `url`
    # attribute, and cast them to a set to eliminate any duplicates
    filtered_urls = set(w.url for w in webhooks if hasattr(w, "url"))

    # Log
    log.info(f"POSTing GeoJSON to: {filtered_urls}")

    # Read GeoJSON
    content = geojson.read_bytes()

    # Enter HTTP Client Context
    with httpx.Client() as client:
        # Loop through the URLs
        for url in filtered_urls:
            # Handle Errors
            try:
                # Log
                log.info(f"POSTing to: '{url}'")

                # POST the GeoJSON
                response = client.post(
                    url=url,
                    content=content,
                    headers={"Content-Type": "application/json"}
                )

            except Exception as exc:
                # Log
                log.error(f"POST failed: {exc}")

            else:
                # Check response
                if response.is_error:
                    # Log
                    log.error(f"POST failed: {response.status_code} - {response.text}")

                else:
                    # Log
                    log.info(f"POST successful: {response.status_code} - {response.text}")
