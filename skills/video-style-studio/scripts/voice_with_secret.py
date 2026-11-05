"""Run only in a visible, private local terminal. Never asks for secrets in chat."""
import getpass
import os
import sys
from studio import main
from vss.core import StudioError, configure_utf8_output
import json

def interactive_stdin():
    if not sys.stdin.isatty():
        return False
    if os.name == 'nt':
        # Windows NUL can satisfy isatty(); getpass needs an actual console.
        import ctypes
        import msvcrt
        from ctypes import wintypes
        try:
            mode = wintypes.DWORD()
            get_mode = ctypes.WinDLL('kernel32', use_last_error=True).GetConsoleMode
            get_mode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            get_mode.restype = wintypes.BOOL
            return bool(get_mode(msvcrt.get_osfhandle(sys.stdin.fileno()), ctypes.byref(mode)))
        except (OSError, ValueError):
            return False
    return True

if __name__ == '__main__':
    configure_utf8_output()
    try:
        if not interactive_stdin():
            raise StudioError('Usa un gestor de secretos o una terminal local interactiva; no envíes la llave por chat.')
        os.environ['ELEVENLABS_API_KEY'] = getpass.getpass('Llave de ElevenLabs (oculta, solo este proceso): ')
        os.environ['ELEVENLABS_VOICE_ID'] = input('Voice ID autorizado: ').strip()
        result = main(['voice-eleven', *sys.argv[1:]])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except StudioError as exc:
        print(str(exc), file=sys.stderr); sys.exit(2)
    finally:
        os.environ.pop('ELEVENLABS_API_KEY', None)
        os.environ.pop('ELEVENLABS_VOICE_ID', None)
