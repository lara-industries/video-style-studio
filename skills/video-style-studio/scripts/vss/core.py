import datetime
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

class StudioError(Exception):
    pass

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def guard_secret(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    for name in ('ELEVENLABS_API_KEY', 'SCRAPECREATORS_API_KEY', 'OPENAI_API_KEY'):
        secret = os.environ.get(name, '')
        if secret and len(secret) > 8 and secret in text:
            raise StudioError('Se detectó una credencial en contenido. Retírala; no se guardó ni imprimió.')
    if re.search(r'(?i)(?:xi-api-key|x-api-key|authorization)\s*[:=]\s*["\x27]?(?:bearer\s+)?[a-z0-9_-]{16,}', text):
        raise StudioError('El archivo contiene una credencial aparente. Usa el gestor de secretos.')
    return value

def read(path):
    path = Path(path)
    if path.stat().st_size > 15 * 1024 * 1024:
        raise StudioError('JSON demasiado grande.')
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, data):
    guard_secret(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)

def run(args, timeout=180, env=None):
    try:
        proc = subprocess.run([str(a) for a in args], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StudioError('No terminó la herramienta local: ' + Path(str(args[0])).name) from exc
    if proc.returncode:
        # Third-party stderr can contain signed URLs, headers or user data.
        raise StudioError('Falló ' + Path(str(args[0])).name + '. Revisa disponibilidad/formato; no se publicó su salida privada.')
    return proc.stdout

def under(root, relative):
    root = Path(root).resolve()
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise StudioError('Una ruta intenta salir del proyecto.')
    return candidate

def state(root):
    root = Path(root).resolve()
    p = root / 'project.json'
    if not p.is_file():
        raise StudioError('Primero crea un proyecto con init.')
    data = read(p)
    if data.get('schema') != 1:
        raise StudioError('Versión de proyecto no compatible.')
    return root, data

def save(root, data, event):
    data.setdefault('history', []).append({'at': now(), 'event': event})
    write(Path(root) / 'project.json', data)

def store_file(root, source, label):
    root = Path(root).resolve()
    source = Path(source).resolve()
    if not source.is_file():
        raise StudioError('No se encontró el archivo de entrada.')
    digest = sha(source)
    dest = under(root, 'assets/' + digest + source.suffix.lower())
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copyfile(source, dest)
    if sha(dest) != digest:
        raise StudioError('El archivo guardado cambió inesperadamente.')
    return {'path': str(dest.relative_to(root)), 'sha256': digest, 'label': label}

def checked(root, record):
    path = under(root, record['path'])
    if not path.is_file() or sha(path) != record['sha256']:
        raise StudioError('Un archivo cambió o falta: ' + record['path'])
    return path

def probe(path):
    data = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path]))
    streams = data.get('streams', [])
    duration = float(data.get('format', {}).get('duration', 0))
    if duration <= 0 or not streams:
        raise StudioError('El archivo no contiene media válida con duración conocida.')
    return {'duration': duration, 'streams': streams}

def doctor():
    result = {'schema': 1, 'checked_at': now(), 'os': platform.system(),
              'python': platform.python_version(), 'python_executable': sys.executable,
              'execution_location': 'unknown', 'desktop_application': 'unknown',
              'note': 'Ejecutar Python prueba este runtime; no prueba que sea la app de escritorio del usuario.',
              'filesystem_write': False, 'process_execution': False,
              'pillow': importlib.util.find_spec('PIL') is not None,
              'yt_dlp': importlib.util.find_spec('yt_dlp') is not None,
              'faster_whisper': importlib.util.find_spec('faster_whisper') is not None,
              'ffmpeg': False, 'ffprobe': False}
    try:
        with tempfile.TemporaryDirectory(prefix='vss-check-') as d:
            p = Path(d) / 'probe'; p.write_bytes(b'vss'); result['filesystem_write'] = p.read_bytes() == b'vss'
        result['process_execution'] = run([sys.executable, '-c', 'print("vss")'], 10).strip() == b'vss'
    except StudioError:
        pass
    for binary in ('ffmpeg', 'ffprobe'):
        if shutil.which(binary):
            try:
                run([binary, '-version'], 10); result[binary] = True
            except StudioError:
                pass
    result['python_compatible'] = sys.version_info >= (3, 10)
    result['pillow_compatible'] = False
    if result['pillow']:
        import PIL
        result['pillow_version'] = PIL.__version__
        result['pillow_compatible'] = tuple(int(x) for x in PIL.__version__.split('.')[:2]) >= (10, 4)
    result['x264_encoder'] = False
    if result['ffmpeg']:
        try: result['x264_encoder'] = b'libx264' in run(['ffmpeg', '-hide_banner', '-encoders'], 10)
        except StudioError: pass
    result['render_capable'] = all(result[k] for k in ('filesystem_write', 'process_execution', 'pillow_compatible', 'python_compatible', 'ffmpeg', 'ffprobe', 'x264_encoder'))
    return result

def require_local(data):
    evidence = data.get('environment', {})
    if evidence.get('execution_location') != 'user-desktop' or evidence.get('source') not in ('user-confirmation', 'runtime-attestation'):
        raise StudioError('No puedo verificar que este runtime controle tu computador. Confirma la ubicación real o abre un agente con archivos y terminal locales.')
    actual = doctor()
    if not actual['render_capable']:
        raise StudioError('Faltan herramientas. Ejecuta doctor y revisa la instalación propuesta antes de autorizarla.')

def consent(data, scope):
    record = data.get('consents', {}).get(scope, {})
    if record.get('decision') != 'approve' or not record.get('verbatim'):
        raise StudioError('Falta autorización registrada para: ' + scope)

def decision_record(decision, response_path):
    text = guard_secret(Path(response_path).read_text(encoding='utf-8')).strip()
    if not text:
        raise StudioError('Conserva la respuesta exacta del usuario.')
    # The agent records an explicit decision from the conversation. Do not guess it
    # from words such as 'no': 'No cambies nada, me gusta' is a valid approval.
    if decision not in ('approve', 'reject'):
        raise StudioError('Registra una decisión explícita; una respuesta ambigua no es aprobación.')
    return {'decision': decision, 'verbatim': text, 'recorded_at': now(),
            'identity_check': 'Not authenticated; agent records the actual user response.'}

def fingerprint(root, data):
    records = {k: data[k] for k in ('analysis', 'style', 'voice', 'story', 'scene') if k in data}
    if len(records) != 5:
        raise StudioError('Faltan análisis, estilo, audio, guion o escena.')
    for item in records.values():
        checked(root, item)
    records['render_settings'] = data['settings']
    checked(root, data['reference']['media'])
    records['reference_sha256'] = data['reference']['media']['sha256']
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
