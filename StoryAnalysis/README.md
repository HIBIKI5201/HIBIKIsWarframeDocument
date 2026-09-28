# StoryAnalysis（ストーリー考察）

Warframe のストーリー考察を Markdown で置く場所。
新しい考察は `_template.md` をコピーして、`_` で始まらない名前（例: `2026-09-new-war.md`）で保存する。

## 構成

- `sources/`: ゲーム内のストーリー関連テキスト（英語原文）。考察の根拠はここから引用する。詳細は [sources/README.md](sources/README.md)。
- `glossary.md`: 英語 ⇔ 日本語の用語対応表。
- `scripts/build_sources.py`: `sources/` の自動生成スクリプト。

## 資料の更新

アップデート後は次のコマンドで `sources/` を再生成する（Python 3 のみ、追加パッケージ不要）。

```sh
python StoryAnalysis/scripts/build_sources.py --refresh
```

ダウンロードしたデータは `StoryAnalysis/.cache/` に置かれる（Git 管理外）。
新しいクエストが増えたときは、スクリプト内の `QUEST_ORDER` と `STORY_NAMESPACES` に追記する。
