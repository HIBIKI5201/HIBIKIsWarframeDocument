# Warframe Document

Warframe に関する個人ドキュメント。

| ディレクトリ | 内容 |
| --- | --- |
| [TODO/](TODO/README.md) | 欲しいものリスト。TOML → SQLite → HTML を自動生成し、`TODO/serve.bat` をダブルクリックすると http://localhost:8000/ で閲覧できる |
| [StoryAnalysis/](StoryAnalysis/README.md) | ストーリー考察（Markdown）。英語原文資料（`sources/`）と英日用語対応表（`glossary.md`）付き。`StoryAnalysis/serve.bat` で HTML 表示（スマホからも閲覧可） |

## スマホで見る（claude.ai アーティファクト）

TODO とストーリー資料を 1 つにまとめたページを claude.ai に非公開で載せている（ヘッダーの「TODO / ストーリー」で切り替え）。
https://claude.ai/artifact/M4pp71NGmLe6bvUcTkySPb

内容は載せた時点のもの。更新するときは `python scripts/build_artifact.py` で `build/artifact/` を作り、
Claude Code に「アーティファクトを更新して」と頼む（上の URL のまま差し替える）。

## 権利・ライセンス

このリポジトリは個人が作成した**非公式のファンプロジェクト**で、Digital Extremes Ltd. とは関係ありません。
Warframe および関連する名称・ロゴ・ゲーム内テキスト・画像などの権利は、Digital Extremes Ltd. に帰属します。

内容ごとの扱いは次のとおりです。

| 内容 | 場所 | 権利・ライセンス |
| --- | --- | --- |
| ゲーム内テキスト（英語原文・公式の日本語訳） | `StoryAnalysis/sources/`、`StoryAnalysis/glossary.md` の公式訳 | © Digital Extremes Ltd. ストーリー考察のための引用・資料として掲載しています。[warframe-public-export-plus](https://github.com/calamity-inc/warframe-public-export-plus) 経由でゲームデータから抽出しました |
| WARFRAME Wiki を元にした記事 | `StoryAnalysis/wiki/`、`StoryAnalysis/characters.md`、`StoryAnalysis/quests.md` | [WARFRAME Wiki](https://wiki.warframe.com/) の記事を元に作成しています。Wiki のライセンス（CC BY-SA）に従い、これらのファイルも同じライセンスで提供します。出典は各項目のリンク先です |
| 作者の考察・過去作品 | `StoryAnalysis/archive/`、`StoryAnalysis/hibiki-works.md`、その他の考察ファイル | © 郷音ヒビキ（[@HIBIKI_5201](https://x.com/HIBIKI_5201)）。無断転載・再配布はご遠慮ください。引用する場合は出典を明記してください |
| 上記以外（スクリプト・HTML テンプレート・TODO データなど） | `scripts/`、`*/scripts/`、`*/site/`、`TODO/` など | © 郷音ヒビキ。ライセンスは設定していません（すべての権利を留保します） |

権利者の方から掲載内容について削除や修正の依頼があれば、対応します。[Issues](https://github.com/HIBIKI5201/WarframeDocument/issues) からご連絡ください。

上の「スマホで見る」のアーティファクトは作者専用の非公開ページで、ほかの人は開けません。
