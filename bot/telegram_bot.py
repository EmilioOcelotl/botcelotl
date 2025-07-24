from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from .reminder import add_reminder

# Para enviar mensajes desde otros scripts (como run_monitor)
bot = Bot(token=TELEGRAM_TOKEN)

async def send_message(text):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)

# Para recibir y guardar recordatorios desde Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower().startswith("recordatorio:"):
        contenido = text[len("recordatorio:"):].strip()
        add_reminder(contenido)
        await update.message.reply_text("✅ Recordatorio agregado.")
