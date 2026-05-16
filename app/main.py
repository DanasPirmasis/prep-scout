from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.scraper.runner import run_scraper

app = FastAPI()


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(run_scraper, "cron", hour=2)
    scheduler.start()
    yield
    scheduler.shutdown()  # cleanup on shutdown


@app.get("/")
async def read_root():
    return {"message": "Hello World"}
