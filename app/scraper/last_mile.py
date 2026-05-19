import base64
import json
import os

from dotenv import load_dotenv
from oxylabs import RealtimeClient

load_dotenv()

username = os.getenv("OXYLABS_USERNAME")
password = os.getenv("OXYLABS_PASSWORD")


def init_last_mile():
    ## TODO: Start by fetching the lastmile categories endpoint.
    # This will give the latest list of categories.
    # Use the returned data and write it into database
    #
    # Then, fetch all the products in each category and update the local database with this information.
    # Finally, return a success message indicating that the last mile has been initialized successfully.

    if username is None or password is None:
        raise Exception("OxyLabs credentials not found in environment variables.")

    client = RealtimeClient(username, password)
    get_categories(client)
    pass


def get_categories(client: RealtimeClient):
    ## TODO: This function should fetch the categories endpoint.
    # Traverse the returned JSON to build an accurate tree of categories.
    # Because the returned data object has both parents and children in it.
    # A category can have its own parent and children
    #
    # Top level parent is denoted by "globalCategoryParentId": "0"
    # The returned object from this function should be a dictionary whose keys are top level parents and all the categories under them.
    # Example:
    # {
    #     "pSp7CyeVom1sAZvZc7EI": [
    #         "P7xyuwbRtRE5FVFe1xr8",
    #         "Gl7ZGnHk3b4dlw5nP2XE",
    #         "jKUM60P3woQgmfwI7EdR",
    #         "vDZoX4YoRHKJp2fiFp0d",
    #         "WcAZLXz93Js0Jti4IRo7",
    #         "lK7sODURO01CWsoaBEVe",
    #         "dXm2I2xsSMKPb34maRSX",
    #         "r6e4ozyqi48AyYVh6yPW",
    #         "Fjr0PdY3SpHbc2GKm9Cd",
    #     ],
    #     ...
    # }
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

    categories = client.universal.scrape_url(
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
    print(categories.raw)


def get_products_in_category(children_ids: list[str]):
    ## TODO: This function should fetch all products that belong to the provided parent.
    # The returned object from this function should be a list of Product objects.
    # Also we should write into database the products and their details
    pass
