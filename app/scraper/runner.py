import logging

from app.scraper.lastmile.scraper import scrape_lastmile
from app.session import session_scope

logger = logging.getLogger(__name__)


def run_scraper() -> None:
    logger.info("Starting scraping run")
    with session_scope() as session:
        scrape_lastmile(session)
    logger.info("Scraping complete.")
