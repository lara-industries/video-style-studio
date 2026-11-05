import json
import math
import os
import shutil
import sys
import wave
from array import array
import tempfile
from pathlib import Path
from .core import StudioError, checked, consent, doctor, guard_secret, now, probe, read, require_local, run, save, sha, state, store_file, under, write
from .network import fetch, is_social, public_url, social_metadata


def init(root, url):
    public_url(url, resolve=False)
    guard_secret(url)
    root = Path(root).resolve()
    if (root / 'project.json').exists():
        _, data = state(root)
        if data['reference']['url'] != url:
            raise StudioError('Este proyecto tiene otra referencia. Usa una carpeta nueva.')
        return data
    if root.exists() and any(root.iterdir()):
        raise StudioError('Usa una carpeta vacía para conservar los archivos existentes.')
    root.mkdir(parents=True, exist_ok=True)
    (root / '.gitignore').write_text('*\n', encoding='utf-8')
    data = {'schema': 1, 'created': now(), 'reference': {'url': url, 'state': 'needed'},
            'settings': {'width': 720, 'height': 1280, 'fps': 30}, 'consents': {}}
    save(root, data, 'project-created')
    return data


def capture(root, media_file=None, metadata_file=None, provider='yt-dlp'):
    root, data = state(root); require_local(data)
    if data['reference'].get('media'):
        checked(root, data['reference']['media'])
        return {'state': 'already-captured', 'reference': data['reference']}
    url = data['reference']['url']
    with tempfile.TemporaryDirectory(prefix='vss-capture-') as td:
        td = Path(td)
        if media_file:
            media = Path(media_file)
            metadata = read(metadata_file) if metadata_file else {'title': None, 'description': '', 'availability': 'User file; page metadata not retrieved.'}
            origin = 'imported-user-file'
        else:
            if is_social(url):
                if provider == 'scrapecreators': consent(data, 'scrapecreators-request')
                raw, metadata = social_metadata(url, provider)
                raw_path = td / 'provider.json'; raw_path.write_bytes(raw)
                raw_record = store_file(root, raw_path, 'provider-original-response')
                media_url = metadata.pop('media_url')
            else:
                if not url.split('?')[0].lower().endswith(('.mp4', '.mov', '.webm')):
                    raise StudioError('Este enlace no es un video directo ni una plataforma admitida. Importa el archivo y conserva esta URL.')
                media_url = url
                metadata = {'title': None, 'description': '', 'availability': 'Direct media has no independent page title or description.'}
                raw_record = None
            media = td / 'source.mp4'
            fetch(media_url, media)
            origin = 'downloaded'
        info = probe(media)
        video = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
        if not video:
            raise StudioError('La referencia no contiene video.')
        if info['duration'] > 180:
            raise StudioError('Esta edición analiza referencias de hasta 180s. Escoge un clip completo más breve.')
        if int(video.get('width', 0)) * int(video.get('height', 0)) > 3840 * 2160:
            raise StudioError('La referencia supera 4K. Importa una copia reducida y conserva el original.')
        record = store_file(root, media, 'reference-original')
        metadata['source_url'] = url
        metadata['capture_method'] = origin
        meta_path = td / 'metadata.json'; write(meta_path, metadata)
        data['reference'].update({'state': 'captured', 'capture_method': origin, 'media': record,
                                  'metadata': store_file(root, meta_path, 'literal-metadata'), 'probe': info})
        if not media_file and raw_record:
            data['reference']['provider_raw'] = raw_record
        save(root, data, 'reference-' + origin)
    return data['reference']


def import_transcript(root, path, source, language='es'):
    root, data = state(root)
    content = Path(path).read_text(encoding='utf-8')
    guard_secret(content)
    if not content.strip():
        raise StudioError('El transcript está vacío. Para una fuente sin habla usa la declaración explícita de audio sin voz.')
    data['reference']['transcript'] = {**store_file(root, path, 'literal-transcript'), 'source': source, 'language': language,
                                      'reading_state': 'captured-not-read'}
    save(root, data, 'literal-transcript-captured')
    return data['reference']['transcript']


def transcribe(root, model_path, language='es'):
    root, data = state(root); require_local(data)
    model_path = Path(model_path)
    if not model_path.is_dir():
        raise StudioError('Indica una carpeta de modelo local. Este comando no descarga modelos.')
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise StudioError('Whisper es opcional y falta. Lee installation.md antes de autorizar su instalación.') from exc
    source = checked(root, data['reference']['media'])
    model = WhisperModel(str(model_path), device='cpu', compute_type='int8', local_files_only=True)
    segments, info = model.transcribe(str(source), language=language, word_timestamps=True)
    rows = [{'start': s.start, 'end': s.end, 'text': s.text,
             'words': [{'start': w.start, 'end': w.end, 'text': w.word} for w in (s.words or [])]} for s in segments]
    with tempfile.TemporaryDirectory() as td:
        text_path = Path(td) / 'transcript.txt'
        text_path.write_text('\n'.join(r['text'] for r in rows), encoding='utf-8')
        if not rows:
            raise StudioError('No se detectó habla. El agente debe comprobar el audio antes de declararlo sin voz.')
        import_transcript(root, text_path, 'local-faster-whisper-generated', language)
        root, data = state(root)
        timed = Path(td) / 'segments.json'; write(timed, rows)
        data['reference']['transcript_segments'] = store_file(root, timed, 'ASR-original-segments')
        save(root, data, 'ASR-segments-preserved')
    return data['reference']['transcript']


def extract(root):
    from PIL import Image, ImageDraw, ImageFont
    root, data = state(root); require_local(data)
    media = checked(root, data['reference']['media'])
    if data.get('extraction'):
        checked(root, data['extraction']['index'])
        return data['extraction']
    if shutil.disk_usage(root).free < 1024 ** 3:
        raise StudioError('Se necesita al menos 1GB libre para extraer y revisar la referencia.')
    frames_raw = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
                                 '-show_entries', 'frame=best_effort_timestamp_time,key_frame', '-of', 'json', media]))
    raw_frames = frames_raw.get('frames', [])
    if not raw_frames or len(raw_frames) > 10800:
        raise StudioError('La referencia no tiene un índice válido o supera 10800 cuadros.')
    out = under(root, 'reference-frames/' + data['reference']['media']['sha256'][:16])
    if out.exists():
        raise StudioError('Existe una extracción incompleta. Consérvala y usa una carpeta de proyecto nueva o revisa su estado.')
    out.mkdir(parents=True)
    run(['ffmpeg', '-nostdin', '-v', 'error', '-i', media, '-vf', 'scale=640:-2',
         '-fps_mode', 'passthrough', '-q:v', '4', out / '%06d.jpg'], timeout=240)
    images = sorted(out.glob('*.jpg'))
    if len(images) != len(raw_frames):
        raise StudioError('La extracción no coincide con el índice de cuadros. No se marcó completa.')
    rows = []
    for n, (f, p) in enumerate(zip(raw_frames, images)):
        rows.append({'frame': n, 'pts': float(f['best_effort_timestamp_time']),
                     'path': str(p.relative_to(root)), 'sha256': sha(p)})
    sheets = []
    for first in range(0, len(images), 24):
        chunk = images[first:first + 24]
        canvas = Image.new('RGB', (6 * 160, 4 * 306), '#e8e8e8')
        d = ImageDraw.Draw(canvas)
        for k, path in enumerate(chunk):
            with Image.open(path) as im:
                im.thumbnail((154, 274)); x, y = (k % 6) * 160, (k // 6) * 306
                canvas.paste(im, (x + (160 - im.width) // 2, y))
                d.text((x + 5, y + 280), f'{first+k} / {rows[first+k]["pts"]:.3f}s', fill='black')
        path = out / f'contact-{first:06d}.jpg'; canvas.save(path, quality=88)
        sheets.append({'path': str(path.relative_to(root)), 'sha256': sha(path),
                       'first_frame': first, 'last_frame': first + len(chunk) - 1})
    index = out / 'index.json'; write(index, {'source_sha256': sha(media), 'frames': rows, 'contact_sheets': sheets})
    data['extraction'] = {'index': store_file(root, index, 'complete-frame-index'), 'frame_count': len(rows),
                          'contact_sheets': sheets, 'technical_coverage': 'Every decoded video frame, at width640; not semantic review.',
                          'semantic_review': 'pending'}
    save(root, data, 'all-reference-frames-extracted')
    return data['extraction']


def analyze(root, path):
    root, data = state(root)
    ref = data['reference']; checked(root, ref['media']); checked(root, ref['metadata'])
    if not ref.get('transcript'):
        raise StudioError('Falta transcript literal o declaración comprobada de fuente sin habla.')
    checked(root, ref['transcript'])
    a = read(path)
    if a.get('source_sha256') != ref['media']['sha256']:
        raise StudioError('El análisis pertenece a otro video.')
    if not all(a.get('literal_reading', {}).get(k) for k in ('title', 'description', 'transcript')):
        raise StudioError('La lectura literal íntegra todavía no está registrada.')
    expected = {s['path'] for s in data.get('extraction', {}).get('contact_sheets', [])}
    reviewed = set(a.get('reviewed_contact_sheets', []))
    if not expected or reviewed != expected:
        raise StudioError('Falta revisión declarada de alguna hoja. Extracción total no equivale a lectura visual.')
    for sheet in data['extraction']['contact_sheets']: checked(root, sheet)
    native = {r['path']:r for b in data.get('native_bursts',[]) for r in b['frames']}
    inspected = a.get('reviewed_native_frames',[])
    if not inspected or any(path not in native for path in inspected):
        raise StudioError('Falta inspección declarada de cuadros nativos. Extrae una ráfaga de la acción o letra de riesgo y mírala.')
    for native_path in inspected: checked(root,native[native_path])
    if not a.get('analyst') or not a.get('limitations') or not a.get('audio_review'):
        raise StudioError('Registra autor, límites y modo real de análisis del audio.')
    aspects = {r.get('aspect') for r in a.get('rules', [])}
    required = {'composition', 'palette', 'typography', 'camera', 'motion', 'narrative', 'sound'}
    if not required.issubset(aspects):
        raise StudioError('Faltan reglas de composición, color, letra, cámara, movimiento, narrativa o sonido.')
    for rule in a['rules']:
        if rule.get('status') not in ('observed', 'inferred', 'proposed') or not rule.get('evidence'):
            raise StudioError('Cada regla necesita estado y evidencia con cuadro/tiempo.')
    data['analysis'] = store_file(root, path, 'agent-semantic-analysis')
    data['extraction']['semantic_review'] = 'agent-attested-contact-sheets; see limitations and native bursts'
    save(root, data, 'semantic-analysis-recorded')
    return a


def style(root, path):
    root, data = state(root)
    a = read(checked(root, data['analysis'])); s = read(path)
    if a.get('compatibility', {}).get('supported') is not True or a.get('visual_type') not in ('2d', 'motion-graphics', '2.5d'):
        raise StudioError('Esta referencia no es compatible con el motor2D disponible. Propón otra técnica o una adaptación explícita; no prometas una clonación imposible.')
    if s.get('renderer') != 'pillow2d' or not s.get('name') or not s.get('rules') or not s.get('caption_preset'):
        raise StudioError('El estilo requiere nombre, reglas, caption_preset y renderer pillow2d.')
    if s.get('source_sha256') != data['reference']['media']['sha256']:
        raise StudioError('El estilo no está vinculado a esta referencia.')
    data['style'] = store_file(root, path, 'reusable-user-style')
    save(root, data, 'user-style-saved')
    return data['style']


def export_style(root, destination):
    root, data = state(root)
    src = checked(root, data['style']); dest = Path(destination)
    if dest.exists(): raise StudioError('El destino ya existe; no se reemplazó el estilo.')
    dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dest)
    return {'path': str(dest), 'sha256': sha(dest), 'scope': 'Rules only; no source media, face or voice bundled.'}


def voice_file(root, path):
    root, data = state(root); require_local(data)
    info = probe(path)
    if not any(s['codec_type'] == 'audio' for s in info['streams']): raise StudioError('El archivo no tiene pista de audio.')
    if info['duration'] < .25 or info['duration'] > 600:
        raise StudioError('La voz debe durar entre0.25s y10min; la respuesta original del proveedor se conserva.')
    original = store_file(root, path, 'user-narration-original')
    with tempfile.TemporaryDirectory() as td:
        normalized = Path(td) / 'voice.wav'
        run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-vn', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', normalized])
        level = voice_level(normalized)
        processed = Path(td) / 'voice-leveled.wav'
        run(['ffmpeg', '-nostdin', '-v', 'error', '-i', normalized, '-af', 'volume=' + str(level['gain_db']) + 'dB', '-c:a', 'pcm_s16le', processed])
        data['voice'] = {**store_file(root, processed, 'narration'), 'original': original, 'duration': info['duration'], 'tempo_factor': 1, 'level': level, 'demo_hold_seconds': max(0, 15 - info['duration']), 'hold_note': 'Si la voz termina antes de15s, el resto de la demo queda para acción visual/sonido o lectura; no se estiran palabras. El agente debe mostrar este cierre.'}
    save(root, data, 'voice-file-imported')
    return data['voice']


def voice_eleven(root, text_path, model='eleven_multilingual_v2'):
    root, data = state(root); require_local(data); consent(data, 'elevenlabs-generation')
    key, voice = os.environ.get('ELEVENLABS_API_KEY'), os.environ.get('ELEVENLABS_VOICE_ID')
    if not key or not voice:
        raise StudioError('Configura ELEVENLABS_API_KEY y ELEVENLABS_VOICE_ID en el entorno seguro. Nunca pegues la llave en chat.')
    import re
    if not re.fullmatch(r'[A-Za-z0-9]{10,64}', voice): raise StudioError('Voice ID no válido.')
    text = guard_secret(Path(text_path).read_text(encoding='utf-8')).strip()
    if not text or len(text) > 5000: raise StudioError('La narración debe tener entre1 y5000 caracteres.')
    payload = json.dumps({'text': text, 'model_id': model}).encode()
    with tempfile.TemporaryDirectory() as td:
        dest = Path(td) / 'voice.mp3'
        fetch('https://api.elevenlabs.io/v1/text-to-speech/' + voice, dest, max_bytes=30 * 1024 * 1024,
              method='POST', body=payload, headers={'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
        data['provider_voice_original'] = store_file(root, dest, 'ElevenLabs-original-preserved-before-validation')
        save(root, data, 'paid-provider-response-preserved')
        result = voice_file(root, dest)
    root, data = state(root); data['voice']['provider'] = {'name': 'ElevenLabs', 'model': model, 'voice_id_fingerprint': __import__('hashlib').sha256(voice.encode()).hexdigest(), 'text_sha256': sha(text_path)}
    save(root, data, 'paid-voice-generated-once')
    return result


def prepare(root, story_path, scene_path):
    root, data = state(root); require_local(data)
    if not data.get('style') or not data.get('voice'):
        raise StudioError('Primero guarda el estilo y aporta una voz. Una imagen muda no sustituye la demo.')
    if data['voice'].get('level', {}).get('needs_attention'):
        raise StudioError('Tu nota de voz sigue muy baja tras un ajuste conservador. Conservé el original; acerca el micrófono o revisa el audio antes de añadir efectos.')
    story = read(story_path)
    if not story.get('text') or not story.get('beats') or not story.get('captions'):
        raise StudioError('Guion incompleto: necesita texto, beats y captions con tiempos.')
    duration = data['voice']['duration']; last = 0
    for caption in story['captions']:
        if not 0 <= float(caption['start']) < float(caption['end']) <= duration + .05 or caption['start'] < last:
            raise StudioError('Tiempos de caption inválidos o solapados.')
        last = caption['end']
    if ' '.join(c['text'] for c in story['captions']).split() != story['text'].split():
        raise StudioError('El texto visible no coincide con el guion.')
    if Path(scene_path).suffix != '.py': raise StudioError('La escena debe ser un archivo Python local revisado por el agente.')
    code = Path(scene_path).read_text(encoding='utf-8'); guard_secret(code)
    if 'render_frame' not in code: raise StudioError('Falta la función render_frame(t,width,height,context).')
    data['story'] = store_file(root, story_path, 'original-story-and-timing')
    data['scene'] = store_file(root, scene_path, 'agent-authored-scene-code')
    save(root, data, 'story-and-scene-prepared')
    return {'next': 'render-demo', 'note': 'Scene code executes locally. Read it before running; this is not a code sandbox.'}


def reuse_style(source_workspace, destination):
    source, previous = state(source_workspace)
    for key in ('analysis', 'style'):
        checked(source, previous[key])
    destination = Path(destination).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise StudioError('El nuevo proyecto debe estar vacío.')
    destination.mkdir(parents=True, exist_ok=True)
    # Copy only the reference, semantic evidence and user style; never prior voice, story or exports.
    data = {'schema': 1, 'created': now(), 'settings': previous['settings'], 'consents': {},
            'reference': previous['reference'], 'extraction': previous['extraction'],
            'analysis': previous['analysis'], 'style': previous['style'], 'native_bursts': previous.get('native_bursts',[])}
    records = []
    def walk(item):
        if isinstance(item, dict):
            if 'path' in item and 'sha256' in item: records.append(item)
            for v in item.values(): walk(v)
        elif isinstance(item, list):
            for v in item: walk(v)
    walk(data)
    index = read(checked(source, previous['extraction']['index']))
    walk(index)
    for record in records:
        src = checked(source, record); dst = under(destination, record['path'])
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists(): shutil.copyfile(src, dst)
    (destination / '.gitignore').write_text('*\n', encoding='utf-8')
    save(destination, data, 'style-reused-with-reference-evidence')
    return {'workspace': str(destination), 'next': 'Confirma el entorno y añade una voz y una historia nuevas.'}


def provider_transcript(root, language):
    root, data = state(root)
    metadata = read(checked(root, data['reference']['metadata']))
    manual = metadata.get('subtitles', {})
    automatic = metadata.get('automatic_captions', {})
    tracks = manual.get(language) or automatic.get(language)
    if not tracks:
        available = sorted(set(manual) | set(automatic))
        raise StudioError('No hay pista exacta en ese idioma. Disponibles: ' + ', '.join(available[:30]) + '. Usa ASR o aporta el transcript literal.')
    choices = [t for t in tracks if t.get('ext') in ('vtt', 'srv3', 'ttml', 'json3') and t.get('url')]
    if not choices:
        raise StudioError('No hay formato de subtítulos compatible. Usa ASR local.')
    track = sorted(choices, key=lambda t: ('vtt','json3','srv3','ttml').index(t['ext']))[0]
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / ('transcript.' + track['ext'])
        fetch(track['url'], path, max_bytes=8*1024*1024)
        # Preserve the literal provider file, not a model summary or translated transcript.
        result = import_transcript(root, path, 'provider-auto' if language not in manual else 'provider-manual', language)
    return result


def voice_level(path):
    peaks = []; rms_windows = []
    with wave.open(str(path), 'rb') as f:
        if f.getsampwidth() != 2:
            raise StudioError('Se esperaba PCM16 para medir la voz.')
        while True:
            raw = f.readframes(f.getframerate())
            if not raw: break
            samples = array('h', raw)
            if sys.byteorder != 'little': samples.byteswap()
            peak = max(abs(v) for v in samples) / 32768
            rms = math.sqrt(sum(v*v for v in samples) / len(samples)) / 32768
            peaks.append(peak)
            if rms > 10 ** (-65/20): rms_windows.append(20*math.log10(rms))
    if not peaks or max(peaks) < 1e-6 or not rms_windows:
        raise StudioError('El audio está vacío o prácticamente en silencio. Aporta una nota de voz audible.')
    peak_db = 20*math.log10(max(peaks))
    values = sorted(rms_windows); active = values[min(len(values)-1, int(len(values)*.75))]
    gain = max(-18.0, min(12.0, -22.0-active, -2.0-peak_db))
    return {'method':'PCM RMS in active1s windows, percentile75; gain only, no echo/reverb/tempo processing.',
            'active_rms_dbfs_before':round(active,3),'peak_dbfs_before':round(peak_db,3),
            'gain_db':round(gain,3),'estimated_active_rms_dbfs_after':round(active+gain,3),
            'needs_attention':active+gain < -30}

def status(root):
    from .core import fingerprint
    from .render import gate_full
    root, data = state(root)
    result = {'workspace':str(root),'finished':False,'no_automatic_publication':True,
              'reference':data['reference'].get('capture_method','pending')}
    steps = [('environment','Confirma el acceso local a tu computador.'),('extraction','Captura la referencia, transcript y cuadros.'),
             ('analysis','Lee y analiza la referencia.'),('style','Guarda el estilo.'),('voice','Añade una voz.'),
             ('story','Prepara guion y escena.'),('scene','Prepara la escena.') ]
    for key,message in steps:
        if key not in data:
            result['next']=message;return result
    try: digest=fingerprint(root,data)
    except StudioError:
        result['next']='Una entrada cambió o falta. Repara el proyecto y prepara otra demo.';return result
    demo=data.get('demo',{})
    if demo.get('inputs_sha256')!=digest:
        result['next']='Crea una demo15s con las entradas actuales.';return result
    try: checked(root,demo)
    except StudioError:
        result['next']='La demo cambió o falta; revisa el archivo antes de continuar.';return result
    if data.get('demo_approval',{}).get('decision')=='reject':
        result['next']='La demo fue rechazada. Recoge el cambio, ajusta y presenta otra demo.';return result
    try: gate_full(root,data)
    except StudioError:
        result['next']='Muestra la demo actual y espera aprobación explícita.';return result
    full=data.get('full',{})
    if full.get('inputs_sha256')==digest:
        try:
            checked(root,full);result['finished']=True;result['next']='Video comprobado técnicamente, listo para revisión local; no publicado.';return result
        except StudioError: pass
    result['next']='La demo actual está aprobada; crea el video completo.';return result


def burst(root, first, last):
    root, data = state(root); require_local(data)
    total = data.get('extraction', {}).get('frame_count', 0)
    if not 0 <= first <= last < total or last-first+1 > 120:
        raise StudioError('La ráfaga debe contener1–120 cuadros dentro del video.')
    media = checked(root, data['reference']['media'])
    out = under(root, 'native-bursts/' + str(first) + '-' + str(last))
    if out.exists():
        match = next((b for b in data.get('native_bursts', []) if b['first']==first and b['last']==last),None)
        if match:
            for r in match['frames']: checked(root,r)
            return match
        raise StudioError('Ráfaga incompleta existente. Se conservó para revisar.')
    out.mkdir(parents=True)
    run(['ffmpeg','-nostdin','-v','error','-i',media,'-vf',f'select=between(n\\,{first}\\,{last})',
         '-fps_mode','vfr',out/'%06d.png'],timeout=180)
    paths=sorted(out.glob('*.png'))
    if len(paths)!=last-first+1: raise StudioError('La ráfaga no tiene todos los cuadros esperados.')
    row={'first':first,'last':last,'source_sha256':sha(media),'native_resolution':True,
         'frames':[{'frame':first+i,'path':str(path.relative_to(root)),'sha256':sha(path)} for i,path in enumerate(paths)]}
    data.setdefault('native_bursts',[]).append(row); save(root,data,'native-burst-extracted');return row
