# 📡 botcelotl – Monitoreo de Sitios y Notificaciones por Telegram

Este proyecto implementa un bot de Telegram que verifica si tus sitios web están activos y te notifica si alguno deja de responder correctamente.

## ✅ Características implementadas (hasta esta etapa)

- Revisa periódicamente si uno o más sitios web están funcionando.
- Envía alertas por Telegram si algún sitio está caído o no responde correctamente.
- Organizado en un entorno virtual Python, con dependencias controladas.
- Preparado para ejecutarse automáticamente (por ejemplo, vía `cron`).

## 🚀 Requisitos

- Python 3.7+
- Cuenta de Telegram
- Bot de Telegram creado con [@BotFather](https://t.me/BotFather)

## ⚙️ Instalación

1. Clona o descarga este repositorio:

```bash
git clone https://github.com/EmilioOcelotl/botcelotl.git
cd botcelotl
python3 -m venv botcelotl-venv
source botcelotl-venv/bin/activate    # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Crea un archivo .env con: 

```bash
TELEGRAM_TOKEN=123456:ABCDEFghijklMNOPQ
TELEGRAM_CHAT_ID=123456789
SITES=https://miweb1.com,https://midominio.com/proyecto
```

## Prueba

```
python scripts/run_monitor.py
```

Este script puede ejecutarse con cron cada cierto tiempo.z  

## Ejecutar bot

```
python -m bot.run_bot
```
Usar pm2 para dejar corriendo al bot. 
