"""用語対応表 (glossary.md) を公式の日本語ローカライズから生成し、手書きの日本語訳が公式表記に合っているか確認する。

    python StoryAnalysis/scripts/terms.py            # glossary.md を生成して確認結果を表示
    python StoryAnalysis/scripts/terms.py --strict   # 指摘が 1 件でもあれば終了コード 1

入力:
  data/terms.json   用語の一覧（英語・分類・メモ）。単独の公式訳がない語だけ、候補の日本語 "ja" を書く
  .cache/dict.*.json, .cache/ExportKeys.json   ゲームの英語・日本語テキスト（build_sources.py が取得）
出力:
  glossary.md       用語対応表（手で編集しない）

日本語の決め方:
  公式        英語がその語だけの文字列として辞書にあり、対応する日本語がある
  公式(文中)  候補の日本語が、その英語を含む文の日本語版に出てくる（件数つき）
  日本語Wiki  ゲーム内では確認できないが、日本語版 Wiki（Fandom）の記事名・転送・定義文にある、または本文で使われている
              （慣用表記。build_fandom_ja.py が取り込んだデータを使い、出典の記事をメモに載せる）
  未確認      どれでも確認できない（候補があれば表示する）

確認する対象（手書きの日本語）:
  data/quests.json の "ja"（クエスト名）      公式のクエスト名と一致するか
  data/ja/**/*.md、data/*.json の概要、考察   公式訳が英字と違う用語を、英字のまま書いていないか
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

import build_fandom_ja
import build_sources

ROOT = build_sources.ROOT
TERMS = ROOT / "data" / "terms.json"
OUT = ROOT / "glossary.md"
HEADER = "<!-- scripts/terms.py で自動生成。手で編集しない（用語は data/terms.json を編集する）。 -->\n"

# 考察として手で書いたファイル（自動生成のページは除く）
GENERATED = {"README.md", "glossary.md", "characters.md", "quests.md", "sources.md", "_template.md"}


def nows(s: str) -> str:
    return re.sub(r"\s", "", s)


class Official:
    """公式の英語・日本語テキストから訳語を引く。"""

    def __init__(self) -> None:
        data = build_sources.fetch(False)
        self.en: dict[str, str] = data["dict.en.json"]
        self.ja: dict[str, str] = data["dict.ja.json"]
        self.keys = data["ExportKeys.json"]
        self.by_en: dict[str, list[str]] = collections.defaultdict(list)
        for k, v in self.en.items():
            self.by_en[v.strip()].append(k)

    def standalone(self, term: str) -> list[str]:
        """英語がその語だけの文字列になっている箇所の日本語（多い順）。"""
        c = collections.Counter(self.ja[k].strip() for k in self.by_en.get(term, []) if self.ja.get(k, "").strip())
        seen, out = set(), []
        for ja, _ in c.most_common():
            if nows(ja) not in seen:
                seen.add(nows(ja))
                out.append(ja)
        return out

    def in_text(self, term: str, ja: str) -> int:
        """英語に term を含み、日本語に ja を含む文字列の数。"""
        pat = re.compile(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])")
        ja = nows(ja)  # 「執行官 Ballas」と「執行官Ballas」のような空白の違いは同じとみなす
        return sum(1 for k, v in self.en.items() if ja in nows(self.ja.get(k, "")) and pat.search(v))

    def quests(self) -> list[tuple[str, str]]:
        """(英語名, 日本語名) 。クエストチェーンだけ。"""
        out = []
        for v in self.keys.values():
            if "chainStages" in v and self.en.get(v.get("name", "")):
                out.append((self.en[v["name"]], self.ja.get(v["name"], "")))
        return sorted(out)


def link(title: str, url: str) -> str:
    return f"[{title}]({url})"


def resolve_wiki(wiki: build_fandom_ja.Index, en: str, candidates: list[str]) -> dict | None:
    """ゲーム内で確認できない語を、日本語 Wiki の表記で確認する。"""
    named = wiki.names(en)
    for c in candidates:
        for t in named:
            if nows(c) in {nows(j) for j in t["ja"]}:
                return {"ja": c, "basis": "日本語Wiki", "source": "記事 " + link(t["page"], t["url"]),
                        "variants": [x for x in candidates if x != c]}
    for c in candidates:
        pages = wiki.pages_with(c) if len(nows(c)) >= 2 else []
        if pages:
            refs = "、".join(link(t, build_fandom_ja.page_url(t)) for t in pages[:3])
            return {"ja": c, "basis": f"日本語Wiki(本文) {len(pages)} 件", "source": "本文 " + refs,
                    "variants": [x for x in candidates if x != c]}
    named_ja = [(j, t) for t in named for j in t["ja"] if nows(j).lower() != nows(en).lower()]
    if named_ja:
        j, t = named_ja[0]
        return {"ja": j, "basis": "日本語Wiki", "source": "記事 " + link(t["page"], t["url"]),
                "variants": [c + "（未確認）" for c in candidates]}
    return None


def resolve(off: Official, wiki: build_fandom_ja.Index, term: dict) -> dict:
    """1 語の日本語と根拠を決める。"""
    en = term["en"]
    found = off.standalone(en)
    if found:
        return {"ja": found[0], "basis": "公式", "variants": found[1:]}
    candidates = [c.strip() for c in term.get("ja", "").split(" / ") if c.strip()]
    hits = [(c, off.in_text(en, c)) for c in candidates]
    confirmed = [(c, n) for c, n in hits if n]
    if confirmed:
        return {"ja": " / ".join(c for c, _ in confirmed), "basis": f"公式(文中) {sum(n for _, n in confirmed)} 件",
                "variants": [c for c, n in hits if not n]}
    return resolve_wiki(wiki, en, candidates) or {"ja": " / ".join(candidates) or "—", "basis": "未確認", "variants": []}


def site_pages() -> dict[str, str]:
    """このサイトのキャラクター・クエストのページ（render_wiki.py が作る）。{英語名（小文字）: パス}"""
    out = {}
    for kind in ("characters", "quests"):
        for f in sorted((ROOT / "wiki" / "data" / kind).glob("*.json")):
            r = json.loads(f.read_text(encoding="utf-8"))
            for n in (r["name"], r["page"]):
                out.setdefault(n.lower(), f"wiki/{kind}/{r['key']}.md")
    return out


def build_glossary(off: Official, wiki: build_fandom_ja.Index, cats: list[dict]) -> tuple[str, dict[str, str]]:
    """glossary.md の本文と、確認に使う {英語: 公式の日本語} を返す。"""
    official: dict[str, str] = {}
    pages = site_pages()
    en_cell = lambda en: f"[{en}]({pages[en.lower()]})" if en.lower() in pages else en
    out = [HEADER, "# 用語対応表（英語 ⇔ 日本語）\n",
           "考察は英語原文（`sources/`）を根拠にするので、英語表記と日本語版の表記を対応させておく。",
           "日本語はゲームの日本語ローカライズ（`dict.ja.json`）から自動で引いている。用語を足すときは `data/terms.json` を編集して "
           "`python StoryAnalysis/scripts/terms.py` を実行する。\n",
           "- **根拠** 列の意味",
           "  - `公式`: 英語がその語だけで辞書にあり、対応する日本語訳がある",
           "  - `公式(文中) N 件`: 単独の訳語はないが、その英語を含む N 件の文の日本語版で使われている訳",
           "  - `日本語Wiki`: ゲーム内では確認できないが、[日本語版 Wiki](https://warframe.fandom.com/ja/wiki/)（Fandom）"
           "の記事名・定義文にある慣用表記（`日本語Wiki(本文) N 件` は N 件の記事の本文で使われている）。出典の記事はメモ列。"
           "取り込んだ資料は [fandom-ja/](fandom-ja/README.md)（CC BY-SA 3.0）",
           "  - `未確認`: どれでも確認できない（コミュニティでの呼び方など）",
           "- 日本語版では、キャラクター名や Warframe 名の多くを英字のまま表記している（例: `Ordis`, `Ballas`）。",
           "- English 列のリンクは、このサイトのキャラクター・クエストのページ。\n"]
    for cat in cats:
        out += [f"## {cat['category']}\n", "| English | 日本語 | 根拠 | メモ |", "| --- | --- | --- | --- |"]
        for term in cat["terms"]:
            r = resolve(off, wiki, term)
            note = term.get("note", "")
            if r["variants"]:
                note = "; ".join(filter(None, [note, "ほかの表記: " + "、".join(r["variants"])]))
            if r.get("source"):
                note = "; ".join(filter(None, [note, "出典: " + r["source"]]))
            out.append(f"| {en_cell(term['en'])} | {r['ja']} | {r['basis']} | {note} |")
            if r["basis"].startswith("公式"):
                official[term["en"]] = r["ja"].split(" / ")[0]
        out.append("")
    out += ["## クエスト\n", "ゲーム内のクエスト名（すべて公式訳）。\n", "| English | 日本語 |", "| --- | --- |"]
    for en, ja in off.quests():
        out.append(f"| {en_cell(en)} | {ja} |")
        official.setdefault(en, ja)
    return "\n".join(out) + "\n", official


# ---------------------------------------------------------------- 確認

def ja_texts() -> list[tuple[str, str]]:
    """確認対象の (場所, 日本語テキスト)。"""
    texts = []
    for p in sorted((ROOT / "data" / "ja").rglob("*.md")):
        texts.append((p.relative_to(ROOT).as_posix(), p.read_text(encoding="utf-8")))
    for name in ("characters.json", "quests.json"):
        path = ROOT / "data" / name
        if not path.exists():
            continue
        for group in json.loads(path.read_text(encoding="utf-8")):
            for item in group["items"]:
                for field in ("ja", "summary"):
                    if item.get(field):
                        texts.append((f"data/{name} {item.get('page')} .{field}", item[field]))
    for p in sorted(ROOT.glob("*.md")):
        if p.name not in GENERATED:
            texts.append((p.name, p.read_text(encoding="utf-8")))
    return texts


def strip_allowed(text: str) -> str:
    """英字のままでよい部分（リンク・コード・括弧内の原語・引用の出典など）を除く。"""
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[（(][^（）()]*[）)]", " ", text)
    return text


def check(off: Official, official: dict[str, str]) -> list[str]:
    problems = []
    quest_ja = dict(off.quests())
    path = ROOT / "data" / "quests.json"
    if path.exists():
        for group in json.loads(path.read_text(encoding="utf-8")):
            for item in group["items"]:
                name = re.sub(r"\s*\(Quest\)$", "", item.get("page", ""))
                want = quest_ja.get(name)
                if want and item.get("ja") and nows(item["ja"]) != nows(want):
                    problems.append(f"data/quests.json {name}: クエスト名「{item['ja']}」→ 公式は「{want}」")

    # 公式訳が英字と違う（カタカナなどに訳されている）用語だけを見る。長い語から順に当てる
    translated = {en: ja for en, ja in official.items() if ja and not re.fullmatch(r"[\x00-\x7f]+", ja) and len(en) > 2}
    patterns = [(en, ja, re.compile(rf"(?<![A-Za-z]){re.escape(en)}(?![A-Za-z'])"))
                for en, ja in sorted(translated.items(), key=lambda kv: -len(kv[0]))]
    for where, text in ja_texts():
        body = strip_allowed(text)
        counts = collections.Counter()
        for en, ja, pat in patterns:
            n = len(pat.findall(body))
            if n:
                counts[(en, ja)] = n
                body = pat.sub(" ", body)  # 長い語で当たった部分を短い語で二重に数えない
        for (en, ja), n in sorted(counts.items()):
            problems.append(f"{where}: 「{en}」が英字のまま {n} 箇所 → 公式訳は「{ja}」")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="指摘があれば終了コード 1")
    args = ap.parse_args()
    off = Official()
    wiki = build_fandom_ja.Index()
    cats = json.loads(TERMS.read_text(encoding="utf-8"))
    text, official = build_glossary(off, wiki, cats)
    OUT.write_text(text, encoding="utf-8")
    print(f"write {OUT.relative_to(ROOT)}")
    problems = check(off, official)
    for p in problems:
        print("  " + p)
    print(f"{len(problems)} 件の指摘")
    if args.strict and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
