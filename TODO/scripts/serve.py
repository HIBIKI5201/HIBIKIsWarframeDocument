"""ビルドしてローカルサーバーで配信し、data/ や site/ の変更を検知して自動で再ビルドする。
編集モード用に、項目を data/*.toml へ書き戻す API (POST /api/item) も提供する。

使い方:
    python TODO/scripts/serve.py [--port 8000] [--open]
"""
from __future__ import annotations

import argparse
import functools
import importlib
import json
import threading
import time
import traceback
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import build
import todo_store

WATCH = [build.DATA, build.TEMPLATES, build.STATIC, build.ROOT / "db", Path(__file__).parent]
LOCK = threading.Lock()  # ビルドとデータ書き込みを直列化する
ALLOWED_HOSTS = {"localhost", "127.0.0.1"}


def snapshot() -> dict[Path, float]:
    return {p: p.stat().st_mtime for d in WATCH for p in d.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts}


def rebuild() -> None:
    with LOCK:
        try:
            # scripts/ の変更を取り込む (serve.py 自身の変更は再起動が必要)
            importlib.reload(todo_store)
            importlib.reload(build)
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


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass

    def _json(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/api/ping":
            self._json(200, {"ok": True})
        else:
            super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/item":
            self._json(404, {"error": "not found"})
            return
        # 他サイトからの書き込み (CSRF) を防ぐ: JSON 以外と localhost 以外の Host を拒否
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        if host not in ALLOWED_HOSTS or not (self.headers.get("Content-Type") or "").startswith("application/json"):
            self._json(403, {"error": "forbidden"})
            return
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)))
            with LOCK:
                item = todo_store.update_item(build.DATA, req["category"], req["name"], req["action"],
                                               req.get("index"))
        except (todo_store.StoreError, KeyError, ValueError) as e:
            self._json(400, {"error": str(e)})
            return
        print(f"[{time.strftime('%H:%M:%S')}] {req['action']}: {req['category']}/{req['name']}", flush=True)
        self._json(200, item)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--open", action="store_true", help="起動後にブラウザで開く")
    args = ap.parse_args()

    rebuild()
    threading.Thread(target=watch, daemon=True).start()
    handler = functools.partial(Handler, directory=str(build.SITE))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    url = f"http://localhost:{args.port}/"
    print(f"serving {url}  (Ctrl+C で停止)", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
