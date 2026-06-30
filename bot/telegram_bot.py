import re
import html
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from . import tracking

# Creamos la aplicación global del bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

AYUDA = (
    "🦎 Comandos de tiempo:\n"
    "- empiezo <actividad>  → arranca el cronómetro\n"
    "- termino  → cierra el cronómetro en curso\n"
    "- +<actividad> <min>  → registro manual (ej. +tesis 45)\n"
    "- hoy  → dashboard de avance del día\n"
    "- actividades  → metas configuradas\n"
    "- ayuda  → muestra esto"
)

# "empiezo tesis", "inicio gym", "voy a chamba"
_INICIO_RE = re.compile(r'^(?:empiezo|inicio|empezar|voy a)\s+(.+)$', re.IGNORECASE)
# "termino", "paro", "listo", "fin"
_FIN_RE = re.compile(r'^(?:termino|termina|terminar|paro|para|listo|fin)$', re.IGNORECASE)
# "+tesis 45", "+tesis 45m"
_MANUAL_RE = re.compile(r'^\+\s*(\w+)\s+(\d+)\s*m?$', re.IGNORECASE)


def _lista_actividades() -> str:
    acts = tracking.load_actividades()
    if not acts:
        return "No hay actividades configuradas en data/actividades.yaml."
    lineas = ["🎯 Actividades y metas:"]
    for a in acts:
        meta = int(a.get("meta_min", 0))
        h, m = divmod(meta, 60)
        meta_txt = (f"{h}h" if h else "") + (f"{m:02d}" if h and m else (f"{m}m" if m else ""))
        alias = a.get("alias") or []
        extra = f"  ({', '.join(alias)})" if alias else ""
        lineas.append(f"- {a.get('nombre', a['id'])}: {meta_txt or '0m'}{extra}")
    return "\n".join(lineas)


# Para recibir comandos desde Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    low = text.lower()

    if low in ("hoy", "/hoy", "dashboard"):
        await update.message.reply_text(
            como_monospace(tracking.resumen_dia()), parse_mode="HTML"
        )

    elif low in ("ayuda", "/ayuda", "help", "/help", "comandos"):
        await update.message.reply_text(AYUDA)

    elif low in ("actividades", "/actividades", "metas"):
        await update.message.reply_text(_lista_actividades())

    elif _INICIO_RE.match(text):
        nombre = _INICIO_RE.match(text).group(1).strip()
        act, cerrada = tracking.iniciar(nombre)
        if not act:
            await update.message.reply_text(
                f"No conozco la actividad «{nombre}». Escribe «actividades» para ver las opciones."
            )
        else:
            partes = []
            if cerrada:
                partes.append(f"⏹️ Cerré {cerrada['nombre']} +{tracking._fmt_dur(cerrada['minutos'])}.")
            partes.append(f"⏱️ {act['nombre']} en curso ({datetime.now().strftime('%H:%M')}).")
            await update.message.reply_text(" ".join(partes))

    elif _FIN_RE.match(low):
        entrada = tracking.terminar()
        if not entrada:
            await update.message.reply_text("No hay ningún cronómetro en curso.")
        else:
            hoy = tracking.minutos_por_actividad().get(entrada["actividad"], 0)
            meta = next(
                (int(a.get("meta_min", 0)) for a in tracking.load_actividades()
                 if a["id"] == entrada["actividad"]), 0
            )
            await update.message.reply_text(
                f"✅ {entrada['nombre']} +{tracking._fmt_dur(entrada['minutos'])} · "
                f"hoy {tracking._fmt_dur(hoy)}/{tracking._fmt_dur(meta)}"
            )

    elif _MANUAL_RE.match(text):
        m = _MANUAL_RE.match(text)
        nombre, minutos = m.group(1), int(m.group(2))
        entrada = tracking.registrar_manual(nombre, minutos)
        if not entrada:
            await update.message.reply_text(
                f"No conozco la actividad «{nombre}». Escribe «actividades» para ver las opciones."
            )
        else:
            await update.message.reply_text(
                f"✅ {entrada['nombre']} +{tracking._fmt_dur(entrada['minutos'])} (manual)."
            )

    else:
        await update.message.reply_text(AYUDA)


# Envuelve texto en un bloque monoespaciado para que las columnas (barras del
# dashboard) queden alineadas: Telegram usa fuente proporcional fuera de <pre>.
def como_monospace(text: str) -> str:
    return f"<pre>{html.escape(text)}</pre>"


# Envío simple desde un proceso ya inicializado (p. ej. el bot en polling).
async def send_message(text: str, parse_mode: str = None):
    await application.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode=parse_mode
    )


# Envío para scripts one-shot de cron: abre y cierra el cliente del bot.
async def send_now(text: str, parse_mode: str = None):
    async with application.bot:
        await application.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode=parse_mode
        )
