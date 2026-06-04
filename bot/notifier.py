# send_message / send_now viven en telegram_bot.py (usan la application global).
# Se reexportan aquí para no romper los imports existentes (monitor, run_monitor).
from .telegram_bot import send_message, send_now  # noqa: F401
