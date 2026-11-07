#!/usr/bin/env python3
"""Portable skill CLI. No implicit installation, paid calls, upload or publication."""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from vss.core import StudioError, checked, configure_utf8_output, decision_record, doctor, fingerprint, read, save, state, write
from vss import workflow as w
from vss import recording


def parser():
    p = argparse.ArgumentParser(description='Video Style Studio · referencia → estilo → demo → aprobación → video')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    recording.add_commands(sub)
    q = sub.add_parser('install'); q.add_argument('--destination', required=True)
    q = sub.add_parser('init'); q.add_argument('--workspace', required=True); q.add_argument('--reference-url', required=True)
    q = sub.add_parser('confirm-environment'); q.add_argument('--workspace', required=True); q.add_argument('--evidence', required=True)
    q = sub.add_parser('consent'); q.add_argument('--workspace', required=True); q.add_argument('--scope', choices=['third-party-install', 'scrapecreators-request', 'elevenlabs-generation'], required=True); q.add_argument('--decision', choices=['approve', 'reject'], required=True); q.add_argument('--response-file', required=True)
    q = sub.add_parser('capture'); q.add_argument('--workspace', required=True); q.add_argument('--media-file'); q.add_argument('--metadata-file'); q.add_argument('--provider', choices=['yt-dlp', 'scrapecreators'], default='yt-dlp')
    q = sub.add_parser('transcript'); q.add_argument('--workspace', required=True); q.add_argument('--file', required=True); q.add_argument('--source', choices=['provider-captions', 'user-transcript', 'agent-ASR-generated', 'verified-no-speech'], required=True); q.add_argument('--language', default='es')
    q = sub.add_parser('provider-transcript'); q.add_argument('--workspace', required=True); q.add_argument('--language', required=True)
    q = sub.add_parser('transcribe'); q.add_argument('--workspace', required=True); q.add_argument('--model-path', required=True); q.add_argument('--language', default='es')
    q = sub.add_parser('burst'); q.add_argument('--workspace', required=True); q.add_argument('--start-frame', type=int, required=True); q.add_argument('--end-frame', type=int, required=True)
    q = sub.add_parser('extract'); q.add_argument('--workspace', required=True)
    for command in ('analyze', 'style'):
        q = sub.add_parser(command); q.add_argument('--workspace', required=True); q.add_argument('--file', required=True)
    q = sub.add_parser('reuse-style'); q.add_argument('--from-workspace', required=True); q.add_argument('--workspace', required=True)
    q = sub.add_parser('export-style'); q.add_argument('--workspace', required=True); q.add_argument('--output', required=True)
    q = sub.add_parser('voice-file'); q.add_argument('--workspace', required=True); q.add_argument('--file', required=True)
    q = sub.add_parser('voice-eleven'); q.add_argument('--workspace', required=True); q.add_argument('--text-file', required=True); q.add_argument('--model', default='eleven_multilingual_v2')
    q = sub.add_parser('prepare'); q.add_argument('--workspace', required=True); q.add_argument('--story', required=True); q.add_argument('--scene', required=True)
    for command in ('render-demo', 'render-full', 'status'):
        q = sub.add_parser(command); q.add_argument('--workspace', required=True)
    q = sub.add_parser('approve-demo'); q.add_argument('--workspace', required=True); q.add_argument('--decision', choices=['approve', 'reject'], required=True); q.add_argument('--response-file', required=True)
    q = sub.add_parser('_render-worker'); q.add_argument('--workspace', required=True); q.add_argument('--output', required=True); q.add_argument('--duration', type=float, required=True)
    return p


def main(argv=None):
    a = parser().parse_args(argv); c = a.command
    if c.startswith('recording-'): return recording.command(a)
    if c == 'doctor': return doctor()
    if c == 'install':
        src = Path(__file__).resolve().parent.parent; dest = Path(a.destination).expanduser().resolve() / src.name
        if dest.exists(): raise StudioError('La skill ya existe. No se sobrescribió; revisa versiones antes de actualizar.')
        dest.parent.mkdir(parents=True, exist_ok=True); shutil.copytree(src, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.venv', '.env', '.env.*', 'workspaces', 'outputs', '.DS_Store'))
        return {'installed': str(dest), 'dependencies_installed': False, 'next': 'Abre el agente y pide: usa la skill video-style-studio.'}
    if c == 'init': return w.init(a.workspace, a.reference_url)
    if c == 'capture': return w.capture(a.workspace, a.media_file, a.metadata_file, a.provider)
    if c == 'transcript': return w.import_transcript(a.workspace, a.file, a.source, a.language)
    if c == 'provider-transcript': return w.provider_transcript(a.workspace, a.language)
    if c == 'transcribe': return w.transcribe(a.workspace, a.model_path, a.language)
    if c == 'burst': return w.burst(a.workspace, a.start_frame, a.end_frame)
    if c == 'extract': return w.extract(a.workspace)
    if c == 'analyze': return w.analyze(a.workspace, a.file)
    if c == 'style': return w.style(a.workspace, a.file)
    if c == 'reuse-style': return w.reuse_style(a.from_workspace, a.workspace)
    if c == 'export-style': return w.export_style(a.workspace, a.output)
    if c == 'voice-file': return w.voice_file(a.workspace, a.file)
    if c == 'voice-eleven': return w.voice_eleven(a.workspace, a.text_file, a.model)
    if c == 'prepare': return w.prepare(a.workspace, a.story, a.scene)
    if c in ('render-demo', 'render-full', '_render-worker'):
        from vss.render import render, worker
        return worker(a.workspace, a.output, a.duration) if c == '_render-worker' else render(a.workspace, c == 'render-full')
    root, data = state(a.workspace)
    if c == 'confirm-environment':
        evidence = read(a.evidence)
        if evidence.get('execution_location') != 'user-desktop' or evidence.get('source') not in ('user-confirmation', 'runtime-attestation') or not evidence.get('evidence'):
            raise StudioError('La evidencia debe confirmar control local del computador; no basta detectar un proceso o navegador.')
        data['environment'] = evidence; save(root, data, 'environment-evidence-recorded'); return evidence
    if c == 'consent':
        data['consents'][a.scope] = decision_record(a.decision, a.response_file); save(root, data, 'consent-' + a.scope); return {'recorded': a.scope, 'decision': a.decision}
    if c == 'approve-demo':
        demo = data.get('demo')
        if not demo: raise StudioError('Todavía no hay una demo para aprobar.')
        checked(root, demo)
        if demo['inputs_sha256'] != fingerprint(root, data): raise StudioError('La demo ya no representa los archivos actuales.')
        data['demo_approval'] = {**decision_record(a.decision, a.response_file), 'demo_sha256': demo['sha256'], 'inputs_sha256': demo['inputs_sha256']}
        save(root, data, 'demo-' + a.decision); return data['demo_approval']
    if c == 'status': return w.status(a.workspace)

if __name__ == '__main__':
    configure_utf8_output()
    try:
        result = main()
        if result is not None: print(json.dumps(result, ensure_ascii=False, indent=2))
    except (StudioError, KeyError, ValueError, FileNotFoundError) as exc:
        message = str(exc) if isinstance(exc, StudioError) else 'Falta un archivo/campo o un dato no es válido. Revisa el contrato de entrada.'
        print(json.dumps({'ok': False, 'message': message}, ensure_ascii=False), file=sys.stderr); sys.exit(2)
