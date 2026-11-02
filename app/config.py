import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SETTINGS_PATH = DATA_DIR / "settings.json"


def ensure_settings_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not SETTINGS_PATH.exists():
        default_settings = {
            "start_message": "Welcome!\n\nYour bot is ready.\n\nChoose an option below.",
            "force_join_message": "Please join the required channels first before using the bot.\n\n{channels}\n\nAfter joining, press /start again.",
            "main_menu": [
                "Refer and Earn",
                "Withdrawal",
                "Profile"
            ],
            "referral_bonus": 20,
            "minimum_withdrawal": 150,
            "admin_only": True,
            "broadcast_prefix": "[Broadcast]"
        }
        SETTINGS_PATH.write_text(json.dumps(default_settings, indent=2), encoding="utf-8")


ensure_settings_file()


class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    ADMINS = {int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()}
    REQUIRED_CHANNELS = [
        int(x.strip()) for x in os.getenv("REQUIRED_CHANNELS", "").split(",") if x.strip()
    ]
    DB_PATH = os.getenv("DB_PATH", str(ROOT_DIR / "data" / "telegram_referral_bot.db"))

    @staticmethod
    def load() -> dict[str, Any]:
        ensure_settings_file()
        with SETTINGS_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        return Settings.load().get(key, default)
