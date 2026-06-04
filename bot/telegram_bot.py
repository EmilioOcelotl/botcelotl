from telegram import Update
from telegram.ext import ContextTypes
from .reminder import add_reminder
# send_message vive en notifier.py; se reexporta para no romper imports previos
from .notifier import send_message  # noqa: F401

# Para recibir y guardar recordatorios desde Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower().startswith("recordatorio:"):
        contenido = text[len("recordatorio:"):].strip()
        add_reminder(contenido)
        await update.message.reply_text("✅ Recordatorio agregado.")
