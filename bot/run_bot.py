from telegram.ext import MessageHandler, filters
from bot.telegram_bot import application, handle_message

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    application.run_polling()
