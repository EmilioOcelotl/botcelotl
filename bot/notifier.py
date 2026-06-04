# send_message vive en telegram_bot.py (usa la application global del bot).
# Se reexporta aquí para no romper los imports existentes (monitor, run_monitor).
from .telegram_bot import send_message  # noqa: F401
