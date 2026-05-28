import logging
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

from oxylabs import RealtimeClient
from sqlmodel import Session

from src.scraper.lastmile import request, save
from src.scraper.lastmile.types import LastMileCategoriesResponse, LastMileProductsResponse

logger = logging.getLogger(__name__)


def scrape_lastmile(session: Session, client: RealtimeClient) -> None:
    categories = request.get_categories(client)
    category_tree = _build_category_tree(categories)

    save.categories(session, categories)

    total_categories = len(category_tree)
    if total_categories == 0:
        return

    with ThreadPoolExecutor(max_workers=2) as executor:
        products_by_category = {
            executor.submit(request.get_products_in_category, client, parent_id): parent_id
            for parent_id in category_tree
        }
        for scraped_categories, future in enumerate(as_completed(products_by_category), start=1):
            parent_id = products_by_category[future]
            try:
                products_response = future.result()
            except Exception:
                logger.exception("Failed to scrape LastMile category %s", parent_id)
                _log_completeness(scraped_categories, total_categories)
                continue

            _save_products(session, products_response)
            logger.info("Scraped LastMile category %s", parent_id)
            _log_completeness(scraped_categories, total_categories)


def _save_products(session: Session, products_response: LastMileProductsResponse) -> None:
    for entry in products_response.products:
        product = entry.front_end_product
        save.last_mile_product(session, product)
        save.product(session, product)


def _build_category_tree(data: LastMileCategoriesResponse) -> dict[str, list[str]]:
    """
    Builds a flat tree mapping each top-level category ID to all of its descendant IDs.
    Top-level categories are identified by globalCategoryParentId == "0".
    Descendants are collected via BFS using parentId relationships.
    """
    children_by_parent_id: dict[str, list[str]] = {}
    for category in data.data:
        children_by_parent_id.setdefault(category.parent_id, []).append(category.id)

    top_level_categories = [c for c in data.data if c.global_category_parent_id == "0"]

    category_tree: dict[str, list[str]] = {}
    for top_level_category in top_level_categories:
        all_descendant_ids: list[str] = []
        bfs_queue: deque[str] = deque([top_level_category.id])
        while bfs_queue:
            current_category_id = bfs_queue.popleft()
            direct_children_ids = children_by_parent_id.get(current_category_id, [])
            all_descendant_ids.extend(direct_children_ids)
            bfs_queue.extend(direct_children_ids)
        category_tree[top_level_category.id] = all_descendant_ids

    return category_tree


def _log_completeness(scraped_categories: int, total_categories: int) -> None:
    completeness = (scraped_categories / total_categories) * 100

    logger.info(
        "Scraped %d/%d categories (%.1f%%)",
        scraped_categories,
        total_categories,
        completeness,
    )
