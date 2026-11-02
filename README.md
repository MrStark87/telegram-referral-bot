# telegram-referral-bot

Complete Telegram referral bot with:
- Force-join verification before access
- Referral and earn link system
- Withdrawal manager with minimum ₹150
- User profile with earnings, referrals, and withdrawal history
- Admin panel with /admin, /broadcast, /addsudo, /removesudo
- Menu builder and editable text/settings
- Auto-join request approval support for required channels
- SQLite database backend

## Features

- Force join requirement using configured Telegram channels
- Auto-accept join requests when bot is a channel admin
- Referrer tracking via `start=ref_<user_id>` payload
- Referral reward of ₹20 per successful referral
- Wallet balance and pending/approved withdrawal history
- Command-based admin controls for moderation and broadcasts
- Editable bot messages and menu structure from JSON config

## Requirements

- Python 3.11+
- Telegram Bot Token
- A bot account that is admin in the target force-join channels

## Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your values
5. Run the bot:
   ```bash
   python main.py
   ```

## Environment variables

- `BOT_TOKEN`: Telegram bot token
- `ADMINS`: comma-separated admin user IDs
- `REQUIRED_CHANNELS`: comma-separated channel IDs like `-100111111,-100222222`
- `DB_PATH`: SQLite database path (optional, default: `data/telegram_referral_bot.db`)

## Admin commands

- `/admin`
- `/broadcast` (reply to a message with this command)
- `/addsudo <user_id>`
- `/removesudo <user_id>`
- `/setchannel <chat_id> <invite_link>`
- `/listchannels`
- `/setstartmsg`
- `/setforcejoinmsg`
- `/menu_builder`

## Example start link

`https://t.me/your_bot_username?start=ref_123456`

This gives the user a referrer ID and creates referral credit automatically when the user joins the bot.

## Notes

This repository is intentionally built as a production-ready starter project and is suitable for customization before deploying to a live Telegram bot account.
