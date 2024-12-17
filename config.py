from dotenv import load_dotenv

import os

from logger import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    logger.error("`SECRET_KEY` environment variable must be set")
    exit(1)

PORT = int(os.getenv("PORT", 3000))
HOST = os.getenv("HOST", "127.0.0.1")

SEND_REAL_EMAILS = os.getenv("SEND_REAL_EMAILS") is not None
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

logger.debug(f"{SEND_REAL_EMAILS=}")

if SEND_REAL_EMAILS and (GMAIL_ADDRESS is None or GMAIL_PASSWORD is None):
    logger.error("SEND_REAL_EMAILS is set, but GMAIL_ADDRESS or GMAIL_PASSWORD is not set")
    exit(1)
