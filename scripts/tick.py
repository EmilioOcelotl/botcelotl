import sys
import os
import asyncio
import argparse
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.rutinas import due_now
from bot.agenda import build_daily_summary
from bot.telegram_bot import send_now


async def main(now: datetime):
    pendientes = due_now(now)
    if not pendientes:
        return
    for r in pendientes:
        if r.get("tipo") == "resumen":
            msg = build_daily_summary(now)
        else:
            msg = r.get("mensaje", "")
        if msg:
            await send_now(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Disparador de rutinas (cron cada minuto)")
    parser.add_argument("--time", help="Simular hora HH:MM (para pruebas)")
    args = parser.parse_args()

    now = datetime.now()
    if args.time:
        h, m = args.time.split(":")
        now = now.replace(hour=int(h), minute=int(m), second=0, microsecond=0)

    asyncio.run(main(now))
