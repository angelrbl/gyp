import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

STORAGE_SECRET = os.getenv("STORAGE_SECRET")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_DB_PATH =f"sqlite:///{DATA_DIR / 'shelf.db'}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_PATH)