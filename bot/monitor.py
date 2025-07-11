import requests
import asyncio
from datetime import datetime, timedelta
from .config import SITES
from .notifier import send_message

async def check_sites():
    for site in SITES:
        try:
            r = requests.get(site, timeout=5)
            if r.status_code == 200:
                await send_message(f"✅ El sitio {site} está funcionando correctamente.")
            else:
                await send_message(f"⚠️ El sitio {site} responde con código {r.status_code}.")
        except Exception as e:
            await send_message(f"❌ Error al acceder a {site}: {e}")

async def check_arduino_heartbeat(filepath="arduino_heartbeats.json"):
    import json
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        for device, timestamp in data.items():
            last = datetime.fromisoformat(timestamp)
            if datetime.utcnow() - last > timedelta(minutes=3):
                await send_message(f"⚠️ {device} no ha enviado latido desde hace más de 3 min.")
    except FileNotFoundError:
        await send_message("⚠️ No se encontró archivo de latidos.")