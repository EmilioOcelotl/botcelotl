from telegram.ext import ApplicationBuilder, MessageHandler, filters
from bot.config import TELEGRAM_TOKEN
from bot.telegram_bot import handle_message

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()
