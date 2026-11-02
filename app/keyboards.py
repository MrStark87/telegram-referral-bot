from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def build_main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("Refer and Earn", callback_data="refer"),
            InlineKeyboardButton("Withdrawal", callback_data="withdraw"),
        ],
        [InlineKeyboardButton("Profile", callback_data="profile")],
    ]
    return InlineKeyboardMarkup(buttons)


def build_reply_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [["Refer and Earn", "Withdrawal"], ["Profile"]],
        resize_keyboard=True,
    )


def build_admin_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("Add Sudo", callback_data="admin_addsudo")],
        [InlineKeyboardButton("Channels", callback_data="admin_channels")],
        [InlineKeyboardButton("Menu Builder", callback_data="admin_menu_builder")],
    ]
    return InlineKeyboardMarkup(buttons)


def build_force_join_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Check Again", callback_data="check_force_join")]]
    )
