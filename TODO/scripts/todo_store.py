"""data/*.toml の 1 項目を書き換える。

TOML ライブラリで書き出すとコメントや並びが崩れるため、該当する [[items]] ブロックの
行だけをテキストとして差し替え、書き込み前に tomllib でパースできることを確かめる。
"""
from __future__ import annotations

import os
import re
import tomllib
from datetime import datetime
from pathlib import Path

ITEM_HEADER = "[[items]]"


class StoreError(Exception):
    pass


def category_file(data_dir: Path, category: str) -> Path:
    if not re.fullmatch(r"[a-z0-9_-]+", category):
        raise StoreError(f"invalid category: {category}")
    matches = list(data_dir.glob(f"*-{category}.toml")) + list(data_dir.glob(f"{category}.toml"))
    if len(matches) != 1:
        raise StoreError(f"category not found: {category}")
    return matches[0]


def _split_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """[[items]] ブロックの (開始行, 終了行) の一覧。終了行は次ブロックの直前。"""
    starts = [i for i, line in enumerate(lines) if line.strip() == ITEM_HEADER]
    return [(s, starts[n + 1] if n + 1 < len(starts) else len(lines)) for n, s in enumerate(starts)]


def _format(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    raise TypeError(value)


def _set_key(block: list[str], key: str, value) -> None:
    line = f"{key} = {_format(value)}\n"
    pattern = re.compile(rf"^{re.escape(key)}\s*=")
    for i, existing in enumerate(block):
        if pattern.match(existing):
            block[i] = line
            return
    # 新しいキーは done の前 (なければブロック末尾の空行の前) に入れる
    at = next((i for i, l in enumerate(block) if re.match(r"^done\s*=", l)), None)
    if at is None:
        at = len(block)
        while at > 1 and not block[at - 1].strip():
            at -= 1
    block.insert(at, line)


def update_item(data_dir: Path, category: str, name: str, action: str) -> dict:
    """action: toggle (完了切替) / inc / dec (必要数の増減)。更新後の項目を返す。"""
    path = category_file(data_dir, category)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    for start, end in _split_blocks(lines):
        block = lines[start:end]
        item = tomllib.loads("".join(block[1:]))
        if item.get("name") == name:
            break
    else:
        raise StoreError(f"item not found: {category}/{name}")

    done = bool(item.get("done", False))
    required = item.get("required")
    if action == "toggle":
        done = not done
        _set_key(block, "done", done)
    elif action in ("inc", "dec"):
        if required is None:
            raise StoreError(f"item has no required count: {name}")
        required = required + 1 if action == "inc" else max(required - 1, 0)
        done = required == 0  # 残り 0 個で完了扱い
        _set_key(block, "required", required)
        _set_key(block, "done", done)
    else:
        raise StoreError(f"invalid action: {action}")

    updated = item.get("updated")
    if updated is not None:  # 更新日時を記録しているカテゴリだけ更新する
        updated = datetime.now().replace(microsecond=0)
        _set_key(block, "updated", updated)

    new_text = "".join(lines[:start] + block + lines[end:])
    tomllib.loads(new_text)  # 壊れた TOML は書き込まない
    tmp = path.with_suffix(".toml.tmp")
    tmp.write_text(new_text, encoding="utf-8")
    os.replace(tmp, path)

    return {
        "done": done,
        "required": required,
        "updated": updated.isoformat(sep=" ", timespec="minutes") if updated else None,
    }
