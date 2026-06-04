from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from bot.config import TELEGRAM_TOKEN
from bot.telegram_bot import handle_message

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()
