import logging

from dotenv import load_dotenv

load_dotenv()

# from apscheduler.schedulers.blocking import BlockingScheduler

from app.scraper.runner import run_scraper  # noqa: E402


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run_scraper()
    # scheduler = BlockingScheduler()
    # scheduler.add_job(run_scraper, "cron", hour=2)
    # scheduler.start()


if __name__ == "__main__":
    main()
