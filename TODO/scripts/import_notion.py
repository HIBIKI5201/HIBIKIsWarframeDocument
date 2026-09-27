"""Notion エクスポート (zip) を TODO/data/*.toml に変換するワンショット移行スクリプト。

使い方:
    python TODO/scripts/import_notion.py TODO/archive/notion/notion-export-2026-09-27.zip [--force]

既存の TOML は --force を付けない限り上書きしない（手で編集した内容を守るため）。
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODO_DIR = ROOT / "data"

# Notion のデータベース名 → (ファイル名, カテゴリID, 表示順, 列マッピング)
# 列マッピングは Notion の列名 → TOML のキー
DATABASES = {
    "装備": ("equipment", 1, {}),
    "MOD": ("mods", 2, {"入手場所": "source"}),
    "アルケイン": ("arcanes", 3, {"取得場所": "source", "必要数": "required", "最終更新日時": "updated"}),
    "ホノリア": ("honoria", 4, {"条件": "condition"}),
    "シーン アリーナ": ("scenes", 5, {"テキスト": "source"}),
    "スキャン": ("scans", 6, {}),
    "その他": ("misc", 7, {}),
}
TITLES = {"シーン アリーナ": "シーン/アリーナ"}

NOTION_ID = re.compile(r" [0-9a-f]{32}(?=(_all)?\.(csv|md)$)")
URL = re.compile(r"^https?://\S+$", re.M)


def read_zip(path: Path) -> dict[str, bytes]:
    """zip (ネストした zip も含む) を展開し {正規化パス: 中身} を返す。"""
    files: dict[str, bytes] = {}

    def walk(zf: zipfile.ZipFile) -> None:
        for info in zf.infolist():
            name = info.filename
            if not info.flag_bits & 0x800:  # UTF-8 フラグなし → cp437 として誤デコードされている
                try:
                    name = name.encode("cp437").decode("utf-8")
                except UnicodeError:
                    pass
            data = zf.read(info)
            if name.endswith(".zip"):
                walk(zipfile.ZipFile(io.BytesIO(data)))
            elif not name.endswith("/"):
                files[NOTION_ID.sub("", name)] = data

    walk(zipfile.ZipFile(path))
    return files


def parse_notion_datetime(s: str) -> datetime:
    return datetime.strptime(s, "%Y年%m月%d日 %H:%M")


def toml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%dT%H:%M:%S")
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def to_toml(title: str, order: int, items: list[dict]) -> str:
    out = [
        "# Notion「欲しいものデータベース」から移行",
        "[category]",
        f"title = {toml_value(title)}",
        f"order = {order}",
        "",
    ]
    for item in items:
        out.append("[[items]]")
        out += [f"{k} = {toml_value(v)}" for k, v in item.items()]
        out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("zip", type=Path)
    ap.add_argument("--force", action="store_true", help="既存の TOML を上書きする")
    args = ap.parse_args()

    files = read_zip(args.zip)
    TODO_DIR.mkdir(parents=True, exist_ok=True)

    for db_name, (slug, order, mapping) in DATABASES.items():
        csv_key = next(k for k in files if k.endswith(f"/{db_name}_all.csv"))
        page_dir = csv_key.removesuffix("_all.csv")
        rows = csv.DictReader(io.StringIO(files[csv_key].decode("utf-8-sig")))

        items = []
        for row in rows:
            item: dict = {"name": row["名前"]}
            for col, key in mapping.items():
                val = row.get(col, "").strip()
                if not val:
                    continue
                if key == "required":
                    val = int(val)
                elif key == "updated":
                    val = parse_notion_datetime(val)
                item[key] = val
            # ページ本文にある URL (スキャン対象の wiki リンクなど)
            body = files.get(f"{page_dir}/{row['名前']}.md", b"").decode("utf-8")
            if m := URL.search(body):
                item["url"] = m.group(0)
            item["done"] = False
            items.append(item)

        dest = TODO_DIR / f"{order:02d}-{slug}.toml"
        if dest.exists() and not args.force:
            print(f"skip (exists): {dest.relative_to(ROOT)}")
            continue
        dest.write_text(to_toml(TITLES.get(db_name, db_name), order, items), encoding="utf-8")
        print(f"wrote {dest.relative_to(ROOT)} ({len(items)} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
