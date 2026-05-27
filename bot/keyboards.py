from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def model_selection_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "🟢 Gemini 2.5 Flash", callback_data="gemini-2.5-flash"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
