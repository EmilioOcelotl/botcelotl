import sys
import os
import asyncio
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.monitor import check_sites
from bot.reminder import get_reminders, clear_reminders
from bot.telegram_bot import send_message

async def main():
    now = datetime.now()

    await check_sites()

    reminders = get_reminders()
    if reminders:
        reminder_message = "📝 Recordatorios:\n" + "\n".join(f"- {r}" for r in reminders)
        await send_message(reminder_message)

    # Solo borrar a las 8:00 AM después de enviar recordatorios
    if now.hour == 8 and now.minute == 0:
        clear_reminders()

if __name__ == "__main__":
    asyncio.run(main())
