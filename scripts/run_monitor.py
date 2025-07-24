import sys
import os
import asyncio
from datetime import datetime

# Añade la carpeta raíz del proyecto al path de módulos de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.monitor import check_sites
from bot.reminder import get_reminders, clear_reminders
from bot.telegram_bot import send_message  # <--- Importa send_message

async def main():
    now = datetime.now()
    if now.hour == 20 and now.minute == 0:
        clear_reminders()

    await check_sites()

    reminders = get_reminders()
    if reminders:
        reminder_message = "Recordatorios:\n" + "\n".join(f"- {r}" for r in reminders)
        await send_message(reminder_message)  # <--- Envía el mensaje por Telegram

if __name__ == "__main__":
    asyncio.run(main())
