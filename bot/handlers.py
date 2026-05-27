from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import model_selection_keyboard
from agent.agent import get_agent

# Guardamos el modelo elegido por cada usuario
user_models = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente IA.\n\nPrimero elegí el modelo que querés usar:",
        reply_markup=model_selection_keyboard()
    )

async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    model = query.data  # "gemini-1.5-flash", "groq-llama" o "groq-mixtral"

    user_models[user_id] = model

    model_names = {
        "gemini-1.5-flash": "🟢 Gemini 1.5 Flash",
        "groq-llama": "⚡ Groq Llama",
        "groq-mixtral": "🔵 Groq Mixtral",
    }

    await query.edit_message_text(
        f"Perfecto, usando {model_names[model]}. ¡Preguntame lo que quieras!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_input = update.message.text

    # Si no eligió modelo todavía
    if user_id not in user_models:
        await update.message.reply_text(
            "Hola!, elegí un modelo para continuar:",
            reply_markup=model_selection_keyboard()
        )
        return

    await update.message.chat.send_action("typing")

    try:
        model = user_models[user_id]
        agent = get_agent(user_id, model)
        response = agent.invoke({"input": user_input})
        await update.message.reply_text(response["output"])
    except Exception as e:
        await update.message.reply_text(f"❌ Ocurrió un error: {str(e)}")