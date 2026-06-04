import os
import yaml
from datetime import datetime

RUTINAS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'rutinas.yaml')

# weekday() -> Lun=0 ... Dom=6
DIAS = ['L', 'M', 'X', 'J', 'V', 'S', 'D']


def load_rutinas():
    if not os.path.exists(RUTINAS_FILE):
        return []
    with open(RUTINAS_FILE, 'r') as f:
        data = yaml.safe_load(f) or {}
    return data.get('rutinas', []) or []


def due_now(now: datetime):
    """Rutinas cuya hora coincide con el minuto actual y aplican hoy."""
    hhmm = now.strftime("%H:%M")
    hoy = DIAS[now.weekday()]
    pendientes = []
    for r in load_rutinas():
        if r.get('hora') != hhmm:
            continue
        dias = r.get('dias')
        if dias and hoy not in dias:
            continue
        pendientes.append(r)
    return pendientes
