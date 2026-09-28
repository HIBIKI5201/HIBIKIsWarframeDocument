"""WARFRAME Wiki からキャラクターとクエストの情報を取り込み、Markdown を生成する。

    python StoryAnalysis/scripts/build_wiki.py [--refresh]

入力:
  data/characters.json  キャラクターの一覧（グループ・日本語の概要）。手で編集する
  data/quests.json      クエストの一覧（グループ・日本語名・日本語の概要）。手で編集する
出力（手で編集しない）:
  characters.md                一覧（グループごとに概要を表で並べる）
  quests.md                    一覧
  wiki/characters/<group>.md   グループごとのページ。キャラクターごとに 概要/基本情報/登場クエスト/詳細
  wiki/quests/<quest>.md       クエストごとのページ。概要/基本情報/登場キャラクター/詳細

Wiki の HTML は .cache/wiki/ に保存し、--refresh を付けない限り再取得しない。
キャラクターを 1 人 1 ページにしないのは、アーティファクトのファイル数上限（255）に収めるため。
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = ROOT / ".cache" / "wiki"
OUT = ROOT / "wiki"
API = "https://wiki.warframe.com/api.php"
WIKI = "https://wiki.warframe.com/w/"
UA = "WarframeDocument/1.0 (personal study notes)"
HEADER = "<!-- scripts/build_wiki.py で自動生成。手で編集しない（概要は data/*.json を編集する）。 -->\n"
LICENSE = ("詳細は [WARFRAME Wiki](https://wiki.warframe.com/) の記事（CC BY-SA）を元に日本語でまとめたもの。"
           "出典は各項目のリンク先。")

SKIP_SECTIONS = {"Media", "Gallery", "Localization", "References", "Patch History", "See Also", "See also",
                 "Navigation", "Walkthrough", "Rewards", "Notes and Trivia Links", "External Links"}
SKIP_CLASSES = {"infobox", "navbox", "mbox", "toc", "mw-editsection", "reference", "references",
                "mw-references-wrap", "gallery", "thumb", "noprint", "mw-empty-elt", "hatnote",
                "portable-infobox", "tooltip-content", "navigation-not-searchable"}
SKIP_TAGS = {"style", "script", "sup", "figure", "img", "noscript"}
# 普通名詞と紛らわしい名前は、台詞の話者としてだけ数える（本文中の言及は数えない）
AMBIGUOUS = {"Son", "Father", "Mother", "Daughter", "Grandmother", "Legs", "Pip", "Pol", "Ula", "Jade", "Boon",
             "Flare", "Whisper", "Violence", "Malice", "Mania", "Misery", "Torment", "Angst", "Operator", "Drifter",
             "Tenno", "Dax", "Vox", "Ticker", "Unum", "Scaldra", "Techrot", "Anarchs", "Raptors", "The Murmur",
             "The Prince", "The Warden", "The Business", "The Husband", "The Sergeant", "Stalker", "Kalymos",
             "Chipper", "Popcorn", "Rablit", "Sprodling", "Orowyrm", "Palanquin", "Myrmidon", "Arcane Machine",
             "Lotus", "Loid", "Aria", "Darro", "Cantis", "Olemedi", "Jubb Lott"}


# ---------------------------------------------------------------- 取得

def fetch(page: str, refresh: bool) -> dict | None:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (urllib.parse.quote(page, safe="") + ".json")
    if path.exists() and not refresh:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data or None
    q = urllib.parse.urlencode({"action": "parse", "page": page, "prop": "text|displaytitle", "redirects": 1,
                                "format": "json", "formatversion": 2})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                print(f"  取得失敗: {page} ({e})", file=sys.stderr)
                return None
            time.sleep(3)
    time.sleep(0.4)
    parsed = data.get("parse")
    result = {"title": parsed["title"], "html": parsed["text"]} if parsed else {}
    path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return result or None


# ---------------------------------------------------------------- HTML → Markdown

def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("|", "｜")


class ToMarkdown(HTMLParser):
    """Wiki 本文の HTML を、見出し・段落・リスト・引用だけの Markdown 行に変換する。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self.buf: list[str] = []
        self.skip = 0            # 読み飛ばし中の要素の深さ
        self.stack: list[tuple[str, bool]] = []  # (tag, 読み飛ばしの起点か)
        self.lists = 0
        self.quote = 0
        self.heading: int | None = None
        self.cells: list[str] | None = None

    def flush(self, prefix: str = "") -> None:
        text = clean("".join(self.buf))
        self.buf = []
        if not text:
            return
        if self.heading:
            self.lines.append(f"\0H{self.heading}\0{text}")
        elif self.cells is not None:
            self.cells.append(text)
        else:
            q = "> " if self.quote else ""
            self.lines.append(q + prefix + text)

    def handle_starttag(self, tag, attrs):
        if tag in ("br", "img", "hr", "wbr", "meta", "link", "input"):
            if tag == "br" and not self.skip:
                self.buf.append(" ")
            return
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        starts_skip = bool(self.skip == 0 and (tag in SKIP_TAGS or classes & SKIP_CLASSES
                                               or "display:none" in (a.get("style") or "").replace(" ", "")))
        self.stack.append((tag, starts_skip))
        if starts_skip or self.skip:
            self.skip += 1
            return
        if tag in ("h2", "h3", "h4", "h5"):
            self.flush()
            self.heading = int(tag[1])
        elif tag in ("p", "div", "dd", "dt", "blockquote", "tr"):
            self.flush()
            if tag == "blockquote":
                self.quote += 1
            if tag == "tr":
                self.cells = []
        elif tag in ("ul", "ol"):
            self.flush()
            self.lists += 1
        elif tag == "li":
            self.flush()
        elif tag in ("td", "th"):
            self.flush()
        if tag == "div" and a.get("data-title"):
            self.lines.append(f"**{clean(a['data-title'])}**")

    def handle_endtag(self, tag):
        if tag in ("br", "img", "hr", "wbr", "meta", "link", "input"):
            return
        while self.stack:
            t, starts_skip = self.stack.pop()
            if self.skip:
                self.skip -= 1
                if t == tag:
                    return
                continue
            self._close(t)
            if t == tag:
                return

    def _close(self, tag):
        if tag in ("h2", "h3", "h4", "h5"):
            self.flush()
            self.heading = None
        elif tag == "li":
            self.flush("  " * (self.lists - 1) + "- ")
        elif tag in ("td", "th"):
            self.flush()
        elif tag == "tr":
            self.flush()
            if self.cells:
                self.lines.append(("> " if self.quote else "") + "- " + " / ".join(self.cells))
            self.cells = None
        elif tag in ("ul", "ol"):
            self.flush("  " * (self.lists - 1) + "- ")
            self.lists = max(0, self.lists - 1)
        elif tag == "dt":
            text = clean("".join(self.buf))
            self.buf = []
            if text:
                self.lines.append(f"**{text}**")
        elif tag in ("p", "div", "dd", "blockquote", "table"):
            self.flush()
            if tag == "blockquote":
                self.quote = max(0, self.quote - 1)

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def to_sections(page_html: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """(導入部の行, [(h2 見出し, 行)]) に分ける。h3 以下は行の中に \\0H3\\0 形式で残す。"""
    p = ToMarkdown()
    p.feed(page_html)
    p.close()
    p.flush()
    intro: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    for line in p.lines:
        m = re.match(r"\0H(\d)\0(.*)", line)
        if m and m.group(1) == "2":
            sections.append((m.group(2), []))
        elif sections:
            sections[-1][1].append(line)
        else:
            intro.append(line)
    return intro, [(h, ls) for h, ls in sections if h not in SKIP_SECTIONS and any(l.strip() for l in ls)]


def infobox(page_html: str) -> list[tuple[str, str]]:
    i = page_html.find('class="infobox')
    if i < 0:
        return []
    j = page_html.find("<h2", i)
    box = page_html[i:j if j > 0 else i + 60000]
    rows = []
    for label, value in re.findall(r'<div class="label[^"]*">(.*?)</div>\s*<div class="value[^"]*">(.*?)</div>',
                                   box, re.S):
        label = clean(html.unescape(re.sub(r"<[^>]+>", " ", label)))
        value = clean(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(br|/p|/li)[^>]*>", " / ", value))))
        value = re.sub(r"(\s*/\s*)+", " / ", value).strip(" /")
        if label and value and len(value) < 400:
            rows.append((label, value))
    return rows


def render_lines(lines: list[str], base_level: int) -> list[str]:
    out, prev_blank = [], True
    for line in lines:
        m = re.match(r"\0H(\d)\0(.*)", line)
        if m:
            level = min(6, base_level + int(m.group(1)) - 3)
            out += ["", f"{'#' * level} {m.group(2)}", ""]
            continue
        is_item = line.lstrip("> ").startswith("- ")
        if not is_item and not prev_blank:
            out.append("")
        out.append(line)
        prev_blank = False
        if not is_item:
            out.append("")
            prev_blank = True
    return out


# ---------------------------------------------------------------- 見出し ID（build_site.py と同じ規則）

class Ids:
    def __init__(self) -> None:
        self.used: set[str] = set()

    def take(self, text: str) -> str:
        base = re.sub(r"[^0-9a-z]+", "-", text.lower()).strip("-") or "s"
        hid, n = base, 2
        while hid in self.used:
            hid, n = f"{base}-{n}", n + 1
        self.used.add(hid)
        return hid

    def scan(self, md_lines: list[str]) -> None:
        for line in md_lines:
            m = re.match(r"^(#{1,6})\s+(.*)$", line)
            if m:
                self.take(re.sub(r"\*\*|`|\[([^\]]+)\]\([^)]*\)", r"\1", m.group(2)))


def slug(text: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", text.lower()).strip("-")


def wiki_url(page: str) -> str:
    return WIKI + urllib.parse.quote(page.replace(" ", "_"), safe="_()/:-.,'")


# ---------------------------------------------------------------- 登場の判定

def speakers_and_text(page_html: str) -> tuple[dict[str, int], str]:
    speakers: dict[str, int] = {}
    for name in re.findall(r"<b>\s*([^<:]{1,40}?)\s*:\s*</b>", page_html):
        name = html.unescape(name).strip()
        speakers[name] = speakers.get(name, 0) + 1
    text = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<style.*?</style>", "", page_html, flags=re.S)))
    return speakers, text


def aliases(name: str) -> list[str]:
    base = re.sub(r"\s*\(.*?\)", "", name).strip()
    result = {base}
    if base.startswith("The "):
        result.add(base[4:])
    parts = base.split()
    if len(parts) > 1 and parts[0] in ("Captain", "Councilor", "General", "Lieutenant", "Executor", "Cephalon",
                                       "Archon", "Major", "Master", "Archimedean", "Lorist", "Dr.", "Sergeant"):
        result.add(" ".join(parts[1:]))
    elif len(parts) > 1 and parts[0] not in ("The", "Old", "Mother"):
        result.add(parts[0])
    return sorted(result, key=len, reverse=True)


# ---------------------------------------------------------------- 生成

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="Wiki から取り直す")
    refresh = ap.parse_args().refresh

    chars = json.loads((DATA / "characters.json").read_text(encoding="utf-8"))
    quests = json.loads((DATA / "quests.json").read_text(encoding="utf-8"))
    official_ja = dict(re.findall(r"^- (.+?)（(.+?)）$",
                                  (ROOT / "sources" / "quests.md").read_text(encoding="utf-8"), re.M))

    quest_list = [q for g in quests for q in g["items"]]
    q_slug = {q["page"]: slug(re.sub(r"\s*\(Quest\)", "", q["page"])) for q in quest_list}
    print(f"クエスト {len(quest_list)} 件を取得中...")
    q_page, q_trans = {}, {}
    for q in quest_list:
        q_page[q["page"]] = fetch(q["page"], refresh)
        q_trans[q["page"]] = fetch(q["page"] + "/Transcript", refresh)

    char_list = [(g["group"], c) for g in chars for c in g["items"] if c["page"]]
    print(f"キャラクター {len(char_list)} 件を取得中...")
    c_page = {c["page"]: fetch(c["page"], refresh) for _, c in char_list}

    # 台詞の話者と本文中の言及から、キャラクターごとの登場クエストを数える
    trans = {qp: speakers_and_text(d["html"]) for qp, d in q_trans.items() if d}
    appear: dict[str, list[tuple[str, int, int]]] = {}
    quest_cast: dict[str, list[tuple[str, int, int]]] = {qp: [] for qp in trans}
    for _, c in char_list:
        names = aliases(c["name"]) + ([] if c["page"] == c["name"] else aliases(c["page"]))
        for q in quest_list:
            if q["page"] not in trans:
                continue
            speakers, text = trans[q["page"]]
            said = sum(n for s, n in speakers.items() if any(s == a or s == "The " + a for a in names))
            mentioned = 0
            if c["name"] not in AMBIGUOUS and c["page"] not in AMBIGUOUS:
                for a in names:
                    if len(a) >= 5 and a not in AMBIGUOUS:
                        mentioned = max(mentioned, len(re.findall(rf"(?<![\w-]){re.escape(a)}(?![\w-])", text)))
            if said or mentioned >= 2:
                appear.setdefault(c["page"], []).append((q["page"], said, mentioned))
                quest_cast[q["page"]].append((c["page"], said, mentioned))

    # 各キャラクターがどのページのどの見出しにいるか（リンク用）を先に決める
    group_slug = {g["group"]: "g" + str(i + 1).zfill(2) + ("-" + slug(g["group"]) if slug(g["group"]) else "")
                  for i, g in enumerate(chars)}
    char_pages: dict[str, list[str]] = {}
    char_anchor: dict[str, str] = {}
    for g in chars:
        ids = Ids()
        lines = [HEADER, f"# {g['group']}", "", LICENSE, ""]
        ids.scan(lines)
        for c in g["items"]:
            if not c["page"]:
                continue
            body = char_section(c, c_page.get(c["page"]), appear.get(c["page"], []), quest_list, q_slug,
                                official_ja)
            char_anchor[c["page"]] = f"wiki/characters/{group_slug[g['group']]}.md#{ids.take(c['name'])}"
            ids.scan(body[1:])
            lines += body
        char_pages[group_slug[g["group"]]] = lines

    if OUT.exists():
        for f in OUT.rglob("*.md"):
            f.unlink()
    (OUT / "characters").mkdir(parents=True, exist_ok=True)
    (OUT / "quests").mkdir(parents=True, exist_ok=True)
    for name, lines in char_pages.items():
        write(OUT / "characters" / f"{name}.md", lines)

    for q in quest_list:
        write(OUT / "quests" / f"{q_slug[q['page']]}.md",
              quest_page(q, q_page.get(q["page"]), q_trans.get(q["page"]), quest_cast.get(q["page"], []),
                         char_anchor, official_ja))

    write(ROOT / "characters.md", character_index(chars, char_anchor, appear))
    write(ROOT / "quests.md", quest_index(quests, q_slug, quest_cast, official_ja))
    missing = [c["page"] for _, c in char_list if not c_page.get(c["page"])]
    print(f"完了: キャラクター {len(char_list)} 件（Wiki になし {len(missing)} 件）/ クエスト {len(quest_list)} 件")
    if missing:
        print("  Wiki になし: " + ", ".join(missing))


JA = DATA / "ja"            # 日本語訳（手で書く）: ja/<kind>/<key>.md
SRC = ROOT / ".cache" / "wiki_src"  # 翻訳の元になる英語本文（自動で書き出す）
LABELS = {"Faction": "所属", "Factions": "所属", "Species": "種族", "Race": "種族", "Gender": "性別", "Status": "状態",
          "Location": "場所", "Locations": "場所", "Planet": "惑星", "Occupation": "職業", "Title": "称号",
          "Titles": "称号", "Affiliation": "所属", "Affiliations": "所属", "Voice": "声優", "Voice Actor": "声優",
          "Voice actor": "声優", "Relatives": "親族", "Family": "家族", "Relationships": "関係",
          "Introduced": "初登場", "Debut": "初登場", "Release Date": "実装日", "Released": "実装日",
          "Prerequisite": "前提", "Prerequisites": "前提", "Rewards": "報酬", "Reward": "報酬",
          "Quest Giver": "依頼者", "Type": "種類", "Next": "次のクエスト", "Previous": "前のクエスト",
          "Aliases": "別名", "Alias": "別名", "Age": "年齢", "Allies": "味方", "Enemies": "敵",
          "Requirement": "条件", "Requirements": "条件", "Previous Quest": "前のクエスト", "Next Quest": "次のクエスト", "Replayable": "再プレイ", "Transcript": "台詞全文", "Voice Actor(s)": "声優", "Home": "拠点", "Mastery Rank": "マスタリーランク", "Weapons": "武器", "Weapon": "武器", "Warframe": "Warframe", "Syndicate": "シンジケート"}


STORY_SECTIONS = re.compile(r"^(Lore.*|History|Background|Biography|Personality|Appearance|Overview|General|"
                            r"Creation|Fansite Bio|Synopsis|Plot|Story|Trivia|Relationships?|Quotes|Cinematic.*|"
                            r"Known .*|Flavor Text)$")


def src_text(intro, sections, box) -> str:
    """翻訳用に英語本文をまとめた Markdown。"""
    out = ["## Intro", ""] + [l.lstrip("> ") for l in intro] + [""]
    for head, lines in sections:
        out += [f"## {head}", ""] + render_lines(lines, base_level=3)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def ja_parts(kind: str, key: str) -> tuple[list[str], list[tuple[str, list[str]]]] | None:
    """日本語訳ファイルを (要約の行, [(見出し, 行)]) に分ける。「## 要約」以外の ## が詳細の章になる。"""
    path = JA / kind / f"{key}.md"
    if not path.exists():
        return None
    summary: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            cur = m.group(1).strip()
            if cur != "要約":
                sections.append((cur, []))
            continue
        if cur == "要約":
            summary.append(line)
        elif sections:
            sections[-1][1].append(line)
    return summary, sections


def shift(lines: list[str], add: int) -> list[str]:
    return [("#" * min(6, len(m.group(1)) + add) + " " + m.group(2)) if (m := re.match(r"^(#{3,6})\s+(.*)$", l)) else l
            for l in lines]


def body(kind, key, page, box, h: int, missing_note: str) -> tuple[list[str], list[str]]:
    """(概要に足す行, 詳細の行)。日本語訳があればそれを、なければ英語の原文を使う。h は詳細の章の見出しレベル。"""
    intro, sections = to_sections(page["html"]) if page else ([], [])
    sections = [(h, ls) for h, ls in sections if STORY_SECTIONS.match(h)]  # 攻略情報は Wiki に任せる
    if page:
        SRC.joinpath(kind).mkdir(parents=True, exist_ok=True)
        SRC.joinpath(kind, f"{key}.md").write_text(src_text(intro, sections, box), encoding="utf-8")
    ja = ja_parts(kind, key)
    if ja:
        summary, jsec = ja
        detail = []
        for head, lines in jsec:
            detail += [f"{'#' * h} {head}", ""] + shift(lines, h - 2) + [""]
        return summary + [""], detail
    if not page:
        return [], [missing_note, ""]
    head_lines = [f"> {l.lstrip('> ')}" for l in intro if not l.startswith("**")][:4]
    detail = ["（日本語訳はまだない。以下は Wiki の英語原文）", ""] if sections else []
    for head, lines in sections:
        detail += [f"{'#' * h} {head}", ""] + render_lines(lines, base_level=h + 1)
    return head_lines + [""], detail


def box_rows(box) -> list[str]:
    return ["| 項目 | 内容 |", "| --- | --- |"] + [f"| {LABELS.get(k, k)} | {v} |" for k, v in box] + [""]


# 名前だけ出てくる人物で、リンク先がその人物の記事ではないもの（詳細は載せない）
LINK_ONLY = {"Little Duck/Quotes", "Styanax", "Red Veil", "Kuria", "Venato Prime", "Archimedean"}


def char_section(c, page, appears, quest_list, q_slug, official_ja) -> list[str]:
    out = ["", f"## {c['name']}", "", "### 概要", "", c["ja"], ""]
    box = infobox(page["html"]) if page and c["page"] not in LINK_ONLY else []
    if c["page"] in LINK_ONLY:
        extra, detail = [], []
    else:
        extra, detail = body("characters", slug(c["page"]), page, box, 4, "（Wiki に個別ページがない）")
    out += extra
    title = page["title"] if page else c["page"]
    out += [f"出典: [WARFRAME Wiki]({wiki_url(title)})", ""]
    if box:
        out += ["### 基本情報", ""] + box_rows(box)
    if appears:
        order = {q["page"]: i for i, q in enumerate(quest_list)}
        out += ["### 登場クエスト", "", "台詞全文（Transcript）での登場。台詞は話者として出てくる回数、言及は本文中で名前が出る回数。", "",
                "| クエスト | 台詞 | 言及 |", "| --- | --- | --- |"]
        for qp, said, men in sorted(appears, key=lambda a: order[a[0]]):
            label = official_ja.get(re.sub(r"\s*\(Quest\)", "", qp), qp)
            out.append(f"| [{label}](../quests/{q_slug[qp]}.md) | {said or ''} | {men or ''} |")
        out.append("")
    if detail:
        out += ["### 詳細", ""] + detail
    return out


def quest_page(q, page, trans, cast, char_anchor, official_ja) -> list[str]:
    name = re.sub(r"\s*\(Quest\)", "", q["page"])
    ja = official_ja.get(name, q["ja"])
    out = [HEADER, f"# {ja}（{name}）", "", LICENSE, "", "## 概要", "", q["summary"], ""]
    box = infobox(page["html"]) if page else []
    extra, detail = body("quests", slug(name), page, box, 3, "")
    out += extra
    links = [f"[WARFRAME Wiki]({wiki_url(q['page'])})"]
    if trans:
        links.append(f"[台詞全文]({wiki_url(q['page'] + '/Transcript')})")
    out += ["出典: " + " / ".join(links), ""]
    if box:
        out += ["## 基本情報", ""] + box_rows(box)
    if cast:
        out += ["## 登場キャラクター", "", "台詞全文での登場。台詞は話者として出てくる回数、言及は本文中で名前が出る回数。", "",
                "| キャラクター | 台詞 | 言及 |", "| --- | --- | --- |"]
        for cp, said, men in sorted(cast, key=lambda x: (-x[1], -x[2])):
            target = char_anchor.get(cp)
            label = f"[{cp}](../../{target})" if target else cp
            out.append(f"| {label} | {said or ''} | {men or ''} |")
        out.append("")
    if detail:
        out += ["## 詳細", ""] + detail
    return out


def character_index(chars, char_anchor, appear) -> list[str]:
    total = sum(len(g["items"]) for g in chars)
    out = [HEADER, "# キャラクター一覧", "",
           f"WARFRAME Wiki のキャラクター {total} 件。名前から詳細（基本情報・登場クエスト・Wiki の経歴など）へ飛べる。",
           "概要は `data/characters.json` に書いたもの、詳細は Wiki から自動で取り込んだ英語の本文。", ""]
    for g in chars:
        out += [f"## {g['group']}", "", "| 名前 | 概要 | 登場 |", "| --- | --- | --- |"]
        for c in g["items"]:
            target = char_anchor.get(c["page"]) if c["page"] else None
            name = f"[{c['name']}]({target})" if target else c["name"]
            n = len(appear.get(c["page"], [])) if c["page"] else 0
            out.append(f"| {name} | {c['ja']} | {f'{n} クエスト' if n else ''} |")
        out.append("")
    return out


def quest_index(quests, q_slug, cast, official_ja) -> list[str]:
    out = [HEADER, "# クエスト一覧", "",
           "WARFRAME Wiki のクエスト。名前から詳細（基本情報・登場キャラクター・Wiki のあらすじなど）へ飛べる。",
           "メインストーリーは Wiki 上の時系列順。", ""]
    for g in quests:
        out += [f"## {g['group']}", "", "| クエスト | 概要 | 登場キャラ |", "| --- | --- | --- |"]
        for q in g["items"]:
            name = re.sub(r"\s*\(Quest\)", "", q["page"])
            ja = official_ja.get(name, q["ja"])
            n = len(cast.get(q["page"], []))
            out.append(f"| [{ja}](wiki/quests/{q_slug[q['page']]}.md) / {name} | {q['summary']} | {n or ''} |")
        out.append("")
    return out


def write(path: Path, lines: list[str]) -> None:
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
