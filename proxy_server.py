#!/usr/bin/env python3
"""Static file server with /api proxy to backend."""
import http.server
import urllib.request
import os

PORT = 9876
BACKEND = "http://localhost:9090"
DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vue/dist")

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy("POST")
        else:
            self._passthrough("POST")

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self._proxy("PUT")
        else:
            self._passthrough("PUT")

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self._proxy("DELETE")
        else:
            self._passthrough("DELETE")

    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            self._proxy("OPTIONS")
        else:
            super().do_OPTIONS()

    def _passthrough(self, method):
        """Pass non-GET requests through to SPA."""
        pass

    def _proxy(self, method):
        url = BACKEND + self.path.replace("/api", "", 1)
        body = None
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len > 0:
            body = self.rfile.read(content_len)

        req = urllib.request.Request(url, data=body, method=method)
        for h, v in self.headers.items():
            hl = h.lower()
            if hl not in ('host', 'connection', 'content-length'):
                req.add_header(h, v)
        if body:
            req.add_header('Content-Length', str(len(body)))

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.send_response(resp.status)
                for h, v in resp.getheaders():
                    if h.lower() not in ('transfer-encoding', 'connection'):
                        self.send_header(h, v)
                resp_body = resp.read()
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except Exception as e:
            msg = str(e).encode()
            self.send_response(502)
            self.send_header('Content-Length', str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

httpd = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler)
print(f"Frontend: http://localhost:{PORT}  (proxy /api -> {BACKEND})")
httpd.serve_forever()
