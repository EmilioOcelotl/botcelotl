import sys
import os
import asyncio
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.monitor import check_sites
from bot.reminder import get_reminders, clear_reminders
from bot.notifier import send_message

async def main():
    now = datetime.now()

    await check_sites()

    reminders = get_reminders()
    if reminders:
        reminder_message = "📝 Recordatorios:\n" + "\n".join(f"- {r}" for r in reminders)
        await send_message(reminder_message)

        # Borrar tras enviarlos en la corrida de las 8:00 AM
        if now.hour == 8:
            clear_reminders()

if __name__ == "__main__":
    asyncio.run(main())
