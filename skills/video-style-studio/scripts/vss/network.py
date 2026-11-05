"""Bounded direct HTTP downloads. yt-dlp metadata has separate documented limits."""
import http.client
import ipaddress
import json
import os
import socket
import ssl
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urljoin, urlencode
from .core import StudioError, guard_secret, run
import sys

SOCIAL = ('youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com', 'vimeo.com')

def public_url(url, resolve=True):
    try:
        p = urlsplit(url)
        port = p.port
    except ValueError as exc:
        raise StudioError('URL no válida.') from exc
    if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password or port not in (None, 80, 443):
        raise StudioError('Usa un enlace público HTTP(S), sin credenciales ni puertos especiales.')
    host = p.hostname.rstrip('.').lower()
    if host == 'localhost' or host.endswith(('.local', '.localhost', '.internal')):
        raise StudioError('No se aceptan destinos de red local.')
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal and not literal.is_global:
        raise StudioError('No se aceptan direcciones privadas o reservadas.')
    addresses = []
    if resolve:
        try:
            addresses = list({r[4][0] for r in socket.getaddrinfo(host, port or (443 if p.scheme == 'https' else 80), type=socket.SOCK_STREAM)})
        except OSError as exc:
            raise StudioError('No se pudo resolver el enlace. Revisa que abra o importa el archivo con su URL original.') from exc
        if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
            raise StudioError('El enlace resuelve a una dirección privada/reservada.')
    return p, addresses

def redacted_url(url):
    p, _ = public_url(url, resolve=False)
    # Social identifiers in the path survive. Query values may contain credentials.
    return urlunsplit((p.scheme, p.netloc, p.path, '', ''))

def is_social(url):
    host = urlsplit(url).hostname or ''
    return any(host == x or host.endswith('.' + x) for x in SOCIAL)

class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, address, port=443):
        super().__init__(host, port=port, timeout=25, context=ssl.create_default_context())
        self.address = address
    def connect(self):
        sock = socket.create_connection((self.address, self.port), timeout=self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)

class PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, address, port=80):
        super().__init__(host, port=port, timeout=25); self.address = address
    def connect(self):
        self.sock = socket.create_connection((self.address, self.port), timeout=self.timeout)

def fetch(url, destination, max_bytes=300 * 1024 * 1024, method='GET', body=None, headers=None, redirects=4):
    """Resolve once per request and connect to the checked address; recheck redirects."""
    if os.environ.get('VSS_OFFLINE') == '1':
        raise StudioError('Modo sin red: importa el archivo autorizado con su URL original.')
    headers = dict(headers or {})
    deadline = time.monotonic() + 120
    for _ in range(redirects + 1):
        p, ips = public_url(url)
        cls = PinnedHTTPS if p.scheme == 'https' else PinnedHTTP
        conn = cls(p.hostname, ips[0], p.port or (443 if p.scheme == 'https' else 80))
        try:
            conn.request(method, urlunsplit(('', '', p.path or '/', p.query, '')), body=body,
                         headers={'User-Agent': 'VideoStyleStudio/0.1', **headers})
            response = conn.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                if method != 'GET' or headers:
                    raise StudioError('Una API autenticada intentó redirigir la petición. Se detuvo.')
                url = urljoin(url, response.getheader('Location', '')); continue
            if response.status >= 400:
                raise StudioError('El proveedor respondió HTTP ' + str(response.status) + '. No se reintentó ni eludió acceso.')
            length = int(response.getheader('Content-Length', '0'))
            if length > max_bytes:
                raise StudioError('El archivo supera el límite de descarga.')
            count = 0
            with open(destination, 'xb') as out:
                while True:
                    if time.monotonic() > deadline:
                        raise StudioError('La descarga excedió120 segundos.')
                    chunk = response.read(128 * 1024)
                    if not chunk: break
                    count += len(chunk)
                    if count > max_bytes:
                        raise StudioError('La descarga superó el límite permitido.')
                    out.write(chunk)
            return {'bytes': count, 'content_type': response.getheader('Content-Type', ''), 'url': redacted_url(url)}
        except (OSError, http.client.HTTPException, ValueError) as exc:
            raise StudioError('La descarga no pudo completarse. Puedes importar el archivo original.') from exc
        finally:
            conn.close()
    raise StudioError('Demasiadas redirecciones.')

def social_metadata(url, provider='yt-dlp'):
    if os.environ.get('VSS_OFFLINE') == '1':
        raise StudioError('Modo sin red: descarga no realizada.')
    public_url(url)
    if not is_social(url):
        raise StudioError('Plataforma no admitida por este adaptador. Usa un MP4 directo o importa un archivo con su enlace.')
    if provider == 'yt-dlp':
        # No generic extractor, playlists, configuration, plugins, postprocessors or execution hooks.
        child_env = {k:v for k,v in os.environ.items() if k in ('PATH','SystemRoot','WINDIR','TEMP','TMP','LANG','LC_ALL','SSL_CERT_FILE')}
        raw = run([sys.executable, '-m', 'yt_dlp', '--ignore-config', '--no-plugin-dirs',
                   '--no-playlist', '--no-cache-dir', '--socket-timeout', '15', '--retries', '0',
                   '--extractor-retries', '0', '--skip-download', '--dump-single-json',
                   '--format', 'best[ext=mp4][vcodec!=none][acodec!=none]/best[ext=mp4]', '--', url], timeout=75, env=child_env)
        if len(raw) > 12 * 1024 * 1024:
            raise StudioError('Metadatos demasiado grandes.')
        guard_secret(raw.decode('utf-8'))
        d = json.loads(raw)
        if d.get('_type') in ('playlist', 'multi_video') or d.get('is_live') or d.get('live_status') == 'is_live':
            raise StudioError('Se requiere un video individual terminado, no una lista o directo.')
        media = d.get('url')
        if not media or d.get('protocol', '').startswith(('m3u8', 'dash')):
            raise StudioError('No hay MP4 progresivo disponible. Importa una descarga autorizada o usa otro conector.')
        public_url(media)
        return raw, {'title': d.get('title'), 'description': d.get('description') or '',
                     'creator': d.get('uploader'), 'media_url': media, 'subtitles': d.get('subtitles', {}),
                     'automatic_captions': d.get('automatic_captions', {}), 'provider': 'yt-dlp'}
    if provider != 'scrapecreators' or 'instagram.com' not in (urlsplit(url).hostname or ''):
        raise StudioError('Este fallback solo implementa reels individuales de Instagram.')
    key = os.environ.get('SCRAPECREATORS_API_KEY')
    if not key:
        raise StudioError('Configura SCRAPECREATORS_API_KEY en secretos; no la pegues en el chat.')
    with tempfile.TemporaryDirectory() as td:
        dest = Path(td) / 'metadata.json'
        fetch('https://api.scrapecreators.com/v1/instagram/post?' + urlencode({'url': url}), dest,
              12 * 1024 * 1024, headers={'x-api-key': key})
        raw = dest.read_bytes()
    guard_secret(raw.decode('utf-8'))
    d = json.loads(raw)
    item = d.get('data', {}).get('xdt_shortcode_media')
    if not isinstance(item, dict) or not item.get('video_url') or item.get('edge_sidecar_to_children'):
        raise StudioError('El proveedor no devolvió un reel individual utilizable; no se reintentó.')
    edges = item.get('edge_media_to_caption', {}).get('edges', [])
    return raw, {'title': None, 'description': '\n'.join(e.get('node', {}).get('text', '') for e in edges),
                 'creator': item.get('owner', {}).get('username'), 'media_url': item['video_url'],
                 'provider': 'scrapecreators'}
