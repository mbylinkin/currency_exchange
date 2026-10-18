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
from typing import Any

FRONTEND_REPO = "https://github.com/zhukovsd/currency-exchange-frontend"
FRONTEND_COMMIT = "24a10a4e9085ddc32a3558cf7f22347f9bbc3e42"
FRONTEND_DIR = Path(__file__).parent / "frontend"
FRONTEND_API_HOST = "http://localhost:8080/currency_exchange_war_exploded"


def fetch_frontend(target: Path = FRONTEND_DIR, commit: str = FRONTEND_COMMIT) -> Path:
    """Check out `commit` into `target`, downloading it only if it's missing.

    `target` is a managed checkout: local edits there are discarded.
    """
    git = ["git", "-C", str(target)]
    if not (target / ".git").exists():
        target.mkdir(parents=True, exist_ok=True)
        subprocess.run([*git, "init", "-q"], check=True)
        subprocess.run([*git, "remote", "add", "origin", FRONTEND_REPO], check=True)

    has_commit = subprocess.run(
        [*git, "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    if has_commit.returncode != 0:
        subprocess.run(
            [*git, "fetch", "-q", "--depth", "1", "origin", commit], check=True
        )
    subprocess.run([*git, "checkout", "-q", "--force", commit], check=True)
    return target


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, api_url: str, **kwargs: Any) -> None:
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

    def log_message(self, format: str, *args: Any) -> None:
        pass


def make_server(
    port: int, api_url: str, host: str = "127.0.0.1"
) -> ThreadingHTTPServer:
    handler = functools.partial(FrontendHandler, api_url=api_url.rstrip("/"))
    return ThreadingHTTPServer((host, port), handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--api-url", default="http://localhost:8000")
    fetch = parser.add_mutually_exclusive_group()
    fetch.add_argument(
        "--fetch-only", action="store_true", help="download the frontend and exit"
    )
    fetch.add_argument(
        "--no-fetch", action="store_true", help="serve the existing download as is"
    )
    args = parser.parse_args()

    if not args.no_fetch:
        fetch_frontend()
    if args.fetch_only:
        raise SystemExit
    server = make_server(args.port, args.api_url, args.host)
    print(f"Frontend: http://localhost:{args.port} -> API {args.api_url}")
    server.serve_forever()
