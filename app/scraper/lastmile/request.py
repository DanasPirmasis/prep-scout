import base64
import json

from oxylabs import RealtimeClient

from app.scraper.lastmile.types import (
    LastMileCategoriesResponse,
    LastMileProductsResponse,
)


def get_categories(client: RealtimeClient) -> LastMileCategoriesResponse:
    body = {
        "params": {
            "type": "categories",
            "show": True,
            "chainIds": ["CvKfTzV4TN5U8BTMF1Hl"],
            "storeIds": ["CvKfTzV4TN5U8BTMF1Hl_594"],
        },
        "isUsingCache": True,
        "slim": None,
    }

    response = client.universal.scrape_url(
        url="https://searchservice-952707942140.europe-north1.run.app/categories",
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

    raw_content = response.results[0].content
    if raw_content is None:
        raise ValueError("Empty response from LastMile categories endpoint.")
    return LastMileCategoriesResponse.model_validate(json.loads(raw_content))


IKI_STORE_ID = "CvKfTzV4TN5U8BTMF1Hl"


def get_products_in_category(
    client: RealtimeClient, parent_id: str
) -> LastMileProductsResponse:
    body = {
        "params": {
            "type": "view_products",
            "isActive": True,
            "isApproved": True,
            "chainIds": [IKI_STORE_ID],
            "categoryIds": [parent_id],
            "filter": {},
            "sort": "karma",
            "isUsingStock": True,
        },
        "limit": 3,  # This is intentional and does not limit anything
    }

    response = client.universal.scrape_url(
        url="https://searchservice-952707942140.europe-north1.run.app/v1/frontend-products",
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

    raw_content = response.results[0].content
    if raw_content is None:
        raise ValueError(f"Empty response for category {parent_id}.")
    return LastMileProductsResponse.model_validate(json.loads(raw_content))
