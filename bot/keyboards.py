from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def model_selection_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "🟢 Gemini 2.5 Flash", callback_data="gemini-2.5-flash"
            ),
        ],
        [
            InlineKeyboardButton("⚡ Groq Llama", callback_data="groq-llama"),
        ],
        # [
        #     InlineKeyboardButton("🔵 Groq Mixtral", callback_data="groq-mixtral"),
        # ],
    ]
    return InlineKeyboardMarkup(keyboard)
