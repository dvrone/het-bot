import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent

# Bot
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///het.db")

# Admins
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

OUTAGE_ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in os.getenv("OUTAGE_ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

GENERAL_ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in os.getenv("GENERAL_ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
