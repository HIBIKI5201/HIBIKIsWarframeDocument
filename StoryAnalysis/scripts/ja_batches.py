"""キャラクター・クエストの日本語訳を作る作業用の補助。

    python StoryAnalysis/scripts/ja_batches.py make [--size 40000]
        まだ日本語訳（data/ja/<kind>/<key>.md）がない項目の英語本文（.cache/wiki_src/）を、
        約 size 文字ずつ .cache/ja_batches/NNN.md にまとめる。項目の区切りは「=== <kind>/<key> ===」。
    python StoryAnalysis/scripts/ja_batches.py apply <日本語の束ファイル>
        同じ区切りで書いた日本語の束を data/ja/<kind>/<key>.md に振り分ける。

日本語訳の書式（build_wiki.py が読む）:
    ## 要約        ← 概要の下に出る 2〜3 文
    ## <章の見出し>  ← 詳細の章（経歴・トリビアなど）。### 以下も使える
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / ".cache" / "wiki_src"
JA = ROOT / "data" / "ja"
BATCH = ROOT / ".cache" / "ja_batches"
SEP = re.compile(r"^=== (characters|quests)/([a-z0-9-]+) ===$", re.M)


def make(size: int) -> None:
    BATCH.mkdir(parents=True, exist_ok=True)
    for f in BATCH.glob("*.md"):
        f.unlink()
    pending = [f for kind in ("quests", "characters") for f in sorted((SRC / kind).glob("*.md"))
               if not (JA / kind / f.name).exists()]
    batches, cur, n = [], [], 0
    for f in pending:
        text = f.read_text(encoding="utf-8").strip()
        if len(text) < 40:
            continue
        if cur and n + len(text) > size:
            batches.append(cur)
            cur, n = [], 0
        cur.append(f"=== {f.parent.name}/{f.stem} ===\n{text}\n")
        n += len(text)
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches, 1):
        (BATCH / f"{i:03}.md").write_text("\n".join(b), encoding="utf-8")
    print(f"未翻訳 {sum(len(b) for b in batches)} 件 → {len(batches)} 束（{BATCH.relative_to(ROOT.parent)}）")


def apply(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    parts = SEP.split(text)
    count = 0
    for kind, key, body in zip(parts[1::3], parts[2::3], parts[3::3]):
        out = JA / kind / f"{key}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body.strip() + "\n", encoding="utf-8", newline="\n")
        count += 1
    print(f"{count} 件を書き出しました")


if __name__ == "__main__":
    if sys.argv[1:2] == ["make"]:
        size = int(sys.argv[3]) if sys.argv[2:3] == ["--size"] else 40000
        make(size)
    elif sys.argv[1:2] == ["apply"] and len(sys.argv) == 3:
        apply(Path(sys.argv[2]))
    else:
        sys.exit(__doc__)
