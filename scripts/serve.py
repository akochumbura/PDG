"""Preview the site locally the way Cloudflare Pages serves it (clean URLs, 404 page).
Usage: python scripts/serve.py [port]   then open http://localhost:8000"""
import functools, http.server, sys
from pathlib import Path

DIST = Path(__file__).resolve().parents[1] / 'dist'

class Handler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.path.split('?', 1)[0].split('#', 1)[0]
        local = DIST / path.lstrip('/')
        if path.endswith('.html') and not path.endswith('/404.html'):
            clean = path[:-len('index.html')] if path.endswith('/index.html') else path[:-len('.html')]
            self.send_response(308); self.send_header('Location', clean); self.end_headers(); return None
        if not local.exists() and local.with_name(local.name + '.html').is_file():
            self.path = path + '.html'
        elif not local.exists():
            lang = path.strip('/').split('/')[0]
            page = DIST / lang / '404.html' if lang in ('en', 'ru') else DIST / '404.html'
            body = page.read_bytes()
            self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body))); self.end_headers()
            self.wfile.write(body); return None
        return super().send_head()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
http.server.ThreadingHTTPServer(('', port), functools.partial(Handler, directory=str(DIST))).serve_forever()
