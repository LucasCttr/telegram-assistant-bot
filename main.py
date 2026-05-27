import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import start, handle_message

load_dotenv()

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    
    app = ApplicationBuilder().token(token).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start))
    
    # Mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()