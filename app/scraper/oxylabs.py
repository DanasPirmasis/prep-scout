import base64
import json
from typing import Any

from oxylabs import RealtimeClient

from app.scraper.exceptions import EmptyResponseError


def post_json(client: RealtimeClient, url: str, body: dict[str, Any]) -> str | None:
    response = client.universal.scrape_url(
        url=url,
        user_agent_type="desktop_chrome",
        geo_location="Lithuania",
        context=[
            {"key": "http_method", "value": "post"},
            {
                "key": "content",
                "value": base64.b64encode(json.dumps(body).encode()).decode(),
            },
            {"key": "force_headers", "value": True},
            {"key": "headers", "value": {"Content-Type": "application/json"}},
        ],
    )
    if len(response.results) == 0:
        raise EmptyResponseError(f"Empty response from OxyLabs for {url}.")

    return response.results[0].content
