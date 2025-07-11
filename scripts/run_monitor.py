import sys
import os

# Añade la carpeta raíz del proyecto al path de módulos de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from bot.monitor import check_sites
# from bot.monitor import check_arduino_heartbeat

if __name__ == "__main__":
    asyncio.run(check_sites())
    # asyncio.run(check_arduino_heartbeat())
