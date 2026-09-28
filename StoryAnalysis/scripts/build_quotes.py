"""WARFRAME Wiki の Category:Quotes（キャラクター・場所・ミッションのセリフ集と、クエストの台詞全文）をすべて取り込む。

    python StoryAnalysis/scripts/build_quotes.py [--refresh]

出力（手で編集しない。内容は WARFRAME Wiki の記事を元にしたもの: CC BY-NC-SA 3.0）:
  quotes/data/<key>.json   1 ページずつのデータ。節（見出しの階層）ごとのセリフ [本文, 音声ファイル名]
  quotes/<key>.md          1 ページずつのセリフ集
  quotes/idle.md           独り言・待機中・雑談など、場面を問わず口にするセリフだけを全ページから集めたもの
  quotes/README.md         一覧

セリフは英語原文（公式の日本語字幕はゲームデータの公開分に含まれない）。
Wiki の HTML は .cache/wiki/ に保存し（build_wiki.py と共有）、--refresh を付けない限り再取得しない。
キャラクター・クエストのページからのリンクは render_wiki.py が quotes/data/ を読んで付ける。
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

import build_wiki
from build_wiki import clean, slug, wiki_url

ROOT = build_wiki.ROOT
OUT = ROOT / "quotes"
DATA_OUT = OUT / "data"
CATEGORY = "Category:Quotes"
HEADER = "<!-- scripts/build_quotes.py で自動生成。手で編集しない。 -->\n"
LICENSE = ("[WARFRAME Wiki](https://wiki.warframe.com/) の記事を元にしたもの"
           "（[CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/deed.ja)）。セリフの権利は Digital Extremes Ltd. にある。")
# 独り言・待機中・雑談など、場面を問わず口にするセリフの節（見出しのどこかに含まれていれば対象）
IDLE = re.compile(r"\b(idle|ambient|ambience|chatter|banter|bored|musings?|random|flavou?r|small talk|"
                  r"citizens|passers?-?by|overheard|barks?|radio chatter)\b", re.I)
# ページ全体が街の住民の雑談・ラジオなどのもの
CROWD = {"Cetus/Quotes", "Fortuna/Quotes", "Duviri/Quotes/Citizens", "Orbiter/Radio"}
KINDS = ("キャラクター", "クエスト（台詞全文）", "場所・ミッション・その他")


# ---------------------------------------------------------------- 取得

def members() -> list[str]:
    titles, cont = [], {}
    while True:
        q = urllib.parse.urlencode({"action": "query", "list": "categorymembers", "cmtitle": CATEGORY,
                                    "cmlimit": "max", "cmnamespace": 0, "format": "json", **cont})
        req = urllib.request.Request(f"{build_wiki.API}?{q}", headers={"User-Agent": build_wiki.UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
        titles += [m["title"] for m in data["query"]["categorymembers"]]
        if "continue" not in data:
            return titles
        cont = data["continue"]


def load_members(refresh: bool) -> list[str]:
    path = build_wiki.CACHE / "_category_quotes.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    titles = members()
    build_wiki.CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(titles, ensure_ascii=False), encoding="utf-8")
    return titles


# ---------------------------------------------------------------- HTML → データ

AUDIO = re.compile(r'(?:<dl>\s*)?<span class="audio-button">.*?data-mwtitle="([^"]+)".*?</audio>.*?'
                   r'\(<a[^>]*>download</a>,\s*<a[^>]*>history</a>\)(?:\s*</dl>)?', re.S)


def parse(page_html: str) -> list[dict]:
    """[{"path": [見出し…], "lines": [{"text": Markdown, "audio": ファイル名 | None}]}]"""
    page_html = AUDIO.sub(lambda m: f" \x01{m.group(1)}\x01 ", page_html)
    p = build_wiki.ToMarkdown()
    p.feed(page_html)
    p.close()
    p.flush()
    sections: list[dict] = [{"path": [], "lines": []}]
    path: list[tuple[int, str]] = []
    skip_level = None
    for line in p.lines:
        m = re.match(r"\0H(\d)\0(.*)", line)
        if m:
            level, head = int(m.group(1)), clean(m.group(2))
            if skip_level and level > skip_level:
                continue
            skip_level = level if head in build_wiki.SKIP_SECTIONS else None
            path = [(lv, h) for lv, h in path if lv < level] + [(level, head)]
            sections.append({"path": [h for _, h in path], "lines": []})
            continue
        if skip_level:
            continue
        audio = re.findall(r"\x01([^\x01]+)\x01", line)
        text = clean(re.sub(r"\x01[^\x01]+\x01", " ", line))
        if not text.strip("-> ") and audio and sections[-1]["lines"] and not sections[-1]["lines"][-1]["audio"]:
            sections[-1]["lines"][-1]["audio"] = audio[0]  # 音声だけが次の行に分かれたとき
            continue
        if not text.strip("-> "):
            continue
        if not path and not audio and len(text.split()) < 4:
            continue  # 冒頭のタブの見出し（ページ名など）
        sections[-1]["lines"].append({"text": text, "audio": audio[0] if audio else None})
    return [s for s in sections if s["lines"]]


def classify(title: str, chars: dict[str, dict], quests: dict[str, dict]) -> tuple[str, dict | None]:
    subject = re.sub(r"/(Quotes|Transcript).*$", "", title)
    if title.endswith("/Transcript") or subject.lower() in quests:
        return "クエスト（台詞全文）", quests.get(subject.lower()) or quests.get(re.sub(r"\s*\(Quest\)$", "", subject).lower())
    if subject.lower() in chars:
        return "キャラクター", chars[subject.lower()]
    return "場所・ミッション・その他", None


def site_records(kind: str) -> dict[str, dict]:
    out = {}
    for f in sorted((ROOT / "wiki" / "data" / kind).glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        for n in (r["name"], r["page"]):
            out.setdefault(n.lower(), {"key": r["key"], "name": r.get("ja") or r["name"], "page": r["page"]})
    return out


# ---------------------------------------------------------------- ページ

def line_md(line: dict) -> str:
    text = line["text"]
    if not re.match(r"^(> )?\s*- ", text):
        text = "- " + text.lstrip("> ")
    if line["audio"]:
        text += f" [音声]({wiki_url('File:' + line['audio'])})"
    return text


def quote_page(rec: dict) -> list[str]:
    own = ""
    if rec["site"]:
        kind = "quests" if rec["kind"].startswith("クエスト") else "characters"
        own = f" / このサイトのページ: [{rec['site']['name']}](../wiki/{kind}/{rec['site']['key']}.md)"
    out = [HEADER, f"# {rec['title']}", "",
           f"[セリフ集の一覧](README.md) › {rec['kind']}", "",
           f"出典: [WARFRAME Wiki「{rec['title']}」]({rec['url']}){own}。{LICENSE}", "",
           f"{rec['count']} 行（うち独り言・待機中・雑談など {rec['idle']} 行）。英語原文。", ""]
    for s in rec["sections"]:
        if s["path"]:
            level = min(6, len(s["path"]) + 1)
            out += ["", f"{'#' * level} {s['path'][-1]}", ""]
        out += [line_md(l) for l in s["lines"]] + [""]
    return out


def idle_page(recs: list[dict]) -> list[str]:
    out = [HEADER, "# 独り言・待機中・雑談のセリフ", "", "[セリフ集の一覧](README.md)", "",
           "全セリフ集から、見出しが Idle・Ambient・Chatter・Banter・Citizens などの節（場面を問わず口にするセリフ）と、"
           "街の住民の雑談・ラジオのページ（Cetus・Fortuna・Duviri の住民・オービターのラジオ）を集めたもの。"
           f"英語原文。{LICENSE}", ""]
    for kind in KINDS:
        group = [r for r in recs if r["kind"] == kind and r["idle"]]
        if not group:
            continue
        out += [f"## {kind}", ""]
        for r in group:
            out += ["", f"### {r['title']}", "", f"[全セリフ]({r['key']}.md) / [Wiki]({r['url']})", ""]
            for s in r["sections"]:
                if s["idle"]:
                    out += [f"**{' › '.join(s['path']) or '（ページ冒頭）'}**", ""] + [line_md(l) for l in s["lines"]] + [""]
    return out


def index_page(recs: list[dict]) -> list[str]:
    total = sum(r["count"] for r in recs)
    idle = sum(r["idle"] for r in recs)
    out = [HEADER, "# セリフ集", "",
           f"WARFRAME Wiki の [Quotes カテゴリ](https://wiki.warframe.com/w/{CATEGORY.replace(' ', '_')}) の {len(recs)} ページ、"
           f"{total} 行を取り込んだもの（英語原文）。{LICENSE}", "",
           f"- [独り言・待機中・雑談のセリフだけを集めたページ](idle.md)（{idle} 行）",
           "- 全文検索の種類「セリフ」で、全ページのセリフを横断して探せる", ""]
    for kind in KINDS:
        group = [r for r in recs if r["kind"] == kind]
        out += [f"## {kind}", "", "| ページ | 行数 | 独り言など | このサイトのページ |", "| --- | --- | --- | --- |"]
        for r in group:
            own = ""
            if r["site"]:
                k = "quests" if kind.startswith("クエスト") else "characters"
                own = f"[{r['site']['name']}](../wiki/{k}/{r['site']['key']}.md)"
            out.append(f"| [{r['title']}]({r['key']}.md) | {r['count']} | {r['idle'] or ''} | {own} |")
        out.append("")
    return out


def save(r: dict) -> None:
    """1 節 1 行の JSON。セリフは [Markdown, 音声ファイル名 | null] の組にして小さくする。"""
    head = json.dumps({k: v for k, v in r.items() if k != "sections"}, ensure_ascii=False, indent=1)[:-2]
    secs = ",\n".join("  " + json.dumps({"path": s["path"], "idle": s["idle"],
                                         "lines": [[l["text"], l["audio"]] for l in s["lines"]]}, ensure_ascii=False)
                      for s in r["sections"])
    (DATA_OUT / f"{r['key']}.json").write_text(f'{head},\n "sections": [\n{secs}\n ]\n}}\n',
                                              encoding="utf-8", newline="\n")


def is_idle(section: dict) -> bool:
    return any(IDLE.search(h) for h in section["path"])


def write(path: Path, lines: list[str]) -> None:
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="Wiki から取り直す")
    refresh = ap.parse_args().refresh
    titles = load_members(refresh)
    chars, quests = site_records("characters"), site_records("quests")
    print(f"セリフのページ {len(titles)} 件を取得中...")
    recs, used = [], set()
    for title in titles:
        page = build_wiki.fetch(title, refresh)
        if not page:
            continue
        sections = parse(page["html"])
        kind, site = classify(title, chars, quests)
        key = slug(title.replace("/Quotes", "").replace("/Transcript", "-transcript")) or "page"
        while key in used:
            key += "-2"
        used.add(key)
        recs.append({"key": key, "title": title, "url": wiki_url(title), "kind": kind, "site": site,
                     "count": sum(len(s["lines"]) for s in sections),
                     "idle": 0, "sections": sections})
        for sec in sections:
            sec["idle"] = title in CROWD or is_idle(sec)
        recs[-1]["idle"] = sum(len(sec["lines"]) for sec in sections if sec["idle"])
    recs.sort(key=lambda r: (KINDS.index(r["kind"]), r["title"].lower()))

    for f in list(OUT.glob("*.md")) + list(DATA_OUT.glob("*.json")):
        f.unlink()
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    for r in recs:
        save(r)
        write(OUT / f"{r['key']}.md", quote_page(r))
    write(OUT / "idle.md", idle_page(recs))
    write(OUT / "README.md", index_page(recs))
    print(f"完了: {len(recs)} ページ / {sum(r['count'] for r in recs)} 行"
          f"（独り言など {sum(r['idle'] for r in recs)} 行）→ {OUT.relative_to(ROOT).as_posix()}")
    import render_wiki  # キャラクター・クエストのページにセリフ集へのリンクを付け直す
    render_wiki.main()


if __name__ == "__main__":
    main()
