"""Reference frontend from the project spec, fetched at a pinned commit.

The frontend hardcodes its API root in js/app.js. Instead of patching the
checkout, `FrontendHandler` rewrites that line on the fly when serving.

Run manually: python e2e/frontend.py --port 8080 --api-url http://localhost:8000
"""

import argparse
import functools
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FRONTEND_REPO = "https://github.com/zhukovsd/currency-exchange-frontend"
FRONTEND_COMMIT = "24a10a4e9085ddc32a3558cf7f22347f9bbc3e42"
FRONTEND_DIR = Path(__file__).parent / "frontend"
FRONTEND_API_HOST = "http://localhost:8080/currency_exchange_war_exploded"


def fetch_frontend(target: Path = FRONTEND_DIR) -> Path:
    if not (target / "index.html").exists():
        subprocess.run(["git", "clone", "-q", FRONTEND_REPO, str(target)], check=True)
    subprocess.run(
        ["git", "-C", str(target), "checkout", "-q", FRONTEND_COMMIT], check=True
    )
    return target


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, api_url: str, **kwargs) -> None:
        self.api_url = api_url
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path.split("?")[0] != "/js/app.js":
            return super().do_GET()

        source = (FRONTEND_DIR / "js" / "app.js").read_text(encoding="utf-8")
        body = source.replace(FRONTEND_API_HOST, self.api_url).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/javascript; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        pass


def make_server(port: int, api_url: str) -> ThreadingHTTPServer:
    handler = functools.partial(FrontendHandler, api_url=api_url.rstrip("/"))
    return ThreadingHTTPServer(("127.0.0.1", port), handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--api-url", default="http://localhost:8000")
    args = parser.parse_args()

    fetch_frontend()
    server = make_server(args.port, args.api_url)
    print(f"Frontend: http://localhost:{args.port} -> API {args.api_url}")
    server.serve_forever()
