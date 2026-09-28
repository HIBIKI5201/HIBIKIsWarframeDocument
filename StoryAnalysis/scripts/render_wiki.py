"""wiki/data/ のデータ（build_wiki.py が作る）から、キャラクター・クエストのページを生成する。

    python StoryAnalysis/scripts/render_wiki.py

入力:
  data/characters.json・data/quests.json  並び順とグループ（手で編集する）
  wiki/data/<kind>/<key>.json              1 件ずつのデータ（build_wiki.py が作る）
  fandom-ja/terms.json                     日本語 Wiki の記事（あればリンクする。build_fandom_ja.py が作る）
  quotes/data/*.json                       セリフ集（あればリンクする。build_quotes.py が作る）
出力（手で編集しない）:
  characters.md・quests.md        一覧
  wiki/characters/<key>.md        キャラクター 1 人 1 ページ
  wiki/characters/<group>.md      グループのページ（旧来の「グループ内の見出し」へのリンクもここで受ける）
  wiki/quests/<key>.md            クエスト 1 件 1 ページ

ネットワークには出ないので、ページの見た目だけを変えるときはこれだけを実行すればよい。
"""
from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "wiki"
WIKI_DATA = OUT / "data"
HEADER = ("<!-- scripts/render_wiki.py で自動生成。手で編集しない"
          "（概要は data/*.json、訳は data/ja/ を編集して build_wiki.py を実行する）。 -->\n")
LICENSE = ("このページの詳細・基本情報は [WARFRAME Wiki](https://wiki.warframe.com/) の記事を元にしたもの"
           "（[CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/deed.ja)）。出典は「リンク」の記事。")


def slug(text: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", text.lower()).strip("-")


class Ids:
    """見出し ID（build_site.py と同じ規則）。"""

    def __init__(self) -> None:
        self.used: set[str] = set()

    def take(self, text: str) -> str:
        base = slug(text) or "s"
        hid, n = base, 2
        while hid in self.used:
            hid, n = f"{base}-{n}", n + 1
        self.used.add(hid)
        return hid


def load(kind: str) -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((WIKI_DATA / kind).glob("*.json"))}


class JaWiki:
    """日本語 Wiki（fandom-ja/terms.json）の記事を英語名から引く。"""

    def __init__(self) -> None:
        path = ROOT / "fandom-ja" / "terms.json"
        self.by_en: dict[str, dict] = {}
        if path.exists():
            for t in json.loads(path.read_text(encoding="utf-8"))["terms"]:
                for e in t["en"]:
                    self.by_en.setdefault(e.lower(), t)

    def find(self, *names: str) -> dict | None:
        return next((self.by_en[n.lower()] for n in names if n and n.lower() in self.by_en), None)


def search_link(prefix: str, term: str) -> str:
    return f"[全文検索]({prefix}search.html?q={urllib.parse.quote(term)})"


def links(rec: dict, ja: dict | None, prefix: str, extra: list[str] = ()) -> str:
    """「リンク」の行。prefix は StoryAnalysis/ への相対パス。"""
    items = [f"[WARFRAME Wiki]({rec['wiki']['url']})（英語・出典）"] if rec["wiki"]["exists"] else []
    items += list(extra)
    if ja:
        items.append(f"[日本語 Wiki「{ja['ja'][0]}」]({ja['url']})")
        if ja.get("local"):
            items.append(f"[日本語 Wiki の取り込み]({prefix}fandom-ja/{ja['local']})")
    items.append(search_link(prefix, rec["name"]))
    return "リンク: " + " / ".join(items)


def infobox_rows(rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    return (["## 基本情報", "", "| 項目 | 内容 |", "| --- | --- |"]
            + [f"| {k} | {v} |" for k, v in rows] + [""])


def detail(body: dict, source: str) -> list[str]:
    out = []
    if body["lang"] == "en" and body["sections"]:
        out += [f"以下の章は {source} の英語原文（日本語訳はまだない）。", ""]
    for head, lines in body["sections"]:
        out += [f"## {head}", ""] + lines + [""]
    return out


def nav(parts: list[str], prev: tuple[str, str] | None, nxt: tuple[str, str] | None) -> list[str]:
    line = " › ".join(parts)
    if prev:
        line += f" ・ ← [{prev[0]}]({prev[1]})"
    if nxt:
        line += f" ・ [{nxt[0]}]({nxt[1]}) →"
    return [line, ""]


def neighbors(items: list, i: int) -> tuple:
    return (items[i - 1] if i > 0 else None), (items[i + 1] if i + 1 < len(items) else None)


def quotes_by_site() -> dict[tuple[str, str], list[dict]]:
    """セリフ集（build_quotes.py が作る quotes/data/）を、このサイトのキャラクター・クエストごとにまとめる。"""
    out: dict[tuple[str, str], list[dict]] = {}
    for f in sorted((ROOT / "quotes" / "data").glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        if r["site"]:
            kind = "quests" if r["kind"].startswith("クエスト") else "characters"
            out.setdefault((kind, r["site"]["key"]), []).append(r)
    return out


def quote_item(label: str, r: dict) -> str:
    idle = f"、うち独り言など {r['idle']} 行" if r["idle"] else ""
    return f"- {label}: [{r['title']}](../../quotes/{r['key']}.md)（{r['count']} 行{idle}）"


# ---------------------------------------------------------------- ページ

def character_page(c: dict, group_chars: list[dict], quests: dict[str, dict], ja: JaWiki, said: list[dict]) -> list[str]:
    i = next(n for n, x in enumerate(group_chars) if x["key"] == c["key"])
    prev, nxt = (x and (x["name"], f"{x['key']}.md") for x in neighbors(group_chars, i))
    out = [HEADER, f"# {c['name']}", ""]
    out += nav(["[キャラクター一覧](../../characters.md)", f"[{c['group']}]({c['group_key']}.md)"], prev, nxt)
    out += ["## 概要", "", c["summary"], ""] + c["body"]["summary"] + [""]
    n = len(c["quests"])
    out += [f"- グループ: [{c['group']}]({c['group_key']}.md)",
            f"- 登場: {n} クエスト（台詞全文から数えたもの。下の表）" if n else "- 登場: 台詞全文では見つからない"]
    out += [quote_item("セリフ集", r) for r in said] + [""]
    if c["link_only"]:
        out += ["Wiki に個別の記事がない（名前のリンク先は別の記事）。", ""]
    elif not c["wiki"]["exists"]:
        out += ["Wiki に個別の記事がない。", ""]
    out += [links(c, ja.find(c["name"], c["page"]), "../../"), ""]
    out += infobox_rows(c["infobox"])
    if c["quests"]:
        out += ["## 登場クエスト", "", "台詞全文（Transcript）での登場。台詞は話者として出てくる回数、言及は本文中で名前が出る回数。", "",
                "| クエスト | 台詞 | 言及 |", "| --- | --- | --- |"]
        for qk, said, men in c["quests"]:
            q = quests[qk]
            out.append(f"| [{q['ja']}](../quests/{qk}.md) | {said or ''} | {men or ''} |")
        out.append("")
    out += detail(c["body"], "Wiki")
    return out + ["---", "", LICENSE]


def group_page(group: str, chars: list[dict]) -> list[str]:
    out = [HEADER, f"# {group}", "", "[キャラクター一覧](../../characters.md) › " + group, "",
           f"{len(chars)} 人。名前から 1 人ずつのページへ飛べる。", ""]
    for c in chars:
        n = len(c["quests"])
        out += [f"## {c['name']}", "", c["summary"], "",
                f"[{c['name']} のページ]({c['key']}.md)" + (f"（登場 {n} クエスト）" if n else ""), ""]
    return out


def quest_page(q: dict, order: list[dict], chars: dict[str, dict], ja: JaWiki, said: list[dict]) -> list[str]:
    i = next(n for n, x in enumerate(order) if x["key"] == q["key"])
    prev, nxt = (x and (x["ja"], f"{x['key']}.md") for x in neighbors(order, i))
    out = [HEADER, f"# {q['ja']}（{q['name']}）", ""]
    out += nav(["[クエスト一覧](../../quests.md)", q["group"]], prev, nxt)
    out += ["## 概要", "", q["summary"], ""] + q["body"]["summary"] + [""]
    extra = [f"[台詞全文]({q['transcript']})"] if q["transcript"] else []
    if said:
        out += [quote_item("台詞全文（取り込み）", r) for r in said] + [""]
    out += [links(q, ja.find(q["name"], q["page"]), "../../", extra), ""]
    out += infobox_rows(q["infobox"])
    if q["characters"]:
        out += ["## 登場キャラクター", "", "台詞全文での登場。台詞は話者として出てくる回数、言及は本文中で名前が出る回数。", "",
                "| キャラクター | グループ | 台詞 | 言及 |", "| --- | --- | --- | --- |"]
        for ck, said, men in q["characters"]:
            c = chars[ck]
            out.append(f"| [{c['name']}](../characters/{ck}.md) | {c['group']} | {said or ''} | {men or ''} |")
        out.append("")
    out += detail(q["body"], "Wiki")
    return out + ["---", "", LICENSE]


def character_index(groups: list[tuple[str, list[dict]]], total: int) -> list[str]:
    out = [HEADER, "# キャラクター一覧", "",
           f"WARFRAME Wiki のキャラクター {total} 人。名前から 1 人ずつのページ（基本情報・登場クエスト・経歴など）へ飛べる。",
           "上の欄に入れた語で表の行を絞り込める（`characters.html?q=Grineer` のように URL でも指定できる）。", ""]
    for group, chars in groups:
        out += [f"## {group}", "", f"グループのページ: [{group}](wiki/characters/{chars[0]['group_key']}.md)", "",
                "| 名前 | 概要 | 登場 |", "| --- | --- | --- |"]
        for c in chars:
            n = len(c["quests"])
            out.append(f"| [{c['name']}](wiki/characters/{c['key']}.md) | {c['summary']} | {f'{n} クエスト' if n else ''} |")
        out.append("")
    return out


def quest_index(groups: list[tuple[str, list[dict]]]) -> list[str]:
    out = [HEADER, "# クエスト一覧", "",
           "WARFRAME Wiki のクエスト。名前から 1 件ずつのページ（基本情報・登場キャラクター・あらすじなど）へ飛べる。",
           "メインストーリーは Wiki 上の時系列順で、各ページの「←」「→」で前後のクエストへ移れる。",
           "上の欄に入れた語で表の行を絞り込める（`quests.html?q=Lotus` のように URL でも指定できる）。", ""]
    for group, quests in groups:
        out += [f"## {group}", "", "| クエスト | 概要 | 登場キャラ |", "| --- | --- | --- |"]
        for q in quests:
            n = len(q["characters"])
            out.append(f"| [{q['ja']}](wiki/quests/{q['key']}.md) / {q['name']} | {q['summary']} | {n or ''} |")
        out.append("")
    return out


def write(path: Path, lines: list[str]) -> None:
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    chars, quests = load("characters"), load("quests")
    if not chars or not quests:
        raise SystemExit("wiki/data/ がない。先に python StoryAnalysis/scripts/build_wiki.py を実行する")
    ja = JaWiki()
    said = quotes_by_site()
    char_groups = [(g["group"], [chars[slug(c["page"])] for c in g["items"] if c["page"] and slug(c["page"]) in chars])
                   for g in json.loads((DATA / "characters.json").read_text(encoding="utf-8"))]
    char_groups = [(g, cs) for g, cs in char_groups if cs]
    quest_groups = [(g["group"], [quests[slug(re.sub(r"\s*\(Quest\)$", "", q["page"]))] for q in g["items"]])
                    for g in json.loads((DATA / "quests.json").read_text(encoding="utf-8"))]
    quest_order = [q for _, qs in quest_groups for q in qs]

    for f in list(OUT.glob("characters/*.md")) + list(OUT.glob("quests/*.md")):
        f.unlink()
    for group, cs in char_groups:
        write(OUT / "characters" / f"{cs[0]['group_key']}.md", group_page(group, cs))
        for c in cs:
            write(OUT / "characters" / f"{c['key']}.md", character_page(c, cs, quests, ja, said.get(('characters', c['key']), [])))
    for q in quest_order:
        write(OUT / "quests" / f"{q['key']}.md", quest_page(q, quest_order, chars, ja, said.get(('quests', q['key']), [])))
    write(ROOT / "characters.md", character_index(char_groups, len(chars)))
    write(ROOT / "quests.md", quest_index(quest_groups))
    print(f"ページ: キャラクター {len(chars)} 件・グループ {len(char_groups)} 件・クエスト {len(quest_order)} 件")


if __name__ == "__main__":
    main()
