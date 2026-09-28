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
どちらも URL で指定できるので、リンクやブックマークに使える。

| URL | 内容 |
| --- | --- |
| `characters.html?q=Grineer` | キャラクター一覧を、表の行単位で絞り込む（`quests.html` やほかのページも同じ） |
| `search.html?q=Margulis` | 全文検索。名前が一致するキャラクター・クエストはページへの近道を上に出す |
| `search.html?q=Margulis&type=クエスト` | 種類（キャラ・クエスト・用語・セリフ・資料・日本語Wiki・考察）で絞り込む。セリフの索引は大きいので、検索ページを開いたあとで読み込む |

キャラクター・クエストは 1 件 1 ページ（`wiki/characters/<名前>.html`・`wiki/quests/<名前>.html`）で、
各ページから前後の項目・グループ・登場クエスト（キャラクター）・Wiki の記事・日本語 Wiki・全文検索へ移れる。
用語対応表の English 列からも各ページへ飛べる。

## 構成

- `sources/`: ゲーム内のストーリー関連テキスト（英語原文）。考察の根拠はここから引用する。詳細は [sources/README.md](sources/README.md)。
- `glossary.md`: 英語 ⇔ 日本語の用語対応表。`data/terms.json` の用語から `scripts/terms.py` で自動生成する（日本語はゲームの公式訳）。
- `quotes/`: WARFRAME Wiki の Quotes カテゴリ（キャラクター・場所・ミッションのセリフ集と、クエストの台詞全文）を全ページ取り込んだもの。英語原文。独り言・待機中・雑談だけを集めた `quotes/idle.md` もある。
- `fandom-ja/`: 日本語版 Wiki（Fandom）から取り込んだ用語対応表とストーリー関連ページ（CC BY-SA 3.0）。日本語での慣用表記の出典に使う。
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
データとページは分けていて、次の 2 段階で作る。

| 段階 | スクリプト | 入力 | 出力 |
| --- | --- | --- | --- |
| 取得・抽出 | `build_wiki.py` | Wiki、`data/characters.json`・`data/quests.json`（一覧・日本語の概要）、`data/ja/`（日本語訳） | `wiki/data/characters/<key>.json`・`wiki/data/quests/<key>.json`（基本情報・登場関係・本文） |
| ページ生成 | `render_wiki.py` | `wiki/data/`、`fandom-ja/terms.json` | `characters.md`・`quests.md`・`wiki/characters/*.md`・`wiki/quests/*.md` |

概要や訳を直したら `build_wiki.py` を実行する（最後に `render_wiki.py` も実行される。`--refresh` で Wiki を取り直す）。
ページの見た目だけを変えるときは `render_wiki.py` だけでよい（ネットワークに出ない）。

```sh
python StoryAnalysis/scripts/build_wiki.py
python StoryAnalysis/scripts/render_wiki.py
```

登場クエスト・登場キャラクターは、クエストの台詞全文（Transcript）で話者として出てくる回数と、本文中で名前が出る回数から数えている。

日本語版 Wiki（[Warframe日本語 Wiki](https://warframe.fandom.com/ja/wiki/)、Fandom）の用語とストーリー関連ページは、次のコマンドで `fandom-ja/` に取り込む（`--refresh` で Wiki を取り直す）。

```sh
python StoryAnalysis/scripts/build_fandom_ja.py --refresh
```

- `fandom-ja/terms.md`・`terms.json`: 英語名と日本語 Wiki での表記の対応。英語名は英語版への言語間リンク・英字の転送ページ・冒頭の太字の定義文（例: オロキン（Orokin））・クエストの英語名称から機械的に取る
- `fandom-ja/pages/`: クエスト・キャラクター・勢力などのカテゴリの記事と、「伝承」などの節がある記事の本文（攻略向けの節は省く）
- 各ページに出典（記事と履歴へのリンク）・最終更新日・ライセンス（CC BY-SA 3.0）を載せる。日本語 Wiki の記事の多くは 2020〜2021 年で更新が止まっているので、内容の根拠はゲーム内テキストを優先する

セリフ集（`quotes/`）は次のコマンドで取り込む（`--refresh` で Wiki を取り直す）。

```sh
python StoryAnalysis/scripts/build_quotes.py
```

- `quotes/data/<key>.json`: 1 ページずつのデータ。見出しの階層ごとのセリフと音声ファイル名（Wiki の File ページへリンクする）
- `quotes/<key>.md`: 1 ページずつのセリフ集。`quotes/idle.md`: 見出しが Idle・Ambient・Chatter・Citizens などの節と、Cetus・Fortuna・Duviri の住民・オービターのラジオのページを集めたもの
- キャラクター・クエストのページには、対応するセリフ集・台詞全文へのリンクが付く（最後に `render_wiki.py` を実行して付け直す）
- 公式の日本語字幕は公開されているゲームデータに含まれないので、英語原文だけ

## 用語と翻訳の確認

用語対応表の日本語は、ゲームの日本語ローカライズから自動で引いている（手で訳さない）。
ゲーム内で確認できない語は、日本語版 Wiki の記事名・定義文・本文にある表記で確認し、根拠を `日本語Wiki` として出典の記事をメモ列に載せる（慣用表記）。
用語を足すときは `data/terms.json` に英語（と、単独の公式訳がない語だけ候補の日本語）を書いて、次を実行する。

```sh
python StoryAnalysis/scripts/terms.py
```

`glossary.md` を作り直したあと、手書きの日本語（`data/ja/`、`data/*.json` の概要、考察ファイル）を公式表記と照らして、次の点を表示する。

- `data/quests.json` のクエスト名が公式のクエスト名と違う
- 公式訳がある用語（例: Orokin → オロキン）を英字のまま書いている（括弧内の原語・リンク・コードは除く）

`--strict` を付けると、指摘があれば終了コード 1 になる。

## 関連資料

考察の根拠に使える Wiki のリンク（クエスト一覧、台詞全文、断片など）は [sources.md](sources.md) にまとめている。
日本語版 Wiki から取り込んだ資料は [fandom-ja/](fandom-ja/README.md)。
キャラクターの一覧は [characters.md](characters.md)、クエストの一覧は [quests.md](quests.md)。
過去に pixiv と X で書いた考察の整理は [hibiki-works.md](hibiki-works.md)、本文の保存先は [archive/pixiv/](archive/pixiv/)。
