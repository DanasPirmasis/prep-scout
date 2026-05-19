# from apscheduler.schedulers.blocking import BlockingScheduler

from app.scraper.runner import run_scraper


def main():
    run_scraper()
    # scheduler = BlockingScheduler()
    # scheduler.add_job(run_scraper, "cron", hour=2)
    # scheduler.start()


if __name__ == "__main__":
    main()
