import hashlib
import json
import os
import socket
import sys
import tempfile
import shutil
import wave
import math
from array import array
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/video-style-studio/scripts'))
from vss.core import StudioError, decision_record, doctor, fingerprint, guard_secret, sha, state, store_file, under, write
from vss.network import public_url, fetch, is_social, social_metadata
from vss.workflow import init, style, voice_eleven, voice_file, voice_level, status, prepare, reuse_style
from vss.render import gate_full, render, captions, caption_font

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name) / 'project'
        self.data = init(self.root, 'https://example.org/reference.mp4')
    def tearDown(self): self.tmp.cleanup()
    def test_url_required_and_local_blocked(self):
        for url in ('', 'file:///etc/passwd', 'http://127.0.0.1/x', 'http://169.254.169.254/x', 'http://[::1]/', 'https://user:pass@example.org/x', 'https://example.org:8080/x', 'http://localhost/x', 'http://foo.local/x'):
            with self.subTest(url=url), self.assertRaises(StudioError): public_url(url, resolve=False)
    def test_dns_private_and_mixed_answers_blocked(self):
        with patch('socket.getaddrinfo', return_value=[(2,1,6,'',('93.184.216.34',443)),(2,1,6,'',('10.0.0.1',443))]):
            with self.assertRaises(StudioError): public_url('https://example.org/video.mp4')
    def test_redirect_is_rechecked(self):
        class Response:
            status=302
            def getheader(self,k,default=None): return 'http://127.0.0.1/private' if k=='Location' else default
        class Connection:
            def __init__(self,*a,**k): pass
            def request(self,*a,**k): pass
            def getresponse(self): return Response()
            def close(self): pass
        with patch('socket.getaddrinfo', return_value=[(2,1,6,'',('93.184.216.34',443))]), patch('vss.network.PinnedHTTPS',Connection):
            with self.assertRaises(StudioError): fetch('https://example.org/x', self.root/'redirect.mp4')
    def test_secret_never_saved(self):
        value='test_secret_abcdefghijklmnopqrstuvwxyz'
        with patch.dict(os.environ,{'ELEVENLABS_API_KEY':value}):
            with self.assertRaises(StudioError): write(self.root/'leak.json',{'text':value})
        self.assertFalse((self.root/'leak.json').exists())
    def test_path_escape_and_symlink(self):
        with self.assertRaises(StudioError): under(self.root,'../outside')
        try: (self.root/'escape').symlink_to(self.root.parent,target_is_directory=True)
        except OSError: return
        with self.assertRaises(StudioError): under(self.root,'escape/outside')
    def test_capability_not_app_detection(self):
        d=doctor(); self.assertEqual(d['execution_location'],'unknown'); self.assertEqual(d['desktop_application'],'unknown')
    def test_paid_provider_requires_consent(self):
        with patch('vss.workflow.require_local'):
            with self.assertRaises(StudioError): voice_eleven(self.root,self.root/'missing.txt')
    def test_no_implicit_approval_and_natural_yes(self):
        p=self.root/'answer.txt';p.write_text('Sí, no cambies nada. Me gusta.',encoding='utf-8')
        self.assertEqual(decision_record('approve',p)['decision'],'approve')
        with self.assertRaises(StudioError): decision_record('unclear',p)
        with self.assertRaises(StudioError): gate_full(self.root,self.data)
    def full_inputs(self):
        for k in ('analysis','style','voice','story','scene'):
            p=self.root/(k+'.txt');p.write_text(k);self.data[k]=store_file(self.root,p,k)
        ref=self.root/'reference.dat';ref.write_bytes(b'reference');self.data['reference']['media']=store_file(self.root,ref,'reference')
        for key,value in [('analysis',{'source_sha256':sha(ref),'visual_type':'motion-graphics','compatibility':{'supported':True}}),('style',{'source_sha256':sha(ref),'renderer':'pillow2d'})]:
            path=self.root/(key+'.json');write(path,value);self.data[key]=store_file(self.root,path,key)
        digest=fingerprint(self.root,self.data); p=self.root/'demo.mp4';p.write_bytes(b'fake-unit-only')
        self.data['demo']={**store_file(self.root,p,'demo'),'inputs_sha256':digest}
        self.data['demo_approval']={'decision':'approve','inputs_sha256':digest,'demo_sha256':sha(p)}
    def test_approval_bound_to_artifact_and_inputs(self):
        self.full_inputs(); gate_full(self.root,self.data)
        self.data['settings']['width']=1080
        with self.assertRaises(StudioError): gate_full(self.root,self.data)
    def test_tampered_demo_rejected(self):
        self.full_inputs(); (self.root/self.data['demo']['path']).write_bytes(b'changed')
        with self.assertRaises(StudioError): gate_full(self.root,self.data)
    def test_live_action_incompatible(self):
        p=self.root/'analysis.json';write(p,{'visual_type':'live-action','compatibility':{'supported':True}})
        self.data['analysis']=store_file(self.root,p,'analysis');write(self.root/'project.json',self.data)
        s=self.root/'style.json';write(s,{'name':'test','renderer':'pillow2d'})
        with self.assertRaises(StudioError): style(self.root,s)
    def test_changed_analysis_blocks_existing_style_everywhere(self):
        self.full_inputs();old_style=self.data['style'].copy()
        path=self.root/'new-analysis.json';write(path,{'source_sha256':self.data['reference']['media']['sha256'],'visual_type':'live-action','compatibility':{'supported':False}})
        self.data['analysis']=store_file(self.root,path,'new-analysis');write(self.root/'project.json',self.data)
        with self.assertRaisesRegex(StudioError,'análisis vigente'): fingerprint(self.root,self.data)
        with patch('vss.workflow.require_local'),self.assertRaisesRegex(StudioError,'análisis vigente'): prepare(self.root,self.root/'unused.json',self.root/'unused.py')
        with patch('vss.render.require_local'),self.assertRaisesRegex(StudioError,'análisis vigente'): render(self.root)
        with self.assertRaisesRegex(StudioError,'análisis vigente'): reuse_style(self.root,self.root.parent/'next')
        _,saved=state(self.root);self.assertEqual(saved['style'],old_style)
        self.assertTrue((self.root/old_style['path']).exists());self.assertFalse((self.root.parent/'next').exists())
    def test_spanish_glyphs_are_present(self):
        font=caption_font(40);missing=bytes(font.getmask('\u0378'))
        for char in 'áéíóúüñÁÉÍÓÚÜÑ¿¡':
            with self.subTest(char=char): self.assertNotEqual(bytes(font.getmask(char)),missing)
    def test_complete_caption_stays_inside_vertical_safe_area(self):
        from PIL import Image
        frame=Image.new('RGB',(360,640),'black')
        story={'captions':[{'start':0,'end':1,'text':'Esta prueba comprueba que las letras caben en tres renglones dentro del cuadro.'}]}
        preset={'caption_preset':{'size_ratio':.05,'y_ratio':.9,'color':'white','outline':'white'}}
        captions(frame,0,story,preset)
        box=frame.getbbox();self.assertIsNotNone(box);self.assertGreaterEqual(box[1],64);self.assertLessEqual(box[3],577)
    def test_resume_preserves_reference(self):
        again=init(self.root,'https://example.org/reference.mp4');self.assertEqual(again['created'],self.data['created'])
        with self.assertRaises(StudioError):init(self.root,'https://example.org/other.mp4')
    def test_status_reject_and_stale_full(self):
        self.full_inputs();self.data.update(environment={},extraction={});self.data['full']=dict(self.data['demo'])
        write(self.root/'project.json',self.data);self.assertTrue(status(self.root)['finished'])
        self.data['demo_approval']['decision']='reject';write(self.root/'project.json',self.data)
        result=status(self.root);self.assertFalse(result['finished']);self.assertIn('rechazada',result['next'])
        self.data['demo_approval']['decision']='approve';self.data['settings']['width']=1080;write(self.root/'project.json',self.data)
        result=status(self.root);self.assertFalse(result['finished']);self.assertIn('actuales',result['next'])
    def wav(self,name,amplitude=7000,seconds=2):
        p=self.root/name;sr=16000;x=array('h',[round(amplitude*math.sin(2*math.pi*220*n/sr)) for n in range(int(sr*seconds))])
        if sys.byteorder!='little':x.byteswap()
        with wave.open(str(p),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(x.tobytes())
        return p
    def test_short_voice_kept_with_explicit_hold(self):
        p=self.wav('short.wav')
        def fake_convert(args,*a,**k):shutil.copyfile(args[args.index('-i')+1],args[-1]);return b''
        with patch('vss.workflow.require_local'),patch('vss.workflow.probe',return_value={'duration':2,'streams':[{'codec_type':'audio'}]}),patch('vss.workflow.run',side_effect=fake_convert):
            result=voice_file(self.root,p)
        self.assertEqual(result['demo_hold_seconds'],13);self.assertEqual(result['tempo_factor'],1)
        self.assertTrue((self.root/result['original']['path']).is_file())
    def test_very_quiet_voice_requests_review(self):
        result=voice_level(self.wav('quiet.wav',amplitude=100))
        self.assertLessEqual(result['gain_db'],12);self.assertTrue(result['needs_attention'])
    def test_paid_response_survives_validation_failure(self):
        self.data['consents']['elevenlabs-generation']={'decision':'approve','verbatim':'Sí, genera esa voz.'};write(self.root/'project.json',self.data)
        text=self.root/'text.txt';text.write_text('Hola mundo')
        def fake_fetch(url,destination,**kwargs):Path(destination).write_bytes(b'provider-response');return {}
        with patch.dict(os.environ,{'ELEVENLABS_API_KEY':'fake-unit-credential','ELEVENLABS_VOICE_ID':'abcdefghijklmno'}),patch('vss.workflow.require_local'),patch('vss.workflow.fetch',side_effect=fake_fetch),patch('vss.workflow.voice_file',side_effect=StudioError('invalid media')):
            with self.assertRaises(StudioError):voice_eleven(self.root,text)
        _,saved=state(self.root);record=saved['provider_voice_original'];self.assertEqual((self.root/record['path']).read_bytes(),b'provider-response')
    def test_metadata_extractor_receives_no_provider_secrets(self):
        raw=json.dumps({'title':'fixture','description':'full description','url':'https://media.example.org/video.mp4','protocol':'https'}).encode()
        with patch.dict(os.environ,{'ELEVENLABS_API_KEY':'test-provider-secret'}),patch('vss.network.run',return_value=raw) as command,patch('socket.getaddrinfo',return_value=[(2,1,6,'',('93.184.216.34',443))]):
            social_metadata('https://www.youtube.com/watch?v=fixture')
        self.assertNotIn('ELEVENLABS_API_KEY',command.call_args.kwargs['env'])
        self.assertIn('--no-plugin-dirs',command.call_args.args[0])
    def test_supported_hosts_exact(self):
        self.assertTrue(is_social('https://www.youtube.com/watch?v=test'))
        self.assertFalse(is_social('https://youtube.com.evil.example/watch?v=test'))

if __name__=='__main__': unittest.main()
