"""Reviewed cuts and captions for an existing recording; originals are immutable."""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from .core import StudioError, checked, decision_record, probe, read, require_local, run, save, sha, state, store_file, write
from .render import captions

def add_commands(sub):
    for command in ('recording-import','recording-silences','recording-prepare','recording-demo','recording-approve','recording-full'):
        q=sub.add_parser(command);q.add_argument('--workspace',required=True)
        if command=='recording-import':q.add_argument('--file',required=True)
        if command=='recording-prepare':q.add_argument('--plan',required=True)
        if command=='recording-approve':
            q.add_argument('--decision',choices=['approve','reject'],required=True)
            q.add_argument('--response-file',required=True)

def validate_plan(plan,duration):
    segments=plan.get('segments',[])
    if not segments or len(segments)>100:raise StudioError('Define entre 1 y 100 segmentos que conservar; nunca una orden de borrar el original.')
    total=0.;last=0.
    for s in segments:
        start,end=float(s['start']),float(s['end'])
        if not all(math.isfinite(v) for v in (start,end)) or not 0<=start<end<=duration+.001 or start<last:
            raise StudioError('Segmentos fuera de orden, solapados o fuera de la grabación.')
        # A frame clock keeps cuts/captions/audio on the same output duration.
        if any(abs(v*30-round(v*30))>.001 for v in (start,end)):
            raise StudioError('Ajusta los cortes a cuadros de 1/30 s antes de preparar.')
        total+=end-start;last=end
    if not 15<=total<=600:raise StudioError('El corte revisable debe durar entre 15 y 600 segundos.')
    last=0.
    for c in plan.get('captions',[]):
        start,end=float(c['start']),float(c['end'])
        if not all(math.isfinite(v) for v in (start,end)) or not last<=start<end<=total+.001 or not isinstance(c.get('text'),str) or not c['text'].strip():
            raise StudioError('Revisa captions: tiempos del montaje final, sin solapamientos y con texto.')
        last=end
    if not isinstance(plan.get('reason'),str) or not plan['reason'].strip():
        raise StudioError('Explica qué pausas/cortes elegiste y por qué; el detector no decide por ti.')
    return round(total*30)/30

def fingerprint(root,data):
    rec=data.get('recording',{})
    for key in ('source','plan'):
        if key not in rec:raise StudioError('Primero importa una grabación y prepara su plan de edición.')
        checked(root,rec[key])
    package=Path(__file__).resolve().parents[2]
    payload={k:rec[k] for k in ('source','plan')}
    payload.update(renderer=sha(Path(__file__)),captions=sha(Path(__file__).with_name('render.py')),font=sha(package/'assets/fonts/NotoSans.ttf'))
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()

def full_gate(root,data):
    rec=data['recording'];digest=fingerprint(root,data);demo=rec.get('demo',{});approval=rec.get('approval',{})
    if approval.get('decision')!='approve' or not demo:raise StudioError('Muestra primero la demo de edición y registra la aprobación real.')
    checked(root,demo)
    if demo.get('inputs_sha256')!=digest or approval.get('inputs_sha256')!=digest or approval.get('demo_sha256')!=demo['sha256']:
        raise StudioError('Cambió la grabación o el montaje. Hace falta otra demo y aprobación.')
    return digest

def render(root,data,full=False):
    rec=data['recording'];digest=full_gate(root,data) if full else fingerprint(root,data)
    source=checked(root,rec['source']);plan=read(checked(root,rec['plan']))
    total=validate_plan(plan,probe(source)['duration']);duration=total if full else 15.
    out=root/'recording-renders'/((('full-' if full else 'demo-')+digest[:16]));out.mkdir(parents=True,exist_ok=True)
    final=out/'video.mp4';field='full' if full else 'demo'
    if final.exists():
        record=rec.get(field,{})
        if record.get('path')==str(final.relative_to(root)):
            checked(root,record);return record
        raise StudioError('Hay un render sin recibo; se conservó. Inspecciónalo antes de repetir.')
    info=probe(source);video=next(s for s in info['streams'] if s['codec_type']=='video')
    width,height=int(video['width']),int(video['height'])
    if width%2 or height%2 or width>2160 or height>3840:raise StudioError('Adapta primero el tamaño a dimensiones pares, máximo 2160 × 3840.')
    if any(s.get('side_data_type')=='Display Matrix' and s.get('rotation',0) for s in video.get('side_data_list',[])):
        raise StudioError('La grabación usa rotación de cámara. Crea una copia con orientación aplicada y reimpórtala; conserva el original.')
    filters=[];labels=[]
    # Render only the segment portions necessary for the selected preview/full.
    remaining=duration
    for n,s in enumerate(plan['segments']):
        if remaining<=.0001:break
        start=s['start'];span=min(s['end']-start,remaining);end=start+span
        filters.extend([f'[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,fps=30,setsar=1[v{n}]',
                        f'[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,aresample=48000[a{n}]'])
        labels.append(f'[v{n}][a{n}]');remaining-=span
    filters.append(''.join(labels)+f'concat=n={len(labels)}:v=1:a=1[v][a]')
    graph=out/'cuts.ffscript';graph.write_text(';'.join(filters),encoding='utf-8')
    cut=out/'cut.mp4'
    run(['ffmpeg','-nostdin','-v','error','-n','-noautorotate','-i',source,'-filter_complex',';'.join(filters),'-map','[v]','-map','[a]',
         '-t',duration,'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','320k','-ar','48000','-ac','2',cut],timeout=max(180,int(duration*15)))
    if plan.get('captions'):
        from PIL import Image
        picture=out/'captioned.mp4'
        dec=subprocess.Popen(['ffmpeg','-v','error','-i',str(cut),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        enc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(picture)],stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
        try:
            for n in range(round(duration*30)):
                raw=dec.stdout.read(width*height*3)
                if len(raw)!=width*height*3:raise StudioError('El corte contiene menos cuadros de lo esperado.')
                im=Image.frombytes('RGB',(width,height),raw)
                captions(im,n/30,plan,{'caption_preset':plan.get('caption_preset',{'size_ratio':.045,'y_ratio':.84})})
                enc.stdin.write(im.tobytes())
            enc.stdin.close();dec.stdout.close()
            if enc.wait(timeout=120) or dec.wait(timeout=120):raise StudioError('No terminó la composición de captions.')
        except BaseException:
            enc.kill();dec.kill();enc.wait();dec.wait();raise
        run(['ffmpeg','-nostdin','-v','error','-n','-i',picture,'-i',cut,'-map','0:v','-map','1:a','-c','copy','-movflags','+faststart',final])
    else:
        run(['ffmpeg','-nostdin','-v','error','-n','-i',cut,'-c','copy','-movflags','+faststart',final])
    result=probe(final);v=next(s for s in result['streams'] if s['codec_type']=='video');audio=next(s for s in result['streams'] if s['codec_type']=='audio')
    if abs(result['duration']-duration)>.06 or int(v.get('nb_frames',-1))!=round(duration*30) or audio['channels']!=2:
        raise StudioError('La duración, cuadros o audio del export no coinciden.')
    run(['ffmpeg','-v','error','-i',final,'-f','null','-'],timeout=max(180,int(duration*3)))
    rec[field]={'path':str(final.relative_to(root)),'sha256':sha(final),'inputs_sha256':digest,'duration':duration,'frames':round(duration*30),'full_decode':True,'review_state':'technical-only; show the edited recording to the user'}
    save(root,data,'recording-'+field+'-rendered');write(out/'receipt.json',rec[field]);return rec[field]

def command(a):
    root,data=state(a.workspace);require_local(data);c=a.command
    if c=='recording-import':
        p=Path(a.file).resolve();info=probe(p)
        if not 15<=info['duration']<=600 or not all(any(s['codec_type']==k for s in info['streams']) for k in ('video','audio')):
            raise StudioError('Aporta una grabación con video y voz de 15 a 600 segundos.')
        if data.get('recording'):raise StudioError('Ya hay una grabación; usa un proyecto nuevo para conservar su edición.')
        data['recording']={'source':store_file(root,p,'Original recording'),'duration':info['duration']};save(root,data,'recording-imported');return data['recording']
    if not data.get('recording'):raise StudioError('Primero importa una grabación con recording-import.')
    rec=data['recording']
    if c=='recording-silences':
        import re
        source=checked(root,rec['source'])
        p=subprocess.run(['ffmpeg','-v','info','-i',str(source),'-af','silencedetect=noise=-38dB:d=0.35','-vn','-f','null','-'],capture_output=True,timeout=300)
        if p.returncode:raise StudioError('No se pudo analizar el audio de la grabación.')
        events=[{'kind':k,'seconds':float(t)} for k,t in re.findall(r'silence_(start|end): ([\d.]+)',p.stderr.decode(errors='replace'))]
        result={'source_sha256':rec['source']['sha256'],'events':events,'threshold_db':-38,'min_seconds':.35,'warning':'Candidatos acústicos; revisar frases, respiraciones y pausas expresivas. No se aplicó ningún corte.'}
        write(root/'recording-silences.json',result);return result
    if c=='recording-prepare':
        plan=read(a.plan);duration=validate_plan(plan,rec['duration']);rec['plan']=store_file(root,a.plan,'Reviewed recording edit plan');save(root,data,'recording-plan-prepared');return {'edited_seconds':duration,'source_seconds':rec['duration'],'next':'recording-demo'}
    if c=='recording-approve':
        demo=rec.get('demo')
        if not demo or demo.get('inputs_sha256')!=fingerprint(root,data):raise StudioError('Primero crea una demo vigente.')
        checked(root,demo);rec['approval']={**decision_record(a.decision,a.response_file),'inputs_sha256':demo['inputs_sha256'],'demo_sha256':demo['sha256']};save(root,data,'recording-'+a.decision);return rec['approval']
    return render(root,data,full=c=='recording-full')
