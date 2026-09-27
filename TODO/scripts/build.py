"""data/*.toml → SQLite (build/todo.db) → 静的 HTML (build/site/) を生成する。

使い方:
    python TODO/scripts/build.py
"""
from __future__ import annotations

import html
import re
import shutil
import sqlite3
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BUILD = ROOT / "build"
DB_PATH = BUILD / "todo.db"
SITE = BUILD / "site"
TEMPLATES = ROOT / "site" / "templates"
STATIC = ROOT / "site" / "static"

# TODO テーブルの任意列 (DB 列名, 見出し)
OPTIONAL_COLUMNS = [
    ("source", "入手場所"),
    ("condition", "条件"),
    ("required", "必要数"),
    ("updated_at", "更新"),
    ("url", "リンク"),
]

esc = html.escape


# ---------------------------------------------------------------- load

def load_todo(con: sqlite3.Connection) -> None:
    for path in sorted(DATA.glob("*.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        cat_id = re.sub(r"^\d+-", "", path.stem)
        meta = data.get("category", {})
        con.execute(
            "INSERT INTO categories (id, title, sort_order) VALUES (?, ?, ?)",
            (cat_id, meta.get("title", cat_id), meta.get("order", 999)),
        )
        for n, item in enumerate(data.get("items", [])):
            updated = item.get("updated")
            con.execute(
                """INSERT INTO items (category_id, name, source, condition, required,
                                      url, note, done, updated_at, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    cat_id, item["name"], item.get("source"), item.get("condition"),
                    item.get("required"), item.get("url"), item.get("note"),
                    int(bool(item.get("done", False))),
                    updated.isoformat(timespec="minutes") if updated else None, n,
                ),
            )



def build_db() -> sqlite3.Connection:
    BUILD.mkdir(exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript((ROOT / "db" / "schema.sql").read_text(encoding="utf-8"))
    load_todo(con)
    con.commit()
    return con


# ---------------------------------------------------------------- render

def template(name: str) -> Template:
    return Template((TEMPLATES / name).read_text(encoding="utf-8"))


def write_page(rel: str, title: str, body: str, nav: str) -> None:
    depth = rel.count("/")
    root = "../" * depth
    page = template("base.html").substitute(
        title=esc(title), content=body, root=root,
        nav_home="current" if nav == "home" else "",
        nav_todo="current" if nav == "todo" else "",
        built=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    out = SITE / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def progress_bar(done: int, total: int) -> str:
    pct = round(done * 100 / total) if total else 0
    return (f'<div class="bar" role="progressbar" aria-valuenow="{pct}" aria-valuemin="0" '
            f'aria-valuemax="100"><span style="width:{pct}%"></span></div>')


def render_home(con: sqlite3.Connection) -> None:
    cats = con.execute("SELECT * FROM category_progress").fetchall()
    total = sum(c["total"] for c in cats)
    done = sum(c["done"] for c in cats)
    cards = "\n".join(
        f'<a class="card" href="todo/?cat={c["id"]}"><h3>{esc(c["title"])}</h3>'
        f'<p class="count"><b>{c["done"]}</b> / {c["total"]}</p>'
        f'{progress_bar(c["done"], c["total"])}</a>'
        for c in cats
    )
    body = template("home.html").substitute(
        done=done, total=total, remaining=total - done,
        bar=progress_bar(done, total), cards=cards,
    )
    write_page("index.html", "ダッシュボード", body, "home")


def cell(col: str, value) -> str:
    if value is None:
        return "<td></td>"
    if col == "url":
        return f'<td><a href="{esc(value)}" target="_blank" rel="noopener">Wiki ↗</a></td>'
    if col == "updated_at":
        return f'<td><time class="updated">{esc(value.replace("T", " "))}</time></td>'
    if col == "required":
        return (f'<td class="num"><button type="button" class="step" data-action="dec" aria-label="1 減らす">−</button>'
                f'<span class="qty">×{value}</span>'
                f'<button type="button" class="step" data-action="inc" aria-label="1 増やす">+</button></td>')
    return f"<td>{esc(str(value))}</td>"


def render_todo(con: sqlite3.Connection) -> None:
    cats = con.execute("SELECT * FROM category_progress").fetchall()
    chips = "\n".join(
        f'<button type="button" class="chip" data-cat="{c["id"]}">{esc(c["title"])}'
        f' <small>{c["total"] - c["done"]}</small></button>'
        for c in cats
    )
    sections = []
    for c in cats:
        items = con.execute(
            "SELECT * FROM items WHERE category_id = ? ORDER BY done, sort_order", (c["id"],)
        ).fetchall()
        cols = [(k, label) for k, label in OPTIONAL_COLUMNS if any(i[k] is not None for i in items)]
        head = "<th>名前</th>" + "".join(f"<th>{label}</th>" for _, label in cols)
        rows = []
        for i in items:
            search = " ".join(str(i[k]) for k in ("name", "source", "condition", "note") if i[k])
            note = f'<div class="note">{esc(i["note"])}</div>' if i["note"] else ""
            # 必要数がある項目 (アルケインなど) は +/- で、それ以外はチェックで完了を切り替える
            counted = i["required"] is not None
            rows.append(
                f'<tr class="{"done" if i["done"] else ""}" data-search="{esc(search.lower())}"'
                f' data-name="{esc(i["name"])}" data-kind="{"count" if counted else "check"}">'
                f'<td class="name"><button type="button" class="check" aria-pressed="{str(bool(i["done"])).lower()}"'
                f' aria-label="完了"{" disabled" if counted else ""}></button>{esc(i["name"])}{note}</td>'
                + "".join(cell(k, i[k]) for k, _ in cols) + "</tr>"
            )
        sections.append(
            f'<section class="category" id="{c["id"]}" data-cat="{c["id"]}">'
            f'<header><h2>{esc(c["title"])}</h2><span class="count"><span class="done-n">{c["done"]}</span> / {c["total"]}</span>'
            f'{progress_bar(c["done"], c["total"])}</header>'
            f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></section>'
        )
    body = template("todo.html").substitute(chips=chips, sections="\n".join(sections))
    write_page("todo/index.html", "TODO", body, "todo")



def build() -> None:
    con = build_db()
    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(STATIC, SITE / "static")
    render_home(con)
    render_todo(con)
    con.close()


if __name__ == "__main__":
    try:
        build()
    except (tomllib.TOMLDecodeError, sqlite3.IntegrityError, KeyError) as e:
        print(f"build failed: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"built {SITE.relative_to(ROOT)}")
