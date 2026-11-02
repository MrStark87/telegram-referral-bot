from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    CommandHandler,
)

from app.config import Settings
from app.db import init_db
from app.handlers import (
    add_sudo_command,
    admin_panel,
    broadcast_command,
    handle_callback_query,
    handle_chat_join_request,
    list_channels_command,
    menu_builder_command,
    menu_update_command,
    profile_command,
    refer_command,
    remove_sudo_command,
    set_channel_command,
    set_force_join_message_command,
    set_start_message_command,
    start_command,
    withdraw_command,
)


def build_app():
    init_db()
    app = ApplicationBuilder().token(Settings.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("addsudo", add_sudo_command))
    app.add_handler(CommandHandler("removesudo", remove_sudo_command))
    app.add_handler(CommandHandler("setchannel", set_channel_command))
    app.add_handler(CommandHandler("listchannels", list_channels_command))
    app.add_handler(CommandHandler("setstartmsg", set_start_message_command))
    app.add_handler(CommandHandler("setforcejoinmsg", set_force_join_message_command))
    app.add_handler(CommandHandler("menu", menu_update_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("refer", refer_command))
    app.add_handler(CommandHandler("withdraw", withdraw_command))

    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(ChatJoinRequestHandler(handle_chat_join_request))
    return app


app = build_app()


if __name__ == "__main__":
    print("Starting bot...")
    app.run_polling()
