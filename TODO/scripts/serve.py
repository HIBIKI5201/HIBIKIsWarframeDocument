"""ビルドしてローカルサーバーで配信し、data/ や site/ の変更を検知して自動で再ビルドする。

使い方:
    python TODO/scripts/serve.py [--port 8000]
"""
from __future__ import annotations

import argparse
import functools
import threading
import time
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import build

WATCH = [build.DATA, build.TEMPLATES, build.STATIC, build.ROOT / "db"]


def snapshot() -> dict[Path, float]:
    return {p: p.stat().st_mtime for d in WATCH for p in d.rglob("*") if p.is_file()}


def rebuild() -> None:
    try:
        build.build()
        print(f"[{time.strftime('%H:%M:%S')}] rebuilt", flush=True)
    except Exception:
        traceback.print_exc()


def watch(interval: float = 1.0) -> None:
    last = snapshot()
    while True:
        time.sleep(interval)
        now = snapshot()
        if now != last:
            last = now
            rebuild()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    rebuild()
    threading.Thread(target=watch, daemon=True).start()
    handler = functools.partial(QuietHandler, directory=str(build.SITE))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"serving http://localhost:{args.port}/  (Ctrl+C で停止)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
