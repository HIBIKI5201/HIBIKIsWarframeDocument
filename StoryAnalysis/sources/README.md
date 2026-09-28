# sources（英語原文資料）

ゲームクライアントに含まれるストーリー関連テキストを、英語原文のまま Markdown にまとめたもの。
`scripts/build_sources.py` で自動生成しているので、ここのファイルは手で編集しない。

## 出典

- [calamity-inc/warframe-public-export-plus](https://github.com/calamity-inc/warframe-public-export-plus)
  - DE 公式の Public Export をゲームデータで補完したもの。`dict.en.json` / `dict.ja.json` はゲームのローカライズそのもの。
  - 取得時点: 2026-09-27 のコミット（`8fdc970`）

## ファイル

| ファイル | 内容 |
| --- | --- |
| [quests.md](quests.md) | 全クエスト（43 件）の名称（英/日）・説明・ステージ・進行中に届く受信箱メッセージ |
| [fragments.md](fragments.md) | Codex の Lore Fragments（断片の本文・シークレット通信）と、クエスト中にスキャンする Codex オブジェクト |
| [warframes.md](warframes.md) | Warframe / アークウイング / ネクロメカの説明文（登場日順） |
| [syndicates.md](syndicates.md) | シンジケート（勢力）の説明 |
| [inbox.md](inbox.md) | クエスト以外で届く受信箱メッセージ |
| [story-strings.md](story-strings.md) | ストーリー関連の名前空間のテキストをキーごとに全部並べたもの（Ordis の記憶、Codex の長文ロア、1999 の会話、Isleweaver など。全文検索用） |

## 含まれないもの（今後の課題）

- **カットシーン・ミッション中の台詞**: 大半は音声ファイル側の字幕で、ゲームデータのテキスト辞書に入っていない。
  Warframe Wiki（<https://wiki.warframe.com/>）の各クエストの Transcript ページで補う。
  ※この資料を作った環境からは Wiki にアクセスできなかったため未収録。
- **Leverian（Albrecht の記録）や Warframe Profiles の本文**、**KIM（1999 のチャット）の会話全文**: 一部は `story-strings.md` にあるが網羅していない。
- **公式サイトの Dev Stream / 設定資料**: 対象外。

## メインストーリーの流れ（おおよそのリリース順）

1. Vor's Prize → Once Awake → The Archwing
2. Natah → The Second Dream → The War Within
3. Chains of Harrow → Apostasy Prologue → The Sacrifice → Chimera Prologue
4. Erra → The New War
5. Angels of the Zariman → Veilbreaker → The Duviri Paradox
6. Whispers in the Walls → Jade Shadows → The Lotus Eaters → The Hex
7. Jade Shadows: Constellations → The Old Peace

※ 6 以降の前後関係と、7 の位置づけは未検証。ゲーム内の推奨順は Wiki の Quest ページを参照。
