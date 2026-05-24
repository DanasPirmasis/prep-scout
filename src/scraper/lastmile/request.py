import json

from oxylabs import RealtimeClient

from src.scraper import oxylabs
from src.scraper.exceptions import EmptyResponseError
from src.scraper.lastmile.types import (
    LastMileCategoriesResponse,
    LastMileProductsResponse,
)

IKI_CHAIN_ID = "CvKfTzV4TN5U8BTMF1Hl"
IKI_STORE_ID = "CvKfTzV4TN5U8BTMF1Hl_594"


def get_categories(client: RealtimeClient) -> LastMileCategoriesResponse:
    body = {
        "params": {
            "type": "categories",
            "show": True,
            "chainIds": [IKI_CHAIN_ID],
            "storeIds": [IKI_STORE_ID],
        },
        "isUsingCache": True,
        "slim": None,
    }

    raw_content = oxylabs.post_json(
        client,
        "https://searchservice-952707942140.europe-north1.run.app/categories",
        body,
    )

    if raw_content is None:
        raise EmptyResponseError("Empty response from LastMile categories endpoint.")
    return LastMileCategoriesResponse.model_validate(json.loads(raw_content))


def get_products_in_category(client: RealtimeClient, parent_id: str) -> LastMileProductsResponse:
    body = {
        "params": {
            "type": "view_products",
            "isActive": True,
            "isApproved": True,
            "chainIds": [IKI_CHAIN_ID],
            "categoryIds": [parent_id],
            "filter": {},
            "sort": "karma",
            "isUsingStock": True,
        },
        "limit": 3,  # This is intentional and does not limit anything
    }

    raw_content = oxylabs.post_json(
        client,
        "https://searchservice-952707942140.europe-north1.run.app/v1/frontend-products",
        body,
    )

    if raw_content is None:
        raise EmptyResponseError(f"Empty response for category {parent_id}.")
    return LastMileProductsResponse.model_validate(json.loads(raw_content))
