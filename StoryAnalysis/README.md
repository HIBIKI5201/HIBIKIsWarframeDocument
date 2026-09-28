# StoryAnalysis（ストーリー考察）

Warframe のストーリー考察を Markdown で置く場所。
新しい考察は `_template.md` をコピーして、`_` で始まらない名前（例: `2026-09-new-war.md`）で保存する。

## 閲覧（PC・スマホ）

`StoryAnalysis/serve.bat` をダブルクリックすると、HTML をビルドしてサーバーを起動し、ブラウザで http://localhost:8001/ を開く。
同じ Wi-Fi のスマホからは、起動時にウィンドウへ表示される `http://<PC の IP アドレス>:8001/` を開く
（初回に Windows ファイアウォールの許可を求められたら「プライベートネットワーク」を許可する）。
止めるときはウィンドウを閉じる（または Ctrl+C）。コマンドから起動する場合:

```sh
python StoryAnalysis/scripts/serve.py --open --lan
```

Markdown・テンプレートの変更を検知して自動で再ビルドする（ブラウザは手動リロード）。
ビルドだけなら `python StoryAnalysis/scripts/build_site.py`（出力は `StoryAnalysis/build/site/`、Git 管理外）。
各ページ上部の入力欄でページ内を絞り込め、「検索」ページでは全資料を横断検索できる。

## 構成

- `sources/`: ゲーム内のストーリー関連テキスト（英語原文）。考察の根拠はここから引用する。詳細は [sources/README.md](sources/README.md)。
- `glossary.md`: 英語 ⇔ 日本語の用語対応表。
- `scripts/build_sources.py`: `sources/` の自動生成スクリプト。
- `scripts/build_site.py` / `scripts/serve.py`: Markdown → HTML の変換とローカルサーバー。
- `site/`: HTML のテンプレートと CSS / JS。

## 資料の更新

アップデート後は次のコマンドで `sources/` を再生成する（Python 3 のみ、追加パッケージ不要）。

```sh
python StoryAnalysis/scripts/build_sources.py --refresh
```

ダウンロードしたデータは `StoryAnalysis/.cache/` に置かれる（Git 管理外）。
新しいクエストが増えたときは、スクリプト内の `QUEST_ORDER` と `STORY_NAMESPACES` に追記する。

キャラクター・クエストのページ（`characters.md`・`quests.md`・`wiki/`）は WARFRAME Wiki から自動生成している。
一覧の日本語の概要は `data/characters.json`・`data/quests.json` を編集し、次のコマンドで作り直す（`--refresh` で Wiki を取り直す）。

```sh
python StoryAnalysis/scripts/build_wiki.py
```

## 関連資料

考察の根拠に使える Wiki のリンク（クエスト一覧、台詞全文、断片など）は [sources.md](sources.md) にまとめている。
キャラクターの一覧は [characters.md](characters.md)、クエストの一覧は [quests.md](quests.md)。
過去に pixiv と X で書いた考察の整理は [hibiki-works.md](hibiki-works.md)、本文の保存先は [archive/pixiv/](archive/pixiv/)。
