import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.monitor import check_sites
from bot.telegram_bot import application


async def main():
    # Abre el cliente del bot una sola vez para esta corrida de cron.
    async with application.bot:
        await check_sites()


if __name__ == "__main__":
    asyncio.run(main())
