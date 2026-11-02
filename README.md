# telegram-referral-bot

Complete Telegram referral bot with required features:
- Force-join verification before bot access
- Referral and earn reward system
- Withdrawal request system with minimum ₹150
- User wallet, profile, and withdrawal history
- Admin panel with /admin, /addsudo, /broadcast
- Config-based menu builder and custom bot text
- Auto-accept join requests for configured channels
- SQLite database

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment values in `.env`:
   ```env
   BOT_TOKEN=your_bot_token_here
   ADMINS=123456789
   OWNER_ID=123456789
   REQUIRED_CHANNELS=-1001234567890,-1001234567891
   DB_PATH=data/telegram_referral_bot.db
   ```

3. Start the bot:
   ```bash
   python main.py
   ```

## Commands

- `/start` – start the bot and verify force-join
- `/admin` – admin control panel
- `/broadcast` – reply to a message and broadcast to all users
- `/addsudo <user_id>` – add sudo user
- `/removesudo <user_id>` – remove sudo access
- `/setchannel <chat_id> <invite_link>` – add required channel
- `/listchannels` – show configured channels
- `/menu add|remove|list|reset <label>` – menu builder
- `/withdraw <amount> <upi_id>` – send withdrawal request
- `/profile` – show user profile and history
- `/refer` – show referral link

## Notes

- The bot checks force-join channels before allowing usage.
- The channel invite links and IDs are configured via `/setchannel` or `.env`.
- The bot uses SQLite for data storage.
