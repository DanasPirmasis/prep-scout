import logging

from dotenv import load_dotenv

load_dotenv()


from src.scraper.runner import run_scraper  # noqa: E402


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run_scraper()


if __name__ == "__main__":
    main()
