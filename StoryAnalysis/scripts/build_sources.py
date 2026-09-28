"""ゲーム内のストーリー関連テキスト（英語原文）を StoryAnalysis/sources/ に Markdown で書き出す。

データ元は Warframe の Public Export を補完した warframe-public-export-plus
(https://github.com/calamity-inc/warframe-public-export-plus)。
ゲームクライアントに含まれる公式テキストなので、英語・日本語ともに公式表記になる。

使い方:
    python StoryAnalysis/scripts/build_sources.py            # GitHub から取得してキャッシュ
    python StoryAnalysis/scripts/build_sources.py --refresh  # キャッシュを捨てて再取得
"""

import argparse
import datetime
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
OUT = ROOT / "sources"
REPO = "calamity-inc/warframe-public-export-plus"
BRANCH = "senpai"
FILES = [
    "dict.en.json",
    "dict.ja.json",
    "ExportKeys.json",
    "ExportCodex.json",
    "ExportWarframes.json",
    "ExportSyndicates.json",
    "ExportEmailItems.json",
]

# クエスト（KeyChain）のおおよそのリリース順。データ側に日付がないので手で持つ。
# ここにないクエストは末尾に回る。
QUEST_ORDER = [
    "VorsPrizeQuestKeyChain",
    "InfestedIntroQuestKeyChain",
    "KubrowQuestKeyChain",
    "ArchwingQuestKeyChain",
    "SpyQuestKeyChain",
    "MirageQuestKeyChain",
    "DragonQuestKeyChain",
    "LimboQuestKeyChain",
    "InfestedAladVQuestKeyChain",
    "GolemQuestKeyChainItem",
    "SentientQuestKeyChain",
    "OrokinMoonQuestKeyChain",
    "MummyQuestKeyChain",
    "GetClemQuestKeyChain",
    "FairyQuestKeyChain",
    "WarWithinQuestKeyChain",
    "IndexQuestKeyChain",
    "BardQuestKeyChain",
    "PriestQuestKeyChain",
    "ModQuestKeyChain",
    "GlassQuestKeyChain",
    "ApostasyKeyChain",
    "SacrificeQuestKeyChain",
    "ChimeraKeyChain",
    "RevenantQuestKeyChain",
    "SolarisQuestKeyChain",
    "ProteaQuestKeyChain",
    "RailjackBuildQuestKeyChain",
    "InfestedMicroplanetQuestKeyChain",
    "WraithQuestKeyChain",
    "YareliQuestKeyChain",
    "NewWarIntroKeyChain",
    "NewWarQuestKeyChain",
    "ZarimanQuestKeyChain",
    "KahlQuestKeyChain",
    "DuviriQuestKeyChain",
    "EntratiQuestKeyChain",
    "JadeShadowQuestKeyChain",
    "1999PrologueQuestKeyChain",
    "1999QuestKeyChain",
    "1999QuestGoodEndKeyChain",
    "JadeShadowsPart2QuestKeyChain",
    "TauPrequelQuestKeyChain",
]

# story-strings.md にまとめて書き出す dict の名前空間（/Lotus/Language/<ns>/...）。
STORY_NAMESPACES = [
    "NewPlayerQuest", "G1Quests", "Quests", "Codex", "Subtitles", "Archive", "Messages", "Inbox",
    "BardQuest", "GlassQuest", "ModQuest", "Apostasy", "Sacrifice", "Chimera", "RevenantQuest",
    "SolarisQuest", "DeadlockProtocol", "InfestedMicroplanetQuest", "WraithQuest", "YareliQuest",
    "NewWarIntro", "NewWar", "Narmer", "ZarimanQuest", "KahlQuest", "Veilbreaker", "Duviri",
    "Entrati", "EntratiLab", "DanteUnbound", "JadeShadows", "JadeShadowsPart2Mission",
    "JadeShadowsPart2Constellations", "LotusEaters", "1999Quest", "1999", "1999Echoes",
    "1999Texting", "1999Coda", "Isleweaver", "TauPrequel", "OldPeace", "LastWish",
    "CitrinesLastWish", "FiveFates", "Episodes", "Bosses", "Npcs",
]

HEADER = (
    "<!-- このファイルは scripts/build_sources.py で自動生成。手で編集しない。 -->\n"
    f"<!-- 出典: https://github.com/{REPO} ({BRANCH}) -->\n\n"
)


def fetch(refresh):
    CACHE.mkdir(exist_ok=True)
    for name in FILES:
        path = CACHE / name
        if path.exists() and not refresh:
            continue
        url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{name}"
        print("download", url)
        with urllib.request.urlopen(url) as r:
            path.write_bytes(r.read())
    return {name: json.loads((CACHE / name).read_text(encoding="utf-8")) for name in FILES}


def quote(text):
    text = text.replace("\r\n", "\n").strip()
    return "\n".join("> " + line if line else ">" for line in text.split("\n"))


def short(path):
    return path.rsplit("/", 1)[-1]


class Lang:
    def __init__(self, en, ja):
        self.en, self.ja = en, ja

    def e(self, key):
        return self.en.get(key, "") if key else ""

    def j(self, key):
        return self.ja.get(key, "") if key else ""

    def both(self, key):
        e, j = self.e(key), self.j(key)
        return f"{e}（{j}）" if j and j != e else e


def message_block(L, msg):
    lines = [
        f"- 差出人: {L.both(msg.get('sender')) or short(msg.get('sender', ''))}",
        f"- 件名: {L.e(msg.get('title'))}",
        "",
        quote(L.e(msg.get("body"))),
    ]
    return "\n".join(lines)


def build_quests(data, L):
    keys = data["ExportKeys.json"]
    chains = {short(p): (p, v) for p, v in keys.items() if "chainStages" in v}
    order = [c for c in QUEST_ORDER if c in chains] + sorted(c for c in chains if c not in QUEST_ORDER)

    out = [HEADER, "# Quests（クエスト）\n",
           "ゲーム内クエストの名称・説明・各ステージ・クエスト進行で届くメッセージの英語原文。",
           "並びはおおよそのリリース順（`QUEST_ORDER`）。セリフ（字幕）の多くはゲームデータに含まれないため、",
           "カットシーンの台詞は別途 Wiki のトランスクリプト等で補うこと。\n"]
    out.append("## 目次\n")
    for c in order:
        _, v = chains[c]
        out.append(f"- {L.e(v['name'])}（{L.j(v['name'])}）")
    out.append("")

    for c in order:
        path, v = chains[c]
        out.append(f"## {L.e(v['name'])}\n")
        out.append(f"- 日本語名: {L.j(v['name'])}")
        out.append(f"- 内部名: `{path}`")
        if v.get("excludeFromCodex") or v.get("codexSecret"):
            out.append("- 備考: Codex 非表示 / シークレット扱い")
        out.append("")
        if v.get("description"):
            out.append(quote(L.e(v["description"])) + "\n")
        out.append("### Stages\n")
        for i, stage in enumerate(v["chainStages"], 1):
            sk = keys.get(stage.get("key", ""), {})
            name = L.e(sk.get("name")) or short(stage.get("key", "")) or "（ミッションなし：受信箱・製作などのステップ）"
            ja = L.j(sk.get("name"))
            out.append(f"{i}. **{name}**" + (f"（{ja}）" if ja and ja != name else ""))
            if sk.get("description"):
                out.append("   - " + L.e(sk["description"]).replace("\n", " "))
        out.append("")
        msgs = [(i, s["messageToSendWhenTriggered"]) for i, s in enumerate(v["chainStages"], 1)
                if s.get("messageToSendWhenTriggered")]
        if msgs:
            out.append("### Messages\n")
            for i, m in msgs:
                out.append(f"#### Stage {i} 完了時\n")
                out.append(message_block(L, m) + "\n")
    return "\n".join(out)


def build_fragments(data, L):
    codex = data["ExportCodex.json"]
    out = [HEADER, "# Codex / Fragments（断片・Codex エントリ）\n",
           "Codex の Fragments（スキャンして集める断片）と、クエスト中にスキャンする Codex オブジェクトの英語原文。\n"]

    groups = {}
    for p, v in codex["loreFragments"].items():
        m = re.match(r"/Lotus/Language/Fragments/([A-Za-z]+?)\d*(Desc)?$", v.get("name", ""))
        group = p.split("/")[-2] if p.split("/")[-2] != "Fragments" else (m.group(1) if m else "Other")
        groups.setdefault(group, []).append((p, v))

    out.append("## Lore Fragments\n")
    for group in sorted(groups):
        out.append(f"### {group}\n")
        for p, v in groups[group]:
            out.append(f"#### {L.e(v.get('name')) or short(p)}\n")
            out.append(f"- 日本語名: {L.j(v.get('name'))}")
            out.append(f"- 内部名: `{p}`\n")
            if v.get("description"):
                out.append(quote(L.e(v["description"])) + "\n")
            st = v.get("secretTransmission")
            if st and L.e(st.get("text")):
                out.append("Secret transmission:\n")
                out.append(quote(L.e(st["text"])) + "\n")

    out.append("## Codex Objects\n")
    for p, v in codex["objects"].items():
        desc = L.e(v.get("description"))
        if not desc:
            continue
        out.append(f"### {L.e(v.get('name')) or short(p)}\n")
        out.append(f"- 日本語名: {L.j(v.get('name'))}")
        out.append(f"- 内部名: `{p}`\n")
        out.append(quote(desc) + "\n")
    return "\n".join(out)


def build_warframes(data, L):
    wf = data["ExportWarframes.json"]
    rows = []
    for p, v in wf.items():
        if v.get("productCategory") not in ("Suits", "SpaceSuits", "MechSuits"):
            continue
        name = L.e(v.get("name"))
        if not name or name.endswith(" Prime"):
            continue
        rows.append((v.get("introducedAt") or 0, name, L.j(v.get("name")), L.e(v.get("description")), v.get("productCategory")))
    rows.sort()
    out = [HEADER, "# Warframes（Warframe の説明文）\n",
           "Codex / アーセナルに表示される Warframe・アークウイング・ネクロメカの説明文の英語原文。",
           "並びはゲームデータ上の登場日時（`introducedAt`）順。Prime 版は省略。\n"]
    for ts, name, ja, desc, cat in rows:
        date = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d") if ts else "不明"
        out.append(f"## {name}\n")
        out.append(f"- 日本語名: {ja}")
        out.append(f"- 種別: {cat}")
        out.append(f"- 登場: {date}\n")
        if desc:
            out.append(quote(desc) + "\n")
    return "\n".join(out)


def build_syndicates(data, L):
    syn = data["ExportSyndicates.json"]
    out = [HEADER, "# Syndicates（シンジケート・勢力）\n",
           "シンジケート（勢力）の名称と説明の英語原文。\n"]
    for p, v in sorted(syn.items(), key=lambda kv: L.e(kv[1].get("name"))):
        name = L.e(v.get("name"))
        if not name:
            continue
        out.append(f"## {name}\n")
        out.append(f"- 日本語名: {L.j(v.get('name'))}")
        out.append(f"- 内部名: `{v.get('uniqueName', p)}`\n")
        if L.e(v.get("description")):
            out.append(quote(L.e(v["description"])) + "\n")
    return "\n".join(out)


def build_inbox(data, L):
    items = data["ExportEmailItems.json"]
    out = [HEADER, "# Inbox（受信箱メッセージ）\n",
           "クエスト以外の契機で届く受信箱メッセージの英語原文。クエスト進行で届くものは quests.md を参照。\n"]
    for p, v in sorted(items.items()):
        msg = v.get("message")
        if not msg or not L.e(msg.get("body")):
            continue
        out.append(f"## {L.e(msg.get('title')) or short(p)}\n")
        out.append(f"- 内部名: `{p}`")
        out.append(message_block(L, msg) + "\n")
    return "\n".join(out)


def build_strings(data, L):
    out = [HEADER, "# Story Strings（ストーリー関連テキスト一覧）\n",
           "ストーリー関連の名前空間に属するゲーム内テキストを、キーごとにそのまま並べたもの（英語原文）。",
           "他のファイルに整形済みのものも重複して含む。全文検索用。\n"]
    by_ns = {}
    for k, v in L.en.items():
        parts = k.split("/")
        if len(parts) > 4 and parts[3] in STORY_NAMESPACES and v.strip():
            by_ns.setdefault(parts[3], []).append((k, v))
    for ns in STORY_NAMESPACES:
        if ns not in by_ns:
            continue
        out.append(f"## {ns}\n")
        for k, v in sorted(by_ns[ns]):
            key = k.split("/", 4)[-1]
            if "\n" in v.strip() or len(v) > 120:
                out.append(f"- `{key}`\n")
                out.append("\n".join("  " + line for line in quote(v).split("\n")) + "\n")
            else:
                out.append(f"- `{key}`: {v}")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    data = fetch(args.refresh)
    L = Lang(data["dict.en.json"], data["dict.ja.json"])
    OUT.mkdir(exist_ok=True)
    builders = {
        "quests.md": build_quests,
        "fragments.md": build_fragments,
        "warframes.md": build_warframes,
        "syndicates.md": build_syndicates,
        "inbox.md": build_inbox,
        "story-strings.md": build_strings,
    }
    for name, fn in builders.items():
        (OUT / name).write_text(fn(data, L).rstrip() + "\n", encoding="utf-8")
        print("write", OUT / name)


if __name__ == "__main__":
    main()
