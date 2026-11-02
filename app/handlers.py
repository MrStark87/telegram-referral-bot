import html
import json

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.config import Settings
from app.db import (
    add_channel,
    add_withdrawal,
    create_user,
    get_admin_ids,
    get_channels,
    get_menu_buttons,
    get_user,
    get_user_referrals,
    get_user_withdrawals,
    get_users,
    save_menu_buttons,
    set_sudo,
    set_user_withdrawn_amount,
)
from app.keyboards import (
    build_admin_menu,
    build_force_join_keyboard,
    build_main_menu,
    build_reply_menu,
)


async def is_admin(user_id: int) -> bool:
    user = get_user(user_id)
    if user and (user.get("is_sudo") == 1 or user.get("is_admin") == 1):
        return True
    if user_id in Settings.ADMINS or user_id == Settings.OWNER_ID:
        return True
    return user_id in get_admin_ids()


async def is_user_in_channel(bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status in {"creator", "administrator", "member"}:
            return True
        return False
    except Exception:
        return False


async def force_join_required(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    required = Settings.REQUIRED_CHANNELS
    if not required:
        return True

    user_id = update.effective_user.id
    bot = context.bot
    blocked_channels = []
    for channel_id in required:
        if not await is_user_in_channel(bot, channel_id, user_id):
            blocked_channels.append(channel_id)

    if blocked_channels:
        text = Settings.get("force_join_message", "Please join the required channels first.")
        channel_names = []
        for channel_id in blocked_channels:
            try:
                chat = await bot.get_chat(channel_id)
                invite = chat.invite_link or f"https://t.me/{chat.username}" if getattr(chat, "username", None) else f"https://t.me/{channel_id}"
                channel_names.append(f"• {chat.title}: {invite}")
            except Exception:
                channel_names.append(f"• Channel ID: {channel_id}")

        final_text = text.replace("{channels}", "\n".join(channel_names))
        await update.message.reply_text(final_text, reply_markup=build_force_join_keyboard())
        return False

    return True


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    payload = context.args[0] if context.args else ""
    referrer_id = None
    if payload.startswith("ref_"):
        try:
            referrer_id = int(payload.replace("ref_", ""))
        except ValueError:
            referrer_id = None

    create_user({
        "id": user.id,
        "first_name": user.first_name,
        "username": user.username,
    }, referrer_id=referrer_id)

    if not await force_join_required(update, context):
        return

    settings = Settings.load()
    text = settings.get("start_message", "Welcome! Choose an option below.")
    await update.message.reply_text(text, reply_markup=build_main_menu())


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized. Only approved admin/sudo IDs can use this command.")
        return

    help_text = (
        "🛠️ Admin Panel\n\n"
        "Available commands:\n"
        "• /broadcast - reply to a message with this command\n"
        "• /addsudo <user_id> - grant sudo access\n"
        "• /removesudo <user_id> - remove sudo\n"
        "• /setchannel <chat_id> <invite_link> - add required channel\n"
        "• /listchannels - list channels\n"
        "• /setstartmsg - set start message\n"
        "• /setforcejoinmsg - set force-join message\n"
        "• /menu add|remove|list <label> - configure menu\n"
        "• /admin - show this panel"
    )
    await update.message.reply_text(help_text, reply_markup=build_admin_menu())


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to the message you want to broadcast, then use /broadcast.")
        return

    source_message = update.message.reply_to_message
    source_chat = source_message.chat
    source_id = source_message.message_id

    users = get_users()
    broadcast_count = 0
    for user in users:
        try:
            await context.bot.forward_message(
                chat_id=user["id"],
                from_chat_id=source_chat.id,
                message_id=source_id,
            )
            broadcast_count += 1
        except Exception:
            try:
                await context.bot.send_message(
                    chat_id=user["id"],
                    text=f"📣 Broadcast\n\n{source_message.text or source_message.caption or 'Please check the latest update.'}",
                )
                broadcast_count += 1
            except Exception:
                continue

    await update.message.reply_text(f"✅ Broadcast sent to {broadcast_count} users.")


async def add_sudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /addsudo <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user id.")
        return

    user = get_user(target_id)
    if not user:
        await update.message.reply_text("User not found. Ask the user to start the bot first.")
        return

    set_sudo(target_id, 1)
    await update.message.reply_text(f"✅ User {target_id} added as sudo/admin.")


async def remove_sudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /removesudo <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user id.")
        return

    set_sudo(target_id, 0)
    await update.message.reply_text(f"✅ User {target_id} removed from sudo.")


async def set_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setchannel <chat_id> <invite_link>")
        return

    chat_id = context.args[0]
    invite_link = context.args[1]
    add_channel(chat_id, invite_link, 1)
    await update.message.reply_text(f"✅ Channel added: {chat_id}")


async def list_channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    channels = get_channels()
    if not channels:
        await update.message.reply_text("No channels configured yet.")
        return

    lines = ["📢 Required channels:"]
    for channel in channels:
        lines.append(f"• {channel['chat_id']} - {channel['invite_link']}")
    await update.message.reply_text("\n".join(lines))


async def set_start_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /setstartmsg <new message text>")
        return

    message = " ".join(context.args)
    Settings.set("start_message", message)
    await update.message.reply_text("✅ Start message updated.")


async def set_force_join_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /setforcejoinmsg <text with {channels} placeholder>")
        return

    message = " ".join(context.args)
    Settings.set("force_join_message", message)
    await update.message.reply_text("✅ Force-join message updated.")


async def menu_builder_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    text = (
        "🧩 Menu Builder\n\n"
        "Use:\n"
        "• /menu add <label>\n"
        "• /menu remove <label>\n"
        "• /menu list\n"
        "• /menu reset\n\n"
        "Example:\n"
        "/menu add Refer and Earn\n"
        "/menu add Withdrawal\n"
        "/menu add Profile"
    )
    await update.message.reply_text(text)


async def menu_update_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return

    if not context.args:
        await menu_builder_command(update, context)
        return

    action = context.args[0].lower()
    current = Settings.get("menu_buttons", [
        {"label": "Refer and Earn", "callback_data": "refer"},
        {"label": "Withdrawal", "callback_data": "withdraw"},
        {"label": "Profile", "callback_data": "profile"},
    ])

    if action == "add":
        label = " ".join(context.args[1:]).strip()
        if not label:
            await update.message.reply_text("Usage: /menu add <button label>")
            return
        if not any(item.get("label") == label for item in current):
            current.append({"label": label, "callback_data": f"menu_{len(current)}"})
            Settings.set("menu_buttons", current)
            await update.message.reply_text(f"✅ Added menu button: {label}")
            return
        await update.message.reply_text(f"Button already exists: {label}")
        return

    if action == "remove":
        label = " ".join(context.args[1:]).strip()
        if not label:
            await update.message.reply_text("Usage: /menu remove <button label>")
            return
        current = [item for item in current if item.get("label") != label]
        Settings.set("menu_buttons", current)
        await update.message.reply_text(f"✅ Removed menu button: {label}")
        return

    if action == "list":
        if not current:
            await update.message.reply_text("No custom menu buttons found.")
            return
        names = "\n".join(f"• {item.get('label')}" for item in current)
        await update.message.reply_text(f"📋 Current menu:\n{names}")
        return

    if action == "reset":
        default_buttons = [
            {"label": "Refer and Earn", "callback_data": "refer"},
            {"label": "Withdrawal", "callback_data": "withdraw"},
            {"label": "Profile", "callback_data": "profile"},
        ]
        Settings.set("menu_buttons", default_buttons)
        await update.message.reply_text("✅ Menu reset to default buttons.")
        return

    await menu_builder_command(update, context)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("User not found. Please start the bot first.")
        return

    referrals = get_user_referrals(user_id)
    withdrawals = get_user_withdrawals(user_id)
    history_text = "\n".join(
        f"• {item['amount']} INR | {item['status']} | {item['upi_id']} | {item['created_at']}"
        for item in withdrawals
    ) if withdrawals else "No withdrawal history yet."

    await update.message.reply_text(
        "👤 Profile\n\n"
        f"User ID: {user['id']}\n"
        f"Username: @{user['username'] or 'N/A'}\n"
        f"Referrals: {referrals}\n"
        f"Balance: ₹{user['balance']}\n"
        f"Earned: ₹{user['total_earned']}\n"
        f"Withdrawn: ₹{user['total_withdrawn']}\n\n"
        f"Withdrawal History:\n{history_text}",
        parse_mode=ParseMode.HTML,
    )


async def refer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("Please start the bot first.")
        return

    bot_username = context.bot.username
    if not bot_username:
        await update.message.reply_text("Bot username is not available. Use a public bot username to generate referral links.")
        return

    ref_link = f"https://t.me/{bot_username}?start=ref_{user['id']}"
    await update.message.reply_text(
        "🔗 Your referral link\n"
        f"{ref_link}\n\n"
        f"Every successful referral gives you ₹{Settings.get('referral_bonus', 20)}."
    )


async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("Please start the bot first.")
        return

    minimum = float(Settings.get('minimum_withdrawal', 150))
    if user['balance'] < minimum:
        await update.message.reply_text(f"Minimum withdrawal is ₹{minimum}. Your current balance is ₹{user['balance']}.")
        return

    if not context.args:
        await update.message.reply_text(
            "💸 Withdrawal\n\n"
            "Use this format:\n"
            "/withdraw 200 upi@upiid\n\n"
            f"Minimum withdrawal: ₹{minimum}"
        )
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /withdraw <amount> <upi_id>")
        return

    try:
        amount = float(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid amount.")
        return

    upi_id = context.args[1]
    if amount < minimum:
        await update.message.reply_text(f"Minimum withdrawal is ₹{minimum}.")
        return
    if user['balance'] < amount:
        await update.message.reply_text("You do not have enough balance for this withdrawal.")
        return

    add_withdrawal(user['id'], amount, upi_id)
    set_user_withdrawn_amount(user['id'], amount)
    await update.message.reply_text(
        f"✅ Withdrawal request sent successfully.\n\n"
        f"Amount: ₹{amount}\n"
        f"UPI: {upi_id}\n"
        f"Status: pending"
    )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data == "refer":
        await refer_command(update, context)
    elif data == "withdraw":
        await withdraw_command(update, context)
    elif data == "profile":
        await profile_command(update, context)
    elif data == "check_force_join":
        user_id = update.effective_user.id
        user = get_user(user_id)
        if not user:
            await query.edit_message_text("Please start the bot first.")
            return
        if await force_join_required(update, context):
            await query.edit_message_text("✅ Force-join check passed. You can use the bot now.")
            await update.effective_message.reply_text(
                Settings.get("start_message", "Welcome! Choose an option below."),
                reply_markup=build_main_menu(),
            )
    elif data == "admin_broadcast":
        await update.effective_message.reply_text("Reply to a message, then use /broadcast.")
    elif data == "admin_addsudo":
        await update.effective_message.reply_text("Usage: /addsudo <user_id>")
    elif data == "admin_channels":
        await list_channels_command(update, context)
    elif data == "admin_menu_builder":
        await menu_builder_command(update, context)
    else:
        await query.edit_message_text("Unknown action.")


async def handle_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = update.chat_join_request
    chat_id = request.chat.id
    user_id = request.from_user.id
    config_channels = get_channels()

    for channel in config_channels:
        if str(channel["chat_id"]) == str(chat_id):
            if channel.get("auto_accept") == 1:
                await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
            return


async def start_bot() -> None:
    from main import app
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()


__all__ = [
    "start_command",
    "admin_panel",
    "broadcast_command",
    "add_sudo_command",
    "remove_sudo_command",
    "set_channel_command",
    "list_channels_command",
    "set_start_message_command",
    "set_force_join_message_command",
    "menu_builder_command",
    "menu_update_command",
    "profile_command",
    "refer_command",
    "withdraw_command",
    "handle_callback_query",
    "handle_chat_join_request",
    "start_bot",
]
