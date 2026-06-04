from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from . import agenda

# Creamos la aplicación global del bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

AYUDA = (
    "Comandos disponibles:\n"
    "- prioridad: <texto>\n"
    "- deadline: AAAA-MM-DD <texto>\n"
    "- recordatorio: <texto>\n"
    "- hoy  (resumen del día)"
)


# Para recibir comandos y editar la agenda desde Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    low = text.lower()

    if low in ("hoy", "/hoy"):
        await update.message.reply_text(agenda.build_daily_summary(datetime.now()))

    elif low.startswith("prioridad:"):
        contenido = text.split(":", 1)[1].strip()
        if contenido:
            agenda.add_item("Prioridades", contenido)
            await update.message.reply_text("🎯 Prioridad agregada.")

    elif low.startswith("deadline:"):
        contenido = text.split(":", 1)[1].strip()
        partes = contenido.split(maxsplit=1)
        fecha_ok = False
        if len(partes) == 2:
            try:
                datetime.strptime(partes[0], "%Y-%m-%d")
                fecha_ok = True
            except ValueError:
                fecha_ok = False
        if fecha_ok:
            agenda.add_item("Deadlines", contenido)
            await update.message.reply_text("⏰ Deadline agregado.")
        else:
            await update.message.reply_text(
                "Formato: deadline: AAAA-MM-DD descripción\n"
                "Ej: deadline: 2026-06-10 entregar proyecto"
            )

    elif low.startswith("recordatorio:"):
        contenido = text.split(":", 1)[1].strip()
        # Permite varios separados por coma en un mismo mensaje.
        items = [i.strip() for i in contenido.split(",") if i.strip()]
        for item in items:
            agenda.add_item("Recordatorios", item)
        if items:
            await update.message.reply_text("✅ Recordatorio agregado.")

    else:
        await update.message.reply_text(AYUDA)


# Envío simple desde un proceso ya inicializado (p. ej. el bot en polling).
async def send_message(text: str):
    await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)


# Envío para scripts one-shot de cron: abre y cierra el cliente del bot.
async def send_now(text: str):
    async with application.bot:
        await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
