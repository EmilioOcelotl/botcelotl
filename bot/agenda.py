import os
import re
from datetime import datetime, date

AGENDA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'agenda.md')

SECCIONES = ['Prioridades', 'Reuniones', 'Deadlines', 'Recordatorios']

_FECHA_RE = re.compile(r'^(\d{4}-\d{2}-\d{2})\b\s*(.*)$')
_HORA_RE = re.compile(r'^(\d{1,2}:\d{2})\b')


def _read_lines():
    if not os.path.exists(AGENDA_FILE):
        return []
    with open(AGENDA_FILE, 'r') as f:
        return f.read().splitlines()


def _parse_sections(lines):
    """dict {seccion: [items]} respetando el orden del archivo."""
    secciones = {}
    actual = None
    for line in lines:
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if m:
            actual = m.group(1)
            secciones.setdefault(actual, [])
            continue
        item = re.match(r'^-\s+(.*)$', line)
        if item and actual is not None:
            texto = item.group(1).strip()
            if texto:
                secciones[actual].append(texto)
    return secciones


def load_agenda():
    secciones = _parse_sections(_read_lines())
    deadlines = []
    for texto in secciones.get('Deadlines', []):
        m = _FECHA_RE.match(texto)
        if m:
            try:
                d = datetime.strptime(m.group(1), '%Y-%m-%d').date()
                deadlines.append((d, m.group(2).strip()))
                continue
            except ValueError:
                pass
        deadlines.append((None, texto))
    return {
        'prioridades': secciones.get('Prioridades', []),
        'reuniones': secciones.get('Reuniones', []),
        'deadlines': deadlines,
        'recordatorios': secciones.get('Recordatorios', []),
    }


def add_item(seccion: str, texto: str):
    """Inserta '- texto' bajo el encabezado '## seccion', creando la sección si falta."""
    texto = texto.strip()
    if not texto:
        return
    lines = _read_lines()

    header_idx = None
    for i, line in enumerate(lines):
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if m and m.group(1) == seccion:
            header_idx = i
            break

    if header_idx is None:
        # Crear la sección al final.
        if lines and lines[-1].strip() != '':
            lines.append('')
        lines.append(f'## {seccion}')
        lines.append(f'- {texto}')
    else:
        # Insertar tras el último ítem/línea de la sección (antes del próximo '## ').
        insert_at = len(lines)
        for j in range(header_idx + 1, len(lines)):
            if re.match(r'^##\s+', lines[j]):
                insert_at = j
                break
        # Retroceder sobre líneas en blanco finales de la sección.
        while insert_at > header_idx + 1 and lines[insert_at - 1].strip() == '':
            insert_at -= 1
        lines.insert(insert_at, f'- {texto}')

    with open(AGENDA_FILE, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def build_daily_summary(now: datetime = None):
    now = now or datetime.now()
    hoy = now.date()
    a = load_agenda()
    partes = [f"☀️ Resumen del {hoy.isoformat()}"]

    if a['prioridades']:
        partes.append("\n🎯 Prioridades:")
        partes += [f"- {p}" for p in a['prioridades']]

    if a['reuniones']:
        partes.append("\n📅 Reuniones:")
        partes += [f"- {r}" for r in a['reuniones']]

    if a['deadlines']:
        con_fecha = sorted([d for d in a['deadlines'] if d[0] is not None], key=lambda x: x[0])
        sin_fecha = [d for d in a['deadlines'] if d[0] is None]
        partes.append("\n⏰ Deadlines:")
        for d, texto in con_fecha:
            dias = (d - hoy).days
            if dias < 0:
                etiqueta = f"vencido hace {-dias}d"
            elif dias == 0:
                etiqueta = "vence hoy"
            elif dias == 1:
                etiqueta = "mañana"
            else:
                etiqueta = f"en {dias}d"
            partes.append(f"- {d.isoformat()} {texto} ({etiqueta})")
        for _, texto in sin_fecha:
            partes.append(f"- {texto}")

    if len(partes) == 1:
        partes.append("\nNada en la agenda. 🌿")

    return "\n".join(partes)
