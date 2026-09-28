"""日本語版 Warframe Wiki（Fandom, https://warframe.fandom.com/ja/）から用語とストーリー情報を取り込む。

    python StoryAnalysis/scripts/build_fandom_ja.py [--refresh]

出力（手で編集しない。内容は CC BY-SA 3.0）:
  fandom-ja/README.md          取り込んだページの一覧・出典・ライセンス
  fandom-ja/terms.md           用語対応表（英語 ⇔ 日本語 Wiki での表記）
  fandom-ja/terms.json         同じ内容の機械可読版
  fandom-ja/pages/<name>.md    ストーリー関連ページ（クエスト・キャラクター・勢力・伝承の節があるページ）の本文

用語の英語名は、次のどれかから機械的に取る。
  英語版への言語間リンク / 英字の転送ページ / 冒頭の「'''オロキン'''（Orokin）」のような太字 / クエストの「英語名称」

Wiki の本文（ウィキテキスト）は .cache/fandom_ja/ に保存し、--refresh を付けない限り再取得しない。
ページの HTML は版（revid）ごとに保存するので、--refresh で更新されたページだけ取り直す。
scripts/terms.py は Index() を使って、glossary.md の「未確認」の語を日本語 Wiki の表記で確認する。
"""
from __future__ import annotations

import argparse
import collections
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import build_wiki

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "fandom_ja"
OUT = ROOT / "fandom-ja"
API = "https://warframe.fandom.com/ja/api.php"
WIKI = "https://warframe.fandom.com/ja/wiki/"
UA = "WarframeDocument/1.0 (personal study notes)"
HEADER = "<!-- scripts/build_fandom_ja.py で自動生成。手で編集しない。 -->\n"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/3.0/deed.ja"
LICENSE = (f"出典: [Warframe日本語 Wiki]({WIKI})（Fandom）。ライセンスは [CC BY-SA 3.0]({LICENSE_URL})。"
           "執筆者は各ページの「履歴」を参照。スクリプトで Markdown に変換し、攻略向けの節を省いている。")

# ストーリー関連として本文を取り込むカテゴリ
STORY_CATEGORIES = {"クエスト", "キャラクター", "Characters", "ストーリー", "勢力", "ファクション", "シンジケート",
                    "センティエント", "オロキン", "エントラティ", "レッド・ベール",
                    "スティール・メリディアン", "セファロン", "ルア", "Nightwave Series"}
# この見出しがあるページは、導入部とその節だけを取り込む
# 「略歴」は日本語 Wiki では更新履歴の意味で使われているので含めない
LORE_SECTIONS = re.compile(r"^(伝承|ロア|Lore|歴史|背景|ストーリー|あらすじ)$")
# ストーリー関連ページでも取り込まない節
SKIP_SECTIONS = {"更新履歴", "Patch History", "メディア", "Media", "画像", "Gallery", "ギャラリー", "動画", "See Also",
                 "See also", "関連項目", "関連記事", "参考", "参照", "References", "注釈", "取得", "入手", "入手方法",
                 "性能", "Stats", "装備", "ヒント", "Tips", "バグ", "Bugs", "不具合", "確認されている不具合", "報酬",
                 "ミッション完了報酬", "External Links", "リンク"}


# ---------------------------------------------------------------- 取得

def api(params: dict) -> dict:
    params = {**params, "format": "json", "formatversion": 2}
    req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}", headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            time.sleep(0.3)
            if "error" in data:
                raise RuntimeError(data["error"].get("info"))
            return data
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                raise
            print(f"  再試行: {e}", file=sys.stderr)
            time.sleep(3)
    raise AssertionError


def query(params: dict):
    """action=query を continue が尽きるまで回す。"""
    cont: dict = {}
    while True:
        data = api({"action": "query", **params, **cont})
        yield data.get("query", {})
        if "continue" not in data:
            return
        cont = data["continue"]


def fetch_index() -> dict:
    """全記事のウィキテキスト・カテゴリ・英語版へのリンクと、転送ページの対応。"""
    pages: dict[int, dict] = {}
    print("記事を取得中...")
    for q in query({"generator": "allpages", "gapnamespace": 0, "gapfilterredir": "nonredirects", "gaplimit": 50,
                    "prop": "revisions|categories|langlinks", "rvprop": "ids|timestamp|content", "rvslots": "main",
                    "cllimit": "max", "clshow": "!hidden", "lllang": "en", "lllimit": "max"}):
        for p in q.get("pages", []):
            page = pages.setdefault(p["pageid"], {"title": p["title"], "categories": [], "en": []})
            page["categories"] += [c["title"].split(":", 1)[1] for c in p.get("categories", [])]
            page["en"] += [l["title"] for l in p.get("langlinks", [])]
            if p.get("revisions"):
                rev = p["revisions"][0]
                page.update(revid=rev["revid"], timestamp=rev["timestamp"], text=rev["slots"]["main"]["content"])
    print(f"  {len(pages)} 件。転送ページを取得中...")
    titles = [p["title"] for q in query({"list": "allpages", "apnamespace": 0, "apfilterredir": "redirects",
                                        "aplimit": "max"}) for p in q.get("allpages", [])]
    redirects: dict[str, str] = {}
    for i in range(0, len(titles), 50):
        q = api({"action": "query", "titles": "|".join(titles[i:i + 50]), "redirects": 1})["query"]
        redirects.update({r["from"]: r["to"] for r in q.get("redirects", [])})
    print(f"  転送 {len(redirects)} 件")
    site = api({"action": "query", "meta": "siteinfo", "siprop": "rightsinfo"})["query"]["rightsinfo"]
    return {"rights": site, "pages": {str(k): v for k, v in sorted(pages.items())}, "redirects": redirects}


def load(refresh: bool = False) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "index.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    data = fetch_index()
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def parse_html(pageid: str, revid: int) -> str:
    path = CACHE / "html" / f"{pageid}.json"
    if path.exists():
        cached = json.loads(path.read_text(encoding="utf-8"))
        if cached["revid"] == revid:
            return cached["html"]
    data = api({"action": "parse", "pageid": pageid, "prop": "text", "disablelimitreport": 1})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"revid": revid, "html": data["parse"]["text"]}, ensure_ascii=False), encoding="utf-8")
    return data["parse"]["text"]


# ---------------------------------------------------------------- 用語

def is_en(s: str) -> bool:
    return bool(re.search(r"[A-Za-z]", s)) and s.isascii()


def unlink(s: str) -> str:
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"<[^>]+>|'''?|\{\{[^}]*\}\}", "", s)
    return re.sub(r"\s+", " ", s).strip(" 　:：、,")


def nows(s: str) -> str:
    return re.sub(r"\s", "", s)


def lead_pairs(text: str) -> list[tuple[str, str]]:
    """冒頭の「'''日本語'''（English）」「'''English（日本語）'''」やクエストの「英語名称」から (英語, 日本語)。"""
    head = re.sub(r"<!--.*?-->", "", text, flags=re.S)[:5000]
    pairs = []
    m = re.search(r"英語名称\s*=\s*([^\n|}]+)", head)
    if m:
        pairs.append((unlink(m.group(1)), ""))
    for pat in (r"'''\s*([^'\n]+?)\s*'''\s*[（(]\s*([^）)\n]+?)\s*[）)]",
                r"'''\s*([^'\n（(]+?)\s*[（(]\s*([^）)\n]+?)\s*[）)]\s*'''"):
        for m in re.finditer(pat, head):
            a, b = unlink(m.group(1)), unlink(m.group(2))
            if re.search(r"[:：、。]", a + b):
                break
            if is_en(b) and a and not a.isascii():
                pairs.append((b, a))
            elif is_en(a) and b and not b.isascii():
                pairs.append((a, b))
            break  # 最初の太字だけ（冒頭の定義文）
    return pairs


def page_url(title: str) -> str:
    return WIKI + urllib.parse.quote(title.replace(" ", "_"), safe="_()/:-.,'")


def is_story(page: dict) -> bool:
    return bool(set(page["categories"]) & STORY_CATEGORIES)


def has_lore(page: dict) -> bool:
    return any(LORE_SECTIONS.match(h.strip()) for h in re.findall(r"^==\s*([^=].*?)\s*==\s*$", page.get("text", ""), re.M))


def build_terms(data: dict) -> list[dict]:
    redirects_to: dict[str, list[str]] = collections.defaultdict(list)
    for src, dst in data["redirects"].items():
        redirects_to[dst].append(src)
    # 英語名の手がかりがないクエストは、公式のクエスト名（sources/quests.md）の日本語名から英語名を引く
    quest_en = {nows(ja): en for en, ja in re.findall(r"^- (.+?)（(.+?)）$",
                                                      (ROOT / "sources" / "quests.md").read_text(encoding="utf-8"), re.M)}
    terms = []
    for pid, p in data["pages"].items():
        title = p["title"]
        if "/" in title:
            continue
        base = re.sub(r"\s*[（(][^）)]*[）)]$", "", title).strip()
        en, ja = [], []
        for e, j in lead_pairs(p.get("text", "")):
            en.append(e)
            if j:
                ja.append(j)
        en += p["en"]
        if nows(base) in quest_en:
            en.append(quest_en[nows(base)])
        (en if is_en(base) else ja).append(base)
        for r in sorted(redirects_to.get(title, [])):
            (en if is_en(r) else ja).append(r)
        en = list(dict.fromkeys(e for e in en if e))
        # 英字の記事名しかない記事（Warframe 名・人名など）は、日本語 Wiki でも英字で表記している
        ja = list(dict.fromkeys(ja)) or [base]
        if not en and not is_story(p):
            continue
        terms.append({"ja": ja, "en": en, "page": title, "url": page_url(title), "story": is_story(p) or has_lore(p),
                      "categories": sorted(set(p["categories"])), "updated": p.get("timestamp", "")[:10]})
    return sorted(terms, key=lambda t: (not t["story"], (t["en"] or t["ja"])[0].lower()))


class Index:
    """日本語 Wiki の表記を引く（scripts/terms.py から使う）。"""

    def __init__(self, refresh: bool = False) -> None:
        self.data = load(refresh)
        self.terms = build_terms(self.data)
        self.by_en: dict[str, list[dict]] = collections.defaultdict(list)
        for t in self.terms:
            for e in t["en"]:
                self.by_en[e.lower()].append(t)
        self.texts = [(p["title"], p.get("text", "")) for p in self.data["pages"].values()]

    def names(self, en: str) -> list[dict]:
        """英語名がその語の記事（記事名・転送・冒頭の定義から）。"""
        return self.by_en.get(en.lower(), [])

    def pages_with(self, ja: str) -> list[str]:
        """本文に ja を含む記事名。"""
        ja = nows(ja)
        return [title for title, text in self.texts if ja in nows(text)]


# ---------------------------------------------------------------- 本文

def slug(text: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", text.lower()).strip("-")


def talk_speakers(page_html: str) -> str:
    """{{Talk}} の話者はアイコン画像でしか示されないので、画像名を「話者: 」として台詞の前に入れる。"""
    def speaker(icon: str) -> str:
        m = re.search(r'alt="([^"]+)"', icon) or re.search(r'title="(?:ファイル:)?([^"]+?)(?:\.\w{3,4})?"', icon)
        return html.unescape(m.group(1)).strip() if m else ""

    def repl(m: re.Match) -> str:
        name = speaker(m.group(1))
        return f'<div class="talk">{m.group(2) or ""}<b>{html.escape(name)}</b>: ' if name else m.group(0)

    return re.sub(r'<div class="(?:left|right)-icon">(.*?)</div>\s*<div class="talk-(?:left|right)">\s*(<p>)?',
                  repl, page_html, flags=re.S)


def page_body(page: dict, page_html: str) -> list[str]:
    intro, sections = build_wiki.to_sections(talk_speakers(page_html))
    # build_wiki は英語の見出し（Media など）だけ落とすので、日本語の見出しの節はここで選ぶ
    lore_only = not is_story(page)
    keep = []
    for head, lines in sections:
        if head in SKIP_SECTIONS:
            continue
        if lore_only and not LORE_SECTIONS.match(head):
            continue
        keep.append((head, lines))
    out = build_wiki.render_lines(intro, base_level=3)
    for head, lines in keep:
        out += ["", f"## {head}", ""] + build_wiki.render_lines(lines, base_level=3)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="Wiki から取り直す")
    args = ap.parse_args()
    data = load(args.refresh)
    terms = build_terms(data)

    story = [(pid, p) for pid, p in data["pages"].items() if "/" not in p["title"] and (is_story(p) or has_lore(p))]
    print(f"ストーリー関連 {len(story)} ページを変換中...")
    names: dict[str, str] = {}
    term_by_page = {t["page"]: t for t in terms}
    for pid, p in sorted(story, key=lambda x: x[1]["title"]):
        t = term_by_page.get(p["title"])
        name = slug(t["en"][0]) if t and t["en"] else ""
        if not name or name in names.values():
            name = f"p{pid}"
        names[pid] = name

    if OUT.exists():
        for f in OUT.rglob("*.md"):
            f.unlink()
    (OUT / "pages").mkdir(parents=True, exist_ok=True)
    rows = collections.defaultdict(list)
    for pid, p in story:
        body = page_body(p, parse_html(pid, p["revid"]))
        t = term_by_page.get(p["title"])
        en = f"（{t['en'][0]}）" if t and t["en"] and t["en"][0] != p["title"] else ""
        lines = [HEADER, f"# {p['title']}{en}", "",
                 f"> 出典: [Warframe日本語 Wiki「{p['title']}」]({page_url(p['title'])})"
                 f"（[履歴]({page_url(p['title'])}?action=history)、最終更新 {p['timestamp'][:10]}）。"
                 f"ライセンス: [CC BY-SA 3.0]({LICENSE_URL})。Markdown に変換し、攻略向けの節を省いた。", "",
                 "> コミュニティが書いた記事で、ゲームの最新の内容や公式の日本語訳と違うことがある。", ""] + body
        write(OUT / "pages" / f"{names[pid]}.md", lines)
        group = next((c for c in ("クエスト", "キャラクター", "勢力") if c in p["categories"]), "その他")
        if group == "その他" and "Characters" in p["categories"]:
            group = "キャラクター"
        rows[group].append((p["title"], en, names[pid], p["timestamp"][:10]))

    readme = [HEADER, "# 日本語 Wiki（Fandom）から取り込んだ資料", "", LICENSE, "",
              "- 日本語での呼び方・慣用表記を確かめるための資料。考察の根拠はゲーム内テキスト（[sources](../sources/README.md)）を優先する。",
              "- 記事の多くは 2020〜2021 年の更新で止まっていて、機械翻訳のような文もある。各ページに最終更新日を載せている。",
              "- 更新は `python StoryAnalysis/scripts/build_fandom_ja.py --refresh`。", "",
              f"- [用語対応表（英語 ⇔ 日本語 Wiki の表記）](terms.md)（{len(terms)} 語）", ""]
    for group in ("クエスト", "キャラクター", "勢力", "その他"):
        if not rows[group]:
            continue
        readme += [f"## {group}", "", "| ページ | 最終更新 |", "| --- | --- |"]
        for title, en, name, updated in sorted(rows[group]):
            readme.append(f"| [{title}{en}](pages/{name}.md) | {updated} |")
        readme.append("")
    write(OUT / "README.md", readme)

    md = [HEADER, "# 用語対応表（日本語 Wiki の表記）", "", LICENSE, "",
          "日本語 Wiki の記事名・転送ページ・冒頭の定義文から機械的に取った、英語名と日本語 Wiki での表記の対応。"
          "公式の日本語訳は [用語対応表](../glossary.md) を見る（こちらはコミュニティでの呼び方の出典）。", ""]
    def same(t: dict) -> bool:
        return {nows(j).lower() for j in t["ja"]} <= {nows(e).lower() for e in t["en"]}

    for story_flag, head in ((True, "ストーリー関連"), (False, "その他")):
        md += [f"## {head}", ""]
        if not story_flag:
            md += ["英語名と同じ英字で書いている記事（武器・MOD 名など）は省いた（`terms.json` には含む）。", ""]
        md += ["| English | 日本語 Wiki の表記 | 記事 | 最終更新 |", "| --- | --- | --- | --- |"]
        for t in terms:
            if t["story"] != story_flag or not story_flag and same(t):
                continue
            cell = lambda xs: " / ".join(x.replace("|", "｜") for x in xs)
            md.append(f"| {cell(t['en']) or '—'} | {cell(t['ja'])} | [{t['page'].replace('|', '｜')}]({t['url']}) "
                      f"| {t['updated']} |")
        md.append("")
    write(OUT / "terms.md", md)
    meta = {"source": WIKI, "license": "CC BY-SA 3.0", "license_url": LICENSE_URL,
            "note": "Warframe日本語 Wiki（Fandom）の記事名・転送ページ・冒頭の定義文から機械的に抽出"}
    # 1 語 1 行にして差分を見やすくする
    head = json.dumps(meta, ensure_ascii=False, indent=1)[:-2]
    body = ",\n".join("  " + json.dumps(t, ensure_ascii=False) for t in terms)
    (OUT / "terms.json").write_text(f'{head},\n "terms": [\n{body}\n ]\n}}\n', encoding="utf-8", newline="\n")
    print(f"完了: 用語 {len(terms)} 語 / ページ {len(story)} 件 → {OUT.relative_to(ROOT)}")


def write(path: Path, lines: list[str]) -> None:
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
