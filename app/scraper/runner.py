import logging
import os

from oxylabs import RealtimeClient

from app.scraper.exceptions import MissingCredentialsError
from app.scraper.lastmile.scraper import scrape_lastmile
from app.session import session_scope

logger = logging.getLogger(__name__)


def run_scraper() -> None:
    logger.info("Starting scraping run")

    username = os.getenv("OXYLABS_USERNAME")
    password = os.getenv("OXYLABS_PASSWORD")
    if username is None or password is None:
        raise MissingCredentialsError("OxyLabs credentials not found in environment variables.")
    client = RealtimeClient(username, password)

    scrape_lastmile(session_scope, client)
    logger.info("Scraping complete.")
