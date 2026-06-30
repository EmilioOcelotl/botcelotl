"""Cronómetro de actividades con metas diarias.

Modelo:
- data/actividades.yaml : catálogo de actividades con meta_min (minutos/día).
- data/sesion.json      : la sesión ABIERTA actual {actividad, inicio}. Una a la vez.
- data/bitacora.jsonl   : log append-only de bloques CERRADOS, una línea por sesión.

Flujo: iniciar() abre una sesión (cerrando la anterior si la hubiera);
terminar() la cierra y suma el bloque a la bitácora; resumen_dia() acumula.
"""
import os
import json
import yaml
from datetime import datetime, date

_DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
ACTIVIDADES_FILE = os.path.join(_DATA, 'actividades.yaml')
SESION_FILE = os.path.join(_DATA, 'sesion.json')
BITACORA_FILE = os.path.join(_DATA, 'bitacora.jsonl')


# --- Catálogo ---------------------------------------------------------------

def load_actividades():
    if not os.path.exists(ACTIVIDADES_FILE):
        return []
    with open(ACTIVIDADES_FILE, 'r') as f:
        data = yaml.safe_load(f) or {}
    return data.get('actividades', []) or []


def resolver_actividad(texto: str):
    """Devuelve la actividad cuyo id/nombre/alias coincide con `texto`, o None."""
    clave = texto.strip().lower()
    for a in load_actividades():
        candidatos = [str(a.get('id', '')).lower(), str(a.get('nombre', '')).lower()]
        candidatos += [str(x).lower() for x in (a.get('alias') or [])]
        if clave in candidatos:
            return a
    return None


# --- Sesión abierta ---------------------------------------------------------

def _read_sesion():
    if not os.path.exists(SESION_FILE):
        return None
    try:
        with open(SESION_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _write_sesion(sesion):
    with open(SESION_FILE, 'w') as f:
        json.dump(sesion, f)


def _claim_sesion():
    """Toma la sesión abierta de forma atómica y la quita del disco.

    Renombra SESION_FILE a un temporal propio del proceso: `os.rename` es atómico
    en POSIX, así que entre el bot (polling) y el cron (tick) solo uno gana la
    carrera y obtiene la sesión; el otro recibe None. Esto evita que ambos cierren
    y registren el mismo bloque por duplicado. Devuelve el dict de la sesión o None.
    """
    claimed = f"{SESION_FILE}.claimed.{os.getpid()}"
    try:
        os.rename(SESION_FILE, claimed)
    except OSError:
        return None  # no hay sesión, o otro proceso ya la tomó
    try:
        with open(claimed, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    finally:
        try:
            os.remove(claimed)
        except OSError:
            pass


def sesion_activa():
    """Sesión abierta actual o None. Incluye 'nombre' resuelto del catálogo."""
    s = _read_sesion()
    if not s:
        return None
    a = resolver_actividad(s.get('actividad', ''))
    s = dict(s)
    s['nombre'] = a['nombre'] if a else s.get('actividad', '')
    return s


# --- Bitácora ---------------------------------------------------------------

def _append_bitacora(entrada):
    with open(BITACORA_FILE, 'a') as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + '\n')


def _read_bitacora():
    if not os.path.exists(BITACORA_FILE):
        return []
    entradas = []
    with open(BITACORA_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entradas.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entradas


def _fin_de_dia(d: datetime) -> datetime:
    return d.replace(hour=23, minute=59, second=59, microsecond=0)


def _cerrar(sesion, fin: datetime):
    """Calcula el bloque de `sesion` hasta `fin` y lo escribe en la bitácora.

    Un bloque nunca cruza la medianoche: si se cierra ya entrado el día siguiente
    (p. ej. el `auto_cierre` de las 23:59 no corrió por una caída de cron), recorta
    el fin al final del día de inicio para no acumular horas fantasma.
    """
    inicio = datetime.fromisoformat(sesion['inicio'])
    fin = min(fin, _fin_de_dia(inicio))
    minutos = max(0, round((fin - inicio).total_seconds() / 60))
    a = resolver_actividad(sesion.get('actividad', ''))
    entrada = {
        'fecha': inicio.date().isoformat(),
        'actividad': a['id'] if a else sesion.get('actividad', ''),
        'nombre': a['nombre'] if a else sesion.get('actividad', ''),
        'inicio': sesion['inicio'],
        'fin': fin.isoformat(timespec='seconds'),
        'minutos': minutos,
    }
    _append_bitacora(entrada)
    return entrada


# --- Operaciones ------------------------------------------------------------

def iniciar(texto: str, now: datetime = None):
    """Abre cronómetro para la actividad `texto`. Cierra la anterior si la había.

    Devuelve (actividad, cerrada) donde `cerrada` es la entrada del bloque
    previo que se cerró por cambio de actividad (o None).
    """
    now = now or datetime.now()
    a = resolver_actividad(texto)
    if not a:
        return None, None
    # Toma la sesión previa de forma atómica para que no se cierre por duplicado
    # si el cron y el bot coinciden.
    previa = _claim_sesion()
    cerrada = _cerrar(previa, now) if previa else None
    _write_sesion({'actividad': a['id'], 'inicio': now.isoformat(timespec='seconds')})
    return a, cerrada


def terminar(now: datetime = None):
    """Cierra la sesión abierta. Devuelve la entrada cerrada o None si no había."""
    now = now or datetime.now()
    # `_claim_sesion` lee y quita la sesión en una sola operación atómica: si otro
    # proceso (cron/bot) la toma primero, aquí recibimos None y no duplicamos.
    s = _claim_sesion()
    if not s:
        return None
    return _cerrar(s, now)


def registrar_manual(texto: str, minutos: int, now: datetime = None):
    """Agrega un bloque ya cerrado de `minutos` (respaldo si olvidaste el cronómetro)."""
    now = now or datetime.now()
    a = resolver_actividad(texto)
    if not a:
        return None
    entrada = {
        'fecha': now.date().isoformat(),
        'actividad': a['id'],
        'nombre': a['nombre'],
        'inicio': None,
        'fin': now.isoformat(timespec='seconds'),
        'minutos': max(0, int(minutos)),
        'manual': True,
    }
    _append_bitacora(entrada)
    return entrada


def auto_cierre(now: datetime = None):
    """Cierra cualquier sesión abierta (para que no cruce la medianoche)."""
    return terminar(now)


# --- Acumulado / dashboard --------------------------------------------------

def _fmt_dur(minutos: int) -> str:
    h, m = divmod(int(minutos), 60)
    if h and m:
        return f"{h}h{m:02d}"
    if h:
        return f"{h}h"
    return f"{m}m"


def _barra(actual: int, meta: int, ancho: int = 7) -> str:
    if meta <= 0:
        return '─' * ancho
    llenos = min(ancho, round(ancho * actual / meta))
    return '█' * llenos + '░' * (ancho - llenos)


def minutos_por_actividad(fecha: date = None):
    """{id_actividad: minutos} acumulados en `fecha` (incluye la sesión abierta)."""
    fecha = fecha or date.today()
    acum = {}
    for e in _read_bitacora():
        if e.get('fecha') == fecha.isoformat():
            acum[e['actividad']] = acum.get(e['actividad'], 0) + int(e.get('minutos', 0))
    # Suma el tiempo en curso de la sesión abierta, si es de hoy.
    s = _read_sesion()
    if s:
        inicio = datetime.fromisoformat(s['inicio'])
        if inicio.date() == fecha:
            a = resolver_actividad(s.get('actividad', ''))
            aid = a['id'] if a else s.get('actividad', '')
            # Mismo tope de medianoche que `_cerrar`, para que el conteo en vivo
            # de una sesión olvidada no se dispare.
            ref = min(datetime.now(), _fin_de_dia(inicio))
            en_curso = max(0, round((ref - inicio).total_seconds() / 60))
            acum[aid] = acum.get(aid, 0) + en_curso
    return acum


def resumen_dia(fecha: date = None, now: datetime = None):
    """Texto con barras de avance por actividad para `fecha`."""
    fecha = fecha or date.today()
    now = now or datetime.now()
    acum = minutos_por_actividad(fecha)
    acts = load_actividades()

    titulo = "📊 Hoy" if fecha == date.today() else f"📊 {fecha.isoformat()}"
    lineas = [f"{titulo} ({fecha.strftime('%d/%m')})"]

    total_hecho = 0
    total_meta = 0
    nombres = [a.get('nombre', a.get('id', '')) for a in acts]
    ancho_nombre = max((len(n) for n in nombres), default=0)

    for a in acts:
        aid = a['id']
        meta = int(a.get('meta_min', 0))
        hecho = acum.get(aid, 0)
        total_hecho += hecho
        total_meta += meta
        nombre = a.get('nombre', aid).ljust(ancho_nombre)
        marca = " ✅" if meta and hecho >= meta else ""
        lineas.append(f"{nombre} {_barra(hecho, meta)} {_fmt_dur(hecho)}/{_fmt_dur(meta)}{marca}")

    # Actividades registradas que no están en el catálogo.
    extras = {k: v for k, v in acum.items() if k not in {a['id'] for a in acts}}
    for k, v in extras.items():
        lineas.append(f"{k} · {_fmt_dur(v)}")
        total_hecho += v

    lineas.append(f"\nTotal: {_fmt_dur(total_hecho)}/{_fmt_dur(total_meta)}")

    s = sesion_activa()
    if s and datetime.fromisoformat(s['inicio']).date() == fecha:
        desde = datetime.fromisoformat(s['inicio']).strftime('%H:%M')
        lineas.append(f"⏱️ En curso: {s['nombre']} (desde {desde})")

    return "\n".join(lineas)
