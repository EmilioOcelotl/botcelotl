from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from .reminder import add_reminder

# Creamos la aplicación global del bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Para recibir y guardar recordatorios desde Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower().startswith("recordatorio:"):
        contenido = text[len("recordatorio:"):].strip()
        add_reminder(contenido)
        await update.message.reply_text("✅ Recordatorio agregado.")

# Función para enviar mensajes desde otros scripts (no necesita application como parámetro)
async def send_message(text: str):
    await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
