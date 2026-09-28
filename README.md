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
