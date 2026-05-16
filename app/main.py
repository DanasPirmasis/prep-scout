import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scraper.runner import run_scraper


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_scraper, "cron", hour=2)
    scheduler.start()
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
