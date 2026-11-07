import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/video-style-studio/scripts'))
from vss.core import StudioError
from vss.recording import validate_plan

class RecordingTests(unittest.TestCase):
    def test_invalid_cuts_rejected(self):
        for segments in ([{'start':3,'end':22}], [{'start':0,'end':16},{'start':15,'end':19}], [{'start':0,'end':15.01}], [{'start':float('nan'),'end':18}]):
            with self.subTest(segments=segments),self.assertRaises(StudioError):
                validate_plan({'segments':segments,'reason':'fixture'},20)
    def test_captions_use_output_clock(self):
        plan={'segments':[{'start':0,'end':8},{'start':10,'end':20}],'reason':'Remove two seconds reviewed in the fixture','captions':[{'start':16,'end':19,'text':'Fuera del montaje'}]}
        with self.assertRaises(StudioError):validate_plan(plan,20)
        plan['captions'][0]['end']=18
        self.assertEqual(validate_plan(plan,20),18)

    @unittest.skipUnless(shutil.which('ffmpeg'),'requires ffmpeg')
    def test_isolated_recording_cli_and_approval(self):
        with tempfile.TemporaryDirectory(prefix='vss-edit-') as td:
            tmp=Path(td);cli=ROOT/'skills/video-style-studio/scripts/studio.py'
            def run(*args,fail=False):
                p=subprocess.run([sys.executable,str(cli),*map(str,args)],capture_output=True,timeout=120)
                if fail:self.assertNotEqual(p.returncode,0);return
                self.assertEqual(p.returncode,0,p.stderr.decode(errors='replace'));return json.loads(p.stdout)
            run('install','--destination',tmp/'installed');cli=tmp/'installed/video-style-studio/scripts/studio.py'
            source=tmp/'source.mp4'
            # Second 8–10 is silent; tones are transport fixtures, not natural speech.
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=size=180x320:rate=30:duration=20','-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=20','-af',"volume=enable='between(t,8,10)':volume=0",'-c:v','libx264','-preset','ultrafast','-c:a','aac',str(source)],check=True)
            project=tmp/'project';run('init','--workspace',project,'--reference-url','https://example.org/fixture.mp4')
            def call(*args,**kw):return run(*args,'--workspace',project,**kw)
            call('recording-import','--file',source,fail=True)
            evidence=tmp/'environment.json';evidence.write_text(json.dumps({'execution_location':'user-desktop','source':'runtime-attestation','evidence':'TEST ONLY: CI supplied environment, not app detection.'}))
            call('confirm-environment','--evidence',evidence);call('recording-import','--file',source)
            report=call('recording-silences');self.assertTrue(any(e['kind']=='start' and 7.9<e['seconds']<8.1 for e in report['events']))
            plan=tmp/'plan.json';value={'segments':[{'start':0,'end':8},{'start':10,'end':20}],'captions':[{'start':1,'end':3,'text':'Prueba: ñ, acción.'},{'start':8,'end':10,'text':'Después del corte.'}],'reason':'TEST ONLY: trim synthetic silent fixture.'};plan.write_text(json.dumps(value))
            call('recording-prepare','--plan',plan);call('recording-full',fail=True)
            demo=call('recording-demo');self.assertEqual(demo['frames'],450)
            answer=tmp/'answer.txt';answer.write_text('TEST ONLY: simulated approval for technical fixture.',encoding='utf-8')
            call('recording-approve','--decision','reject','--response-file',answer);call('recording-full',fail=True)
            call('recording-approve','--decision','approve','--response-file',answer)
            full=call('recording-full');self.assertEqual(full['frames'],540);self.assertEqual(full['duration'],18)
            value['captions'][0]['text']='Cambio';plan.write_text(json.dumps(value));call('recording-prepare','--plan',plan);call('recording-full',fail=True)
            # Original remains readable with the same full duration.
            info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(source)]));self.assertAlmostEqual(float(info['format']['duration']),20,places=1)

if __name__=='__main__':unittest.main()
