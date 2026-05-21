import logging
from collections import deque
from collections.abc import Callable
from contextlib import AbstractContextManager

from oxylabs import RealtimeClient
from sqlmodel import Session

from app.scraper.lastmile import request, save
from app.scraper.lastmile.types import LastMileCategoriesResponse

logger = logging.getLogger(__name__)


SessionFactory = Callable[[], AbstractContextManager[Session]]


def scrape_lastmile(session_factory: SessionFactory, client: RealtimeClient) -> None:
    categories = request.get_categories(client)
    category_tree = _build_category_tree(categories)

    with session_factory() as session:
        save.categories(session, categories)

    total_categories = len(category_tree)
    if total_categories == 0:
        return
    scraped_categories = 0

    for parent_id in category_tree:
        # TODO: this should execute all of the requests at the same time.
        products_response = request.get_products_in_category(client, parent_id)
        for entry in products_response.products:
            product = entry.front_end_product
            with session_factory() as session:
                save.last_mile_product(session, product)
                save.product(session, product)
        scraped_categories += 1
        _log_completeness(scraped_categories, total_categories)


def _log_completeness(scraped_categories: int, total_categories: int):
    completeness = (scraped_categories / total_categories) * 100

    logger.info(
        "Scraped %d/%d categories (%.1f%%)",
        scraped_categories,
        total_categories,
        completeness,
    )


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
