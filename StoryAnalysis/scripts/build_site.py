"""StoryAnalysis の Markdown（考察・用語対応表・sources/）を静的 HTML (build/site/) に変換する。

使い方:
    python StoryAnalysis/scripts/build_site.py
"""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
REPO_URL = "https://github.com/HIBIKI5201/HIBIKIsWarframeDocument/tree/main/"
current_src: Path | None = None  # 変換中の Markdown（相対リンクの解決用）
BUILD = ROOT / "build"
SITE = BUILD / "site"
TEMPLATES = ROOT / "site" / "templates"
STATIC = ROOT / "site" / "static"

esc = html.escape


# ---------------------------------------------------------------- markdown
# このリポジトリの Markdown で使っている範囲だけを扱う最小実装。

LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def inline(text: str) -> str:
    codes: list[str] = []

    def keep_code(m: re.Match) -> str:
        codes.append(f"<code>{esc(m.group(1))}</code>")
        return f"\0{len(codes) - 1}\0"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = esc(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{link(m.group(2))}">{m.group(1)}</a>', text)
    text = re.sub(r"&lt;(https?://[^\s&]+)&gt;", r'<a href="\1">\1</a>', text)
    return re.sub(r"\0(\d+)\0", lambda m: codes[int(m.group(1))], text)


def link(href: str) -> str:
    if re.match(r"^[a-z]+:", href):
        return esc(href) + '" target="_blank" rel="noopener'
    path, _, frag = href.partition("#")
    if path and not path.endswith(".md") and current_src is not None:
        # サイトに含まれないファイル・フォルダ（例: archive/pixiv/）は GitHub 上の場所へリンクする
        target = (current_src.parent / path).resolve()
        if target.exists() and target.is_relative_to(REPO_ROOT):
            return esc(REPO_URL + target.relative_to(REPO_ROOT).as_posix()) + '" target="_blank" rel="noopener'
    if path.endswith("README.md"):
        path = path[: -len("README.md")] + "index.html"
    elif path.endswith(".md"):
        path = path[:-3] + ".html"
    return esc(path + (f"#{frag}" if frag else ""))


class Renderer:
    def __init__(self) -> None:
        self.headings: list[tuple[int, str, str]] = []  # (level, id, text)
        self.used_ids: set[str] = set()

    def heading_id(self, text: str) -> str:
        base = re.sub(r"[^0-9a-z]+", "-", text.lower()).strip("-") or "s"
        hid, n = base, 2
        while hid in self.used_ids:
            hid, n = f"{base}-{n}", n + 1
        self.used_ids.add(hid)
        return hid

    def render(self, text: str) -> str:
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        lines = text.replace("\r\n", "\n").split("\n")
        body = self.blocks(lines, quote=False)
        return self.sectionize(body)

    def blocks(self, lines: list[str], quote: bool) -> list[str]:
        out: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
            elif line.startswith("```"):
                j = i + 1
                while j < len(lines) and not lines[j].startswith("```"):
                    j += 1
                out.append(f"<pre><code>{esc(chr(10).join(lines[i + 1:j]))}</code></pre>")
                i = j + 1
            elif m := HEADING_RE.match(line):
                level, title = len(m.group(1)), m.group(2).strip()
                hid = self.heading_id(title)
                self.headings.append((level, hid, re.sub(r"<[^>]+>", "", inline(title))))
                out.append(("H", level, f'<h{level} id="{hid}">{inline(title)}</h{level}>'))
                i += 1
            elif line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
                j = i + 2
                while j < len(lines) and lines[j].startswith("|"):
                    j += 1
                out.append(self.table(lines[i], lines[i + 2:j]))
                i = j
            elif line.lstrip().startswith(">"):
                j = i
                while j < len(lines) and lines[j].lstrip().startswith(">"):
                    j += 1
                inner = [re.sub(r"^\s*> ?", "", l) for l in lines[i:j]]
                out.append("<blockquote>" + "".join(self.plain(self.blocks(inner, quote=True))) + "</blockquote>")
                i = j
            elif LIST_RE.match(line):
                html_, i = self.list_block(lines, i, quote)
                out.append(html_)
            else:
                j = i + 1  # 表にならない "|" 始まりの行（例: |PLAYER_NAME|）も段落として 1 行は消費する
                while j < len(lines) and lines[j].strip() and not self.starts_block(lines[j]):
                    j += 1
                joiner = "<br>" if quote else "\n"
                out.append("<p>" + joiner.join(inline(l.strip()) for l in lines[i:j]) + "</p>")
                i = j
        return out

    @staticmethod
    def starts_block(line: str) -> bool:
        return bool(HEADING_RE.match(line) or LIST_RE.match(line) or line.startswith(("|", "```"))
                    or line.lstrip().startswith(">"))

    @staticmethod
    def plain(parts: list) -> list[str]:
        return [p[2] if isinstance(p, tuple) else p for p in parts]

    def list_block(self, lines: list[str], i: int, quote: bool) -> tuple[str, int]:
        first = LIST_RE.match(lines[i])
        indent = len(first.group(1))
        tag = "ol" if first.group(2)[0].isdigit() else "ul"
        items: list[list[str]] = []
        while i < len(lines):
            m = LIST_RE.match(lines[i])
            if m and len(m.group(1)) == indent:
                items.append([m.group(3)])
                i += 1
                continue
            line = lines[i]
            if line.strip() and (len(line) - len(line.lstrip())) > indent:
                items[-1].append(line[indent + 2:] if line[: indent + 2].strip() == "" else line.strip())
                i += 1
            elif not line.strip() and i + 1 < len(lines) and lines[i + 1].strip() and \
                    (len(lines[i + 1]) - len(lines[i + 1].lstrip())) > indent:
                items[-1].append("")
                i += 1
            else:
                break
        lis = []
        for item in items:
            if len(item) == 1:
                lis.append(f"<li>{inline(item[0])}</li>")
            else:
                head, rest = item[0], item[1:]
                lis.append(f"<li>{inline(head)}" + "".join(self.plain(self.blocks(rest, quote))) + "</li>")
        return f"<{tag}>{''.join(lis)}</{tag}>", i

    @staticmethod
    def table(head: str, rows: list[str]) -> str:
        def cells(row: str) -> list[str]:
            return [c.strip() for c in row.strip().strip("|").split("|")]
        th = "".join(f"<th>{inline(c)}</th>" for c in cells(head))
        trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(r)) + "</tr>" for r in rows)
        return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

    @staticmethod
    def sectionize(parts: list) -> str:
        """見出しごとに <section> で入れ子にする（ページ内検索で見出し単位に絞り込むため）。"""
        out: list[str] = []
        stack: list[int] = []
        for p in parts:
            if isinstance(p, tuple):
                level = p[1]
                while stack and stack[-1] >= level:
                    out.append("</section>")
                    stack.pop()
                out.append(f'<section class="s{level}">')
                stack.append(level)
                out.append(p[2])
            else:
                out.append(p)
        out.extend("</section>" for _ in stack)
        return "\n".join(out)


# ---------------------------------------------------------------- pages

def pages() -> list[tuple[Path, str]]:
    """(元 Markdown, 出力パス) の一覧。"""
    result = [(ROOT / "README.md", "index.html"), (ROOT / "glossary.md", "glossary.html")]
    for p in sorted(ROOT.glob("*.md")):
        if p.name not in ("README.md", "glossary.md") and not p.name.startswith("_"):
            result.append((p, p.stem + ".html"))
    result.append((ROOT / "sources" / "README.md", "sources/index.html"))
    for p in sorted((ROOT / "sources").glob("*.md")):
        if p.name != "README.md":
            result.append((p, f"sources/{p.stem}.html"))
    for p in sorted((ROOT / "wiki").rglob("*.md")):
        rel = p.relative_to(ROOT).with_suffix(".html").as_posix()
        result.append((p, rel))
    return result


def title_of(md: str, fallback: str) -> str:
    m = re.search(r"^# (.+)$", md, re.M)
    return m.group(1).strip() if m else fallback


def toc_html(headings: list[tuple[int, str, str]]) -> str:
    items = [(l, i, t) for l, i, t in headings if l in (2, 3)]
    if len(items) < 3:
        return ""
    if sum(1 for l, _, _ in items if l == 3) > 60:
        items = [h for h in items if h[0] == 2]
    lis = "".join(f'<li class="t{l}"><a href="#{i}">{esc(t, quote=False)}</a></li>' for l, i, t in items)
    return f'<details class="toc"><summary>目次（{len(items)}）</summary><ul>{lis}</ul></details>'


def search_entries(rel: str, page_title: str, body: str) -> list[dict]:
    """見出し単位の全文検索インデックス。"""
    entries = []
    for m in re.finditer(r'<h(\d) id="([^"]+)">(.*?)</h\1>(.*?)(?=<h\d id=|\Z)', body, re.S):
        text = html.unescape(re.sub(r"<[^>]+>", " ", m.group(4)))
        text = re.sub(r"\s+", " ", text).strip()
        entries.append({
            "u": f"{rel}#{m.group(2)}",
            "p": page_title,
            "h": html.unescape(re.sub(r"<[^>]+>", "", m.group(3))),
            "t": text,
        })
    return entries


def nav_html(root: str, current: str, nav: list[tuple[str, str]]) -> str:
    return "".join(
        f'<a class="{"current" if rel == current else ""}" href="{root}{rel}">{esc(label)}</a>'
        for rel, label in nav
    )


def build() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(STATIC, SITE / "static")
    base = Template((TEMPLATES / "base.html").read_text(encoding="utf-8"))
    built = datetime.now().strftime("%Y-%m-%d %H:%M")
    nav = [("index.html", "ホーム"), ("characters.html", "キャラ"), ("quests.html", "クエスト"), ("glossary.html", "用語"),
           ("sources/index.html", "資料"), ("search.html", "検索")]

    index: list[dict] = []
    global current_src
    for src, rel in pages():
        current_src = src
        md = src.read_text(encoding="utf-8")
        r = Renderer()
        body = r.render(md)
        title = title_of(md, src.stem)
        index.extend(search_entries(rel, title, body))
        root = "../" * rel.count("/")
        if rel == "index.html":
            body += analyses_html()
        content = toc_html(r.headings) + f'<article class="doc">{body}</article>'
        write(rel, base.substitute(title=esc(title), root=root, nav=nav_html(root, rel, nav),
                                   content=content, built=built, search_ui=page_search_ui()))

    search = (TEMPLATES / "search.html").read_text(encoding="utf-8")
    write("search.html", base.substitute(title="検索", root="", nav=nav_html("", "search.html", nav),
                                         content=search, built=built, search_ui=""))
    (SITE / "static" / "search-index.js").write_text(
        "window.SEARCH_INDEX = " + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")


def analyses_html() -> str:
    """ホームに載せる考察ページの一覧。"""
    items = [(src, rel) for src, rel in pages() if src.parent == ROOT and rel not in ("index.html", "glossary.html")]
    lis = "".join(
        f'<li><a href="{rel}">{esc(title_of(src.read_text(encoding="utf-8"), src.stem))}</a></li>' for src, rel in items
    ) or '<li class="muted">まだありません</li>'
    return f'<section class="s2"><h2 id="analyses">考察一覧</h2><ul>{lis}</ul></section>'


def page_search_ui() -> str:
    return ('<div class="find"><input type="search" id="find" placeholder="このページ内を絞り込み" '
            'autocomplete="off"><span id="find-count"></span></div>')


def write(rel: str, text: str) -> None:
    out = SITE / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    build()
    print(f"built {SITE.relative_to(ROOT)}")
