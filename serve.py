#!/usr/bin/env python3
"""Serve the research radar and relay its arXiv calls.

The arXiv API sends no Access-Control-Allow-Origin header, so a browser
refuses the direct call and the page has to fall back to public proxies
that are rate-limited and frequently down. Running this script gives the
page a route it owns:

    python3 serve.py            # then open http://localhost:8787/

GET /arxiv?url=<encoded arXiv API url> fetches that URL server-side and
returns it with CORS enabled. Only export.arxiv.org is allowed through,
so this stays a single-purpose relay rather than an open proxy.
"""
import http.server, socketserver, urllib.parse, urllib.request, urllib.error, os, sys

PORT = int(os.environ.get("PORT", "8787"))
ALLOWED_HOST = "export.arxiv.org"
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        parts = urllib.parse.urlsplit(self.path)
        if parts.path == "/arxiv":
            return self.relay(urllib.parse.parse_qs(parts.query).get("url", [""])[0])
        return super().do_GET()

    def relay(self, target):
        parsed = urllib.parse.urlsplit(target)
        if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
            return self.fail(403, "only https://%s is relayed" % ALLOWED_HOST)
        req = urllib.request.Request(target, headers={
            "User-Agent": "arxiv-research-radar/1.0 (local relay)",
            "Accept": "application/atom+xml",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                body = res.read()
        except urllib.error.HTTPError as e:
            return self.fail(e.code, "arXiv returned HTTP %s" % e.code)
        except Exception as e:
            return self.fail(502, "relay failed: %s" % e)
        self.send_response(200)
        self.send_header("Content-Type", "application/atom+xml; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def fail(self, code, msg):
        body = msg.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        if self.path.endswith(".html") or self.path in ("/", ""):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Server(("127.0.0.1", PORT), Handler) as httpd:
        print("Research radar  ->  http://localhost:%d/arxiv_semantic_research_radar.html" % PORT)
        print("arXiv relay     ->  http://localhost:%d/arxiv?url=..." % PORT)
        print("Ctrl-C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
