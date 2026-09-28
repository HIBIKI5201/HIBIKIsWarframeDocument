"""TODO とストーリー資料の HTML を 1 つのサイトにまとめ、ヘッダーから切り替えられるようにする。

claude.ai のアーティファクト（スマホから見る用）に載せるためのもの。
それぞれのビルドスクリプトを実行してから、出力を build/artifact/ に並べる。

    build/artifact/
      index.html        TODO ダッシュボード（アーティファクトの入口。<html> などの外枠なし）
      todo/index.html   TODO 一覧
      static/           TODO の CSS / JS
      story/            ストーリー資料一式

使い方:
    python scripts/build_artifact.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "artifact"
TODO_SITE = ROOT / "TODO" / "build" / "site"
STORY_SITE = ROOT / "StoryAnalysis" / "build" / "site"

SWITCH_STYLE = """<style>
.app-switch { display: inline-flex; padding: 2px; border: 1px solid var(--line); border-radius: 99px; background: var(--surface); }
.app-switch a { padding: .15rem .8rem; border-radius: 99px; font-size: .85rem; color: var(--muted); }
.app-switch a:hover { text-decoration: none; color: var(--text); }
.app-switch a[aria-current] { background: var(--accent-soft); color: var(--text); font-weight: 600; }
</style>"""


def switcher(root: str, app: str) -> str:
    def item(label: str, href: str, key: str) -> str:
        current = ' aria-current="page"' if key == app else ""
        return f'<a href="{root}{href}"{current}>{label}</a>'
    return (f'<nav class="app-switch" aria-label="表示の切り替え">'
            f'{item("TODO", "index.html", "todo")}{item("ストーリー", "story/index.html", "story")}</nav>')


def build_sites() -> None:
    for script in ("TODO/scripts/build.py", "StoryAnalysis/scripts/build_site.py"):
        subprocess.run([sys.executable, str(ROOT / script)], check=True)


def patch(path: Path, root: str, app: str) -> None:
    text = path.read_text(encoding="utf-8")
    # ブランドの直後に切り替えボタンを置く
    text = re.sub(r'(<a class="brand"[^>]*>.*?</a>)', lambda m: m.group(1) + switcher(root, app), text, count=1)
    text = text.replace("</head>", SWITCH_STYLE + "\n</head>", 1)
    if app == "todo":
        # アーティファクトはディレクトリの index.html 補完やクエリ文字列を当てにできないので書き換える
        text = re.sub(r'href="([^"]*?)todo/\?cat=([^"]+)"', r'href="\1todo/index.html#\2"', text)
        text = re.sub(r'href="([^"]*?)todo/"', r'href="\1todo/index.html"', text)
    path.write_text(text, encoding="utf-8")


def strip_document(path: Path, title: str) -> None:
    """入口ページは公開時に外枠が付くので、<head> の中身と <body> の中身だけにする。"""
    text = path.read_text(encoding="utf-8")
    head = text[text.index("<head>") + 6:text.index("</head>")]
    head = re.sub(r"<meta[^>]*>\n?", "", head)
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head)
    body = text[text.index("<body>") + 6:text.index("</body>")]
    path.write_text(head.strip() + "\n" + body.strip() + "\n", encoding="utf-8")


def main() -> None:
    build_sites()
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(TODO_SITE, OUT)
    shutil.copytree(STORY_SITE, OUT / "story")
    for page in OUT.rglob("*.html"):
        rel = page.relative_to(OUT)
        root = "../" * (len(rel.parts) - 1)
        patch(page, root, "story" if rel.parts[0] == "story" else "todo")
    strip_document(OUT / "index.html", "Warframe Document")
    print(f"built {OUT.relative_to(ROOT)}")
    for f in sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()):
        print(" ", f)


if __name__ == "__main__":
    main()
