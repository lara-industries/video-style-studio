import importlib.util
import json
import math
import os
import random
import subprocess
import sys
import wave
from array import array
from pathlib import Path
from .core import StudioError, checked, fingerprint, probe, read, require_compatible, require_local, run, save, sha, state, under, write


def caption_font(size):
    from PIL import ImageFont
    return ImageFont.truetype(str(Path(__file__).resolve().parents[2] / 'assets/fonts/NotoSans.ttf'), size=size)


def captions(frame, t, story, style):
    from PIL import ImageDraw, ImageFont
    active = next((c for c in story['captions'] if c['start'] <= t < c['end']), None)
    if not active: return
    w, h = frame.size
    preset = style['caption_preset']; size = max(12, round(w * float(preset.get('size_ratio', .045))))
    font = caption_font(size)
    d = ImageDraw.Draw(frame); max_width = w * .84; lines = []; line = ''
    for token in active['text'].split():
        test = (line + ' ' + token).strip()
        if d.textlength(test, font=font) > max_width and line:
            lines.append(line); line = token
        else: line = test
    if line: lines.append(line)
    if len(lines) > 3: raise StudioError('Una línea de captions ocupa más de tres renglones. Divide el cue y revisa sus tiempos.')
    y = round(h * float(preset.get('y_ratio', .84)))
    if not .10 * h <= y <= .90 * h: raise StudioError('Caption fuera del área segura.')
    stroke = max(1, size // 18)
    boxes = [d.textbbox((0, n * (size + 8)), text, font=font, stroke_width=stroke) for n, text in enumerate(lines)]
    top = min(b[1] for b in boxes); bottom = max(b[3] for b in boxes)
    if bottom - top > .80 * h:
        raise StudioError('El bloque completo de captions no cabe en el área segura. Reduce tamaño o divide el cue.')
    y = min(y, math.floor(.90 * h - bottom))
    y = max(y, math.ceil(.10 * h - top))
    for n, text in enumerate(lines):
        x = round((w - d.textlength(text, font=font)) / 2)
        d.text((x, y + n * (size + 8)), text, font=font, fill=preset.get('color', '#FFFFFF'),
               stroke_width=stroke, stroke_fill=preset.get('outline', '#161616'))


def synth_events(path, duration, fps, events):
    rate = 48000; samples = array('f', [0]) * math.ceil(duration * rate); rng = random.Random(7)
    for e in events:
        start = int(e['frame']) / fps
        gain = float(e.get('gain', .12))
        if e.get('kind') not in ('impact', 'tick', 'whoosh') or not 0 <= gain <= .5 or start < 0:
            raise StudioError('Evento sonoro fuera de contrato.')
        if start >= duration: continue
        span = {'impact': .22, 'tick': .05, 'whoosh': .28}[e['kind']]
        for n in range(min(round(span * rate), len(samples) - round(start * rate))):
            t = n / rate; env = min(1, t / .002) * math.exp(-t / (span / 5))
            tone = math.sin(2 * math.pi * (105 if e['kind'] == 'impact' else 1050) * t)
            val = rng.uniform(-1, 1) if e['kind'] == 'whoosh' else .7 * tone + .3 * rng.uniform(-1, 1)
            samples[round(start * rate) + n] += gain * val * env
    pcm = array('h', [max(-32767, min(32767, round(s * 32767))) for s in samples])
    if sys.byteorder != 'little': pcm.byteswap()
    with wave.open(str(path), 'wb') as out:
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(rate); out.writeframes(pcm.tobytes())


def worker(root, destination, duration):
    from PIL import Image
    root, data = state(root); scene = checked(root, data['scene']); story = read(checked(root, data['story'])); style = read(checked(root, data['style']))
    require_compatible(root, data)
    width, height, fps = [int(data['settings'][k]) for k in ('width', 'height', 'fps')]
    if not 128 <= width <= 1920 or not 128 <= height <= 2160 or width % 2 or height % 2 or fps not in (24, 25, 30, 60):
        raise StudioError('Dimensiones/fps no admitidos.')
    frames = math.ceil(duration * fps)
    spec = importlib.util.spec_from_file_location('project_scene', scene)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    if not callable(getattr(module, 'render_frame', None)): raise StudioError('Escena sin render_frame.')
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{width}x{height}',
           '-r', str(fps), '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', str(destination)]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        context = {'style': style, 'story': story, 'events': story.get('events', []), 'workspace': str(root), 'fps': fps}
        for n in range(frames):
            im = module.render_frame(n / fps, width, height, context)
            if not isinstance(im, Image.Image) or im.size != (width, height): raise StudioError('La escena devolvió una imagen con tamaño incorrecto.')
            im = im.convert('RGB'); captions(im, n / fps, story, style)
            process.stdin.write(im.tobytes())
        process.stdin.close()
        if process.wait(timeout=120): raise StudioError('FFmpeg no terminó el render.')
    except BaseException:
        process.kill(); process.wait(); raise


def gate_full(root, data):
    digest = fingerprint(root, data); demo = data.get('demo', {}); approval = data.get('demo_approval', {})
    if not demo or approval.get('decision') != 'approve': raise StudioError('Primero muestra la demo15s y registra la aprobación real del usuario.')
    checked(root, demo)
    if demo.get('inputs_sha256') != digest or approval.get('inputs_sha256') != digest or approval.get('demo_sha256') != demo['sha256']:
        raise StudioError('Cambió voz, escena, estilo, guion o referencia desde la aprobación. Renderiza y aprueba otra demo.')
    return digest


def render(root, full=False):
    root, data = state(root); require_local(data)
    digest = gate_full(root, data) if full else fingerprint(root, data)
    voice = checked(root, data['voice']); story = read(checked(root, data['story']))
    fps = data['settings']['fps']; duration = max(15.0, math.ceil(data['voice']['duration'] * fps) / fps) if full else 15.0
    if not 15 <= duration <= 600: raise StudioError('Duración fuera del rango admitido.')
    name = ('full' if full else 'demo') + '-' + digest[:16]
    out = under(root, 'renders/' + name); out.mkdir(parents=True, exist_ok=True)
    final = out / 'video.mp4'
    field = 'full' if full else 'demo'
    if final.exists():
        record = data.get(field, {})
        if record.get('path') == str(final.relative_to(root)):
            checked(root, record); return record
        raise StudioError('Ya existe un render sin recibo completo. Se conservó; usa un proyecto nuevo o investiga el fallo.')
    # Only reviewed, agent-authored local code is run. This is not a sandbox.
    # Do not pass provider secrets to scene code or child FFmpeg processes.
    safe_env = {k: v for k, v in os.environ.items() if k in ('PATH', 'SystemRoot', 'WINDIR', 'TEMP', 'TMP', 'LANG', 'LC_ALL')}
    cli = Path(__file__).resolve().parents[1] / 'studio.py'
    run([sys.executable, cli, '_render-worker', '--workspace', root, '--output', out / 'picture.mp4', '--duration', str(duration)],
        timeout=max(180, int(duration * 40)), env=safe_env)
    synth_events(out / 'effects.wav', duration, fps, story.get('events', []))
    temp = out / 'assembling.mp4'
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', out / 'picture.mp4', '-i', voice, '-i', out / 'effects.wav',
         '-filter_complex', '[1:a]apad[a];[a][2:a]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89:latency=1[m]',
         '-map', '0:v:0', '-map', '[m]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
         '-t', str(duration), '-movflags', '+faststart', temp], timeout=max(120, int(duration * 4)))
    info = probe(temp); video = next(s for s in info['streams'] if s['codec_type'] == 'video'); audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    if abs(info['duration'] - duration) > .05 or int(video.get('nb_frames', -1)) != round(duration * fps) or int(audio['channels']) != 2:
        raise StudioError('El export no coincide con duración, cuadros o canales esperados.')
    run(['ffmpeg', '-v', 'error', '-i', temp, '-f', 'null', '-'], timeout=max(120, int(duration * 3)))
    temp.rename(final)
    data[field] = {'path': str(final.relative_to(root)), 'sha256': sha(final), 'inputs_sha256': digest,
                   'duration': duration, 'frames': round(duration * fps), 'full_decode': True,
                   'review_state': 'technical-only; show artifact to user', 'audio': True}
    save(root, data, field + '-rendered')
    write(out / 'render-receipt.json', data[field])
    return data[field]
