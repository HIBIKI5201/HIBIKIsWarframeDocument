"""サイトをビルドしてローカルサーバーで配信し、Markdown やテンプレートの変更を検知して自動で再ビルドする。

使い方:
    python StoryAnalysis/scripts/serve.py [--port 8001] [--open] [--lan]

--lan を付けると同じ Wi-Fi のスマホなどからも見られる（PC の IP アドレスでアクセス）。
"""
from __future__ import annotations

import argparse
import functools
import socket
import threading
import time
import traceback
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import build_site


def snapshot() -> dict[Path, float]:
    files = [*build_site.ROOT.glob("*.md"), *(build_site.ROOT / "sources").glob("*.md"),
             *build_site.TEMPLATES.rglob("*"), *build_site.STATIC.rglob("*")]
    return {p: p.stat().st_mtime for p in files if p.is_file()}


def rebuild() -> None:
    try:
        build_site.build()
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


def lan_ip() -> str:
    """外向きの通信に使う IP アドレス（実際には送信しない）。"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("192.0.2.1", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8001)
    ap.add_argument("--open", action="store_true", help="起動後にブラウザで開く")
    ap.add_argument("--lan", action="store_true", help="同じネットワークの他の端末からも見られるようにする")
    args = ap.parse_args()

    rebuild()
    threading.Thread(target=watch, daemon=True).start()
    handler = functools.partial(QuietHandler, directory=str(build_site.SITE))
    server = ThreadingHTTPServer(("0.0.0.0" if args.lan else "127.0.0.1", args.port), handler)
    url = f"http://localhost:{args.port}/"
    print(f"serving {url}  (Ctrl+C で停止)", flush=True)
    if args.lan:
        print(f"スマホからは http://{lan_ip()}:{args.port}/ を開く（同じ Wi-Fi に接続しておく）", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
