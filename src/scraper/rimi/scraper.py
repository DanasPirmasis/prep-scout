import logging
from concurrent.futures import ThreadPoolExecutor

from oxylabs import RealtimeClient
from sqlmodel import Session

from src.scraper.rimi import request, save

logger = logging.getLogger(__name__)

FIRST_PAGE = 0


def scrape_rimi(session: Session, client: RealtimeClient) -> None:
    categories = request.get_categories(client)
    save.categories(session, categories)

    # RIMI allows to fetch all of their products by hitting
    # their search endpoint and then just iterating through all of the pages

    firstPage = request.get_products_in_page(client, FIRST_PAGE)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(request.get_products_in_page, client, i) for i in range(firstPage.totalPages)]
    for future in futures:
        future.result()
