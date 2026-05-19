from app.scraper.lastmile.scraper import scrape_lastmile
from app.session import get_session


def run_scraper():
    print("Starting scraping run")
    session = next(get_session())
    scrape_lastmile(session)
    print("Scraping complete.")
