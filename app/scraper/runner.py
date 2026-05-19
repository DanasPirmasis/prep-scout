from app.scraper.last_mile import init_last_mile


def run_scraper():
    print("Starting scraping run")
    init_last_mile()
    print("Scraping complete.")
