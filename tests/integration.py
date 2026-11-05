"""Run an isolated, credential-free vertical workflow. Tone in CI; pass --voice-file for spoken audio."""
import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from array import array
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = 'Una buena idea necesita movimiento. Primero cae, después encuentra equilibrio. Cada golpe tiene una respuesta. Así probamos una herramienta antes de construir una historia completa.'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--voice-file');a=ap.parse_args()
    out=Path(a.output).resolve()
    if out.exists() and any(out.iterdir()):raise RuntimeError('Use an empty output directory.')
    out.mkdir(parents=True,exist_ok=True)
    # Everything executed after this point lives in this copied package, not the origin checkout.
    copied=out/'installed'/'video-style-studio'
    subprocess.run([sys.executable,str(ROOT/'skills/video-style-studio/scripts/studio.py'),'install','--destination',str(out/'installed')],check=True,stdout=subprocess.PIPE)
    scene=out/'scene.py';shutil.copyfile(ROOT/'examples/scene.py',scene)
    cli=copied/'scripts/studio.py';project=out/'project'
    env={k:v for k,v in os.environ.items() if k in ('PATH','SystemRoot','WINDIR','TEMP','TMP','LANG','LC_ALL')};env['VSS_OFFLINE']='1'
    def call(*args,fail=False):
        p=subprocess.run([sys.executable,str(cli),*map(str,args)],cwd=out,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if fail:
            assert p.returncode!=0,(args,p.stdout);return
        if p.returncode:raise RuntimeError(p.stderr.decode())
        return json.loads(p.stdout)
    def dump(name,value):
        p=out/name;p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');return p
    caps=call('doctor');assert caps['render_capable'];assert caps['execution_location']=='unknown'
    # Original self-generated reference: no downloaded source or creator assets.
    ref=out/'reference.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','testsrc2=size=320x568:rate=12:duration=3','-c:v','libx264','-pix_fmt','yuv420p',str(ref)],check=True,env=env)
    metadata=dump('metadata.json',{'title':'Original motion fixture','description':'A self-generated moving test pattern; silent technical fixture, not a creative style claim.'})
    transcript=out/'reference-transcript.txt';transcript.write_text('Sin habla: referencia generada sin pista de audio.',encoding='utf-8')
    call('init','--workspace',project,'--reference-url','https://example.org/original-motion-fixture.mp4')
    call('capture','--workspace',project,'--media-file',ref,'--metadata-file',metadata,fail=True) # environment not attested
    evidence=dump('environment.json',{'execution_location':'user-desktop','source':'runtime-attestation','evidence':'Isolated integration harness explicitly supplies this fixture attestation; not production desktop detection.'})
    call('confirm-environment','--workspace',project,'--evidence',evidence)
    broken=out/'broken.mp4';broken.write_bytes(b'not a video')
    call('capture','--workspace',project,'--media-file',broken,fail=True)
    call('capture','--workspace',project,'--media-file',ref,'--metadata-file',metadata)
    call('transcript','--workspace',project,'--file',transcript,'--source','verified-no-speech')
    extraction=call('extract','--workspace',project)
    native=call('burst','--workspace',project,'--start-frame',0,'--end-frame',5)
    state=json.loads((project/'project.json').read_text());source_sha=state['reference']['media']['sha256']
    rules=[{'aspect':key,'status':'observed' if key!='narrative' else 'proposed','evidence':'Fixture frames0-35; automated test declarations, not human creative analysis.','rule':'Original generic motion exercise; user style must be measured independently.'} for key in ['composition','palette','typography','camera','motion','narrative','sound']]
    analysis=dump('analysis.json',{'source_sha256':source_sha,'analyst':'integration-fixture (not human review)',
        'literal_reading':{'title':True,'description':True,'transcript':True},'reviewed_contact_sheets':[s['path'] for s in extraction['contact_sheets']],
        'reviewed_native_frames':[f['path'] for f in native['frames']], 'visual_type':'motion-graphics','compatibility':{'supported':True,'stack':'pillow2d'},'rules':rules,
        'limitations':['Automated fixture for pipeline acceptance; does not establish aesthetic or semantic quality.'],
        'audio_review':{'mode':'ffprobe','finding':'No audio stream in generated reference.'}})
    call('analyze','--workspace',project,'--file',analysis)
    style=dump('style.json',{'name':'Original motion exercise','source_sha256':source_sha,'renderer':'pillow2d','colors':['#241C35','#FFB454','#B8E0D2'],
        'rules':rules,'caption_preset':{'size_ratio':.046,'y_ratio':.83,'color':'#FFFFFF','outline':'#241C35'}})
    call('style','--workspace',project,'--file',style)
    audio=out/'narration.wav'
    if a.voice_file:
        subprocess.run(['ffmpeg','-v','error','-i',str(Path(a.voice_file).resolve()),'-ar','48000','-ac','1',str(audio)],check=True,env=env)
        audio_kind='provided spoken-audio file; fixture text alignment must be reviewed separately'
    else:
        sr=16000;pcm=array('h',[round(1800*math.sin(2*math.pi*220*n/sr)*(.3+.7*math.sin(math.pi*(n/sr%1))**2)) for n in range(sr*16)])
        if sys.byteorder!='little':pcm.byteswap()
        with wave.open(str(audio),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())
        audio_kind='CI tone fixture; not speech, accent, timbre or lexical validation'
    voice=call('voice-file','--workspace',project,'--file',audio)
    chunks=[s.strip()+'.' for s in TEXT.split('.') if s.strip()];duration=voice['duration'];span=min(duration,15)/len(chunks)
    story=dump('story.json',{'text':TEXT,'beats':[{'start':i*span,'end':(i+1)*span,'visible_action':'Fall, contact, damped rebound','meaning':t} for i,t in enumerate(chunks)],
        'captions':[{'text':t,'start':i*span,'end':(i+1)*span} for i,t in enumerate(chunks)],
        'events':[{'frame':round(t*30),'kind':'impact','gain':.13} for t in (1.2,6.2,11.2)]})
    call('prepare','--workspace',project,'--story',story,'--scene',scene)
    # Keep the acceptance render fast while exercising the real frame/audio exporter.
    state=json.loads((project/'project.json').read_text());state['settings'].update(width=360,height=640)
    (project/'project.json').write_text(json.dumps(state),encoding='utf-8')
    call('render-full','--workspace',project,fail=True)
    demo=call('render-demo','--workspace',project);assert demo['frames']==450 and demo['duration']==15 and demo['audio']
    answer=out/'fixture-approval.txt';answer.write_text('Sí, no cambies nada. Aprobación automatizada del fixture técnico, no aprobación humana.',encoding='utf-8')
    call('approve-demo','--workspace',project,'--decision','approve','--response-file',answer)
    # Changed input invalidates an approval. Restore exact bytes afterwards.
    st=json.loads((project/'project.json').read_text());st['settings']['width']=362;(project/'project.json').write_text(json.dumps(st))
    call('render-full','--workspace',project,fail=True);st['settings']['width']=360;(project/'project.json').write_text(json.dumps(st))
    full=call('render-full','--workspace',project)
    # Reuse actually carries evidence/style and clears narration, story and approval.
    reused=out/'next-story';call('reuse-style','--from-workspace',project,'--workspace',reused)
    new=json.loads((reused/'project.json').read_text());assert 'style' in new and all(k not in new for k in ('voice','story','scene','demo_approval','full'))
    report={'passed':True,'isolated_cli':str(cli),'network':'VSS_OFFLINE=1; no credentials passed','reference_method':'imported-user-file; never claimed as download',
        'reference_frames':extraction['frame_count'],'audio_kind':audio_kind,'demo':demo,'full':full,'gate_rejected_before_approval':True,'gate_rejected_after_input_change':True,'style_reuse':True,
        'limitations':'Technical acceptance test. Automated semantic/approval fixtures are labeled and are not real user approvals.'}
    dump('integration-report.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
