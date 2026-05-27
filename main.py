import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters
from bot.handlers import handle_image, handle_pdf, start, handle_message, handle_model_selection
from database.database import initialize_db

load_dotenv()

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    initialize_db()
    
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))  # ← handler para imágenes
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))  # ← handler para PDFs
    app.add_handler(CallbackQueryHandler(handle_model_selection))  # ← botones
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()