from telegram import Update
from telegram.ext import ContextTypes
from agent.agent import get_agent

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente IA.\n\n"
        "Puedo ayudarte con:\n"
        "🔍 Buscar información en la web\n"
        "💬 Responder preguntas\n\n"
        "¡Escribime lo que necesitás!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_input = update.message.text

    # Indicador de escritura mientras procesa
    await update.message.chat.send_action("typing")

    try:
        agent = get_agent(user_id)
        response = agent.invoke({"input": user_input})
        await update.message.reply_text(response["output"])
    except Exception as e:
        error_text = str(e)
        if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
            await update.message.reply_text(
                "⚠️ I hit the Gemini API quota limit. Please try again later or use a different API key/model."
            )
            return
        await update.message.reply_text(f"❌ Ocurrió un error: {str(e)}")