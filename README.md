# botcelotl – Recordatorio personal y notificaciones por Telegram

Bot de Telegram que funciona como **cerebro notificador personal**: lee archivos
locales en el servidor (fuente de verdad) y envía mensajes programados. También
conserva el monitoreo de sitios web como función aparte.

## Características

- **Cronómetro de actividades** (`data/actividades.yaml`): metas diarias de
  tiempo (ej. tesis 2h, trabajo 1h, ejercicio 1h). El bot lleva la cuenta con
  comandos start/stop y muestra el avance del día.
- **Rutinas fijas** (`data/rutinas.yaml`): mensajes programados por hora
  (comer, dormir) y disparo del dashboard de tiempo.
- **Monitoreo de sitios** (`SITES`): alerta si alguno está caído (función aparte).
- **Agenda** (`data/agenda.md`): *suspendida* — el código sigue en
  `bot/agenda.py`; para reactivar el resumen, descomenta la rutina
  `tipo: resumen` en `data/rutinas.yaml`.
- Pensado para ejecutarse vía `cron` y dejar el bot corriendo con `pm2`.

## Fuente de verdad

Estos archivos son personales y están en `.gitignore` (solo viven en local).
Crea los tuyos a partir de las plantillas versionadas:

```bash
cp data/rutinas.example.yaml data/rutinas.yaml
cp data/actividades.example.yaml data/actividades.yaml
cp data/agenda.example.md data/agenda.md   # opcional (agenda suspendida)
```

### Cronómetro de actividades

Modelo de "presupuesto de tiempo": cada actividad tiene una meta diaria y el
bot acumula cuánto le dedicas.

- `data/actividades.yaml` — catálogo (`id`, `nombre`, `meta_min`, `alias`).
- `data/sesion.json` — sesión (cronómetro) abierta actual. Una a la vez.
- `data/bitacora.jsonl` — log append-only de bloques cerrados. Editable a mano
  para corregir.

El cronómetro se auto-cierra a las 23:59 (rutina `tipo: auto_cierre`) para que
una sesión no cruce la medianoche.

### `data/rutinas.yaml`
```yaml
rutinas:
  - hora: "07:00"        # HH:MM, hora local del servidor
    tipo: dashboard      # envía el avance de tiempo del día
  - hora: "14:00"
    mensaje: "¿Ya comiste? 🍽️"
  - hora: "23:59"
    tipo: auto_cierre    # cierra el cronómetro abierto
    # dias: [L,M,X,J,V]  # opcional; si se omite, todos los días
```

## Comandos del bot (Telegram)

- `empiezo <actividad>` (o `inicio` / `voy a`) — arranca el cronómetro; si había
  otro en curso, lo cierra solo.
- `termino` (o `paro` / `listo`) — cierra el cronómetro en curso.
- `+<actividad> <min>` (ej. `+tesis 45`) — registro manual de respaldo.
- `hoy` — dashboard de avance del día con barras.
- `actividades` — metas configuradas.
- `ayuda` — lista de comandos.

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
