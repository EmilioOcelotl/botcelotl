# botcelotl – Recordatorio personal y notificaciones por Telegram

Bot de Telegram que funciona como **cerebro notificador personal**: lee archivos
locales en el servidor (fuente de verdad) y envía mensajes programados. También
conserva el monitoreo de sitios web como función aparte.

## Características

- **Rutinas fijas** (`data/rutinas.yaml`): mensajes programados por hora.
- **Agenda dinámica** (`data/agenda.md`): prioridades, reuniones, deadlines y
  recordatorios. Editable a mano o por comandos al bot.
- **Resumen diario** que surfacea prioridades, reuniones y deadlines próximos.
- **Monitoreo de sitios** (`SITES`): alerta si alguno está caído (función aparte).
- Pensado para ejecutarse vía `cron` y dejar el bot corriendo con `pm2`.

## Fuente de verdad

Estos archivos son personales y están en `.gitignore` (solo viven en local).
Crea los tuyos a partir de las plantillas versionadas:

```bash
cp data/rutinas.example.yaml data/rutinas.yaml
cp data/agenda.example.md data/agenda.md
```

### `data/rutinas.yaml`
```yaml
rutinas:
  - hora: "07:00"        # HH:MM, hora local del servidor
    tipo: resumen        # arma el resumen del día desde la agenda
  - hora: "14:00"
    mensaje: "Mensaje para las 14"
  - hora: "23:00"
    mensaje: "Mensaje ppara las 23"
    # dias: [L,M,X,J,V]  # opcional; si se omite, todos los días
```

### `data/agenda.md`
Markdown con secciones fijas (`## Prioridades`, `## Reuniones`, `## Deadlines`,
`## Recordatorios`). Reuniones empiezan con `HH:MM`; deadlines con `AAAA-MM-DD`.

## Comandos del bot (Telegram)

- `prioridad: <texto>` — agrega una prioridad del día.
- `deadline: AAAA-MM-DD <texto>` — registra un deadline.
- `recordatorio: <texto>` — agrega recordatorio (varios separados por coma).
- `hoy` — responde con el resumen del día.

## Requisitos

- Python 3.7+
- Cuenta de Telegram
- Bot de Telegram creado con [@BotFather](https://t.me/BotFather)

## Instalación

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
# Disparador de rutinas (simula una hora sin esperar al reloj)
python scripts/tick.py --time 14:00

# Monitoreo de sitios
python scripts/run_monitor.py
```

## Cron

```cron
# Rutinas: revisar cada minuto qué toca enviar según data/rutinas.yaml
* * * * * cd /ruta/a/botcelotl && botcelotl-venv/bin/python scripts/tick.py

# Monitoreo de sitios (ajusta la frecuencia a gusto)
*/10 * * * * cd /ruta/a/botcelotl && botcelotl-venv/bin/python scripts/run_monitor.py
```

## Ejecutar bot

```
python -m bot.run_bot
```

## Configuración para pm2

```
pm2 start "./entorno-venv/bin/python -m bot.run_bot" \
  --name "telegram_bot" \
  --cwd "/ruta/a/la/carpeta"
```
