from dotenv import load_dotenv
import os
from pathlib import Path
import json

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SETTINGS_PATH = DATA_DIR / "settings.json"


def ensure_settings_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not SETTINGS_PATH.exists():
        default_settings = {
            "start_message": "Welcome!\n\nThanks for joining.\n\nChoose an option below.",
            "force_join_message": "Please join the required channels first to unlock the bot.\n\n{channels}\n\nAfter joining, click the button below to verify.",
            "main_menu": [
                "Refer and Earn",
                "Withdrawal",
                "Profile"
            ],
            "referral_bonus": 20,
            "minimum_withdrawal": 150,
            "admin_only": True,
            "broadcast_prefix": "[Broadcast]",
            "menu_buttons": [
                {"label": "Refer and Earn", "callback_data": "refer"},
                {"label": "Withdrawal", "callback_data": "withdraw"},
                {"label": "Profile", "callback_data": "profile"}
            ]
        }
        SETTINGS_PATH.write_text(json.dumps(default_settings, indent=2), encoding="utf-8")


ensure_settings_file()


class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    ADMINS = {int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()}
    OWNER_ID = int(os.getenv("OWNER_ID", "0") or 0)
    REQUIRED_CHANNELS = [
        int(x.strip())
        for x in os.getenv("REQUIRED_CHANNELS", "").split(",")
        if x.strip()
    ]
    DB_PATH = os.getenv("DB_PATH", str(ROOT_DIR / "data" / "telegram_referral_bot.db"))

    @staticmethod
    def load() -> dict:
        ensure_settings_file()
        try:
            with SETTINGS_PATH.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def save(data: dict) -> None:
        ensure_settings_file()
        with SETTINGS_PATH.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    @staticmethod
    def get(key: str, default=None):
        return Settings.load().get(key, default)

    @staticmethod
    def set(key: str, value):
        data = Settings.load()
        data[key] = value
        Settings.save(data)
