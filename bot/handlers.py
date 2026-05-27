import base64
import asyncio
from datetime import datetime
import os
from agent.memory import get_memory
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import model_selection_keyboard
from agent.agent import get_agent
from database.database import save_image
from tools.pdf import process_pdf

# Guardamos el modelo elegido por cada usuario
user_models = {}
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CARPETA_IMAGENES = os.path.join(PROJECT_ROOT, "stored_images")
os.makedirs(CARPETA_IMAGENES, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente IA.\n\nPrimero elegí el modelo que querés usar:",
        reply_markup=model_selection_keyboard()
    )

async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    model = query.data

    if model != "gemini-2.5-flash":
        await query.edit_message_text(
            "Ese modelo no está habilitado. Por ahora solo está disponible 🟢 Gemini 2.5 Flash."
        )
        return

    user_models[user_id] = model

    model_names = {
        "gemini-2.5-flash": "🟢 Gemini 2.5 Flash",
    }

    selected_model_name = model_names.get(model, model)

    await query.edit_message_text(
        f"Perfecto, usando {selected_model_name}. ¡Preguntame lo que quieras!"
    )

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file_path = None

    # Si no eligió modelo todavía
    if user_id not in user_models:
        await update.message.reply_text(
            "Primero elegí un modelo:",
            reply_markup=model_selection_keyboard()
        )
        return

    await update.message.reply_text("📄 Recibí tu PDF, procesando...")
    await update.message.chat.send_action("typing")

    try:
        # Descargar el PDF de Telegram
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"/tmp/{user_id}_{update.message.document.file_name}"
        await file.download_to_drive(file_path)

        # Procesar el PDF
        result = await asyncio.to_thread(process_pdf, user_id, file_path)
        await update.message.reply_text(result)

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el PDF: {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file_path = None

    if user_id not in user_models:
        await update.message.reply_text(
            "Primero elegí un modelo:",
            reply_markup=model_selection_keyboard()
        )
        return

    user_caption = update.message.caption if update.message.caption else "Describí esta imagen en detalle."

    await update.message.reply_text("📥 Procesando tu imagen...")
    await update.message.chat.send_action("typing")

    try:
        # 1. Descargar imagen
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(CARPETA_IMAGENES, f"{user_id}_{timestamp}.jpg")
        await photo_file.download_to_drive(file_path)

        # 2. Convertir a base64
        with open(file_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 3. Mandar imagen + pregunta DIRECTO al LLM
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage

        vision_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        
        message = HumanMessage(content=[
            {"type": "text", "text": user_caption},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
        ])
        
        response = await asyncio.to_thread(vision_llm.invoke, [message])

        # 4. Guardar imagen + respuesta en memoria del agente
        memory = get_memory(user_id)
        await asyncio.to_thread(
            memory.save_context,
            {"input": f"[El usuario mandó una imagen] {user_caption}"},
            {"output": response.content},
        )

        await update.message.reply_text(response.content)
        await asyncio.to_thread(save_image, user_id, file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")



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
        response = await asyncio.to_thread(agent.invoke, {"input": user_input})
        await update.message.reply_text(response["output"])
    except Exception as e:
        await update.message.reply_text(f"❌ Ocurrió un error: {str(e)}")