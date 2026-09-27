# TODO（欲しいものリスト）

Notion の「欲しいものデータベース」から移行した TODO リスト。
`data/*.toml` を正本とし、SQLite 経由で静的 HTML を生成してローカルで閲覧する。Python 3.11 以上の標準ライブラリだけで動く。

## 閲覧

`TODO/serve.bat` をダブルクリックすると、ビルドしてサーバーを起動し、ブラウザで http://localhost:8000/ を開く。
止めるときはウィンドウを閉じる（または Ctrl+C）。コマンドから起動する場合:

```bash
python TODO/scripts/serve.py --open
```

起動時にビルドし、`data/`・`site/`・`db/` の変更を検知して自動で再ビルドする（ブラウザは手動リロード）。
ビルドだけなら `python TODO/scripts/build.py`（出力は `TODO/build/`、git 管理外）。

## ディレクトリ構成

```
TODO/
  serve.bat           ダブルクリックで起動
  data/NN-<id>.toml   ← 編集するのはここ。カテゴリ 1 つ = 1 ファイル、NN は表示順
  db/schema.sql       SQLite スキーマ（カテゴリ別進捗ビュー category_progress など）
  scripts/
    build.py          data → build/todo.db → build/site/*.html
    serve.py          ローカルサーバー + 自動再ビルド
  site/
    templates/        HTML テンプレート (string.Template)
    static/           CSS / JS
  build/              生成物（git 管理外）
```

## 項目の編集

`data/*.toml` に `[[items]]` を追加・編集する。手に入れたら `done = true` にすると、打ち消し線付きで末尾に回り進捗に反映される。

```toml
[[items]]
name = "アルケイン ホットショット"   # 必須。カテゴリ内で一意
source = "次元アルキメデア"          # 入手場所
condition = "..."                   # 入手条件
required = 12                       # 必要数
url = "https://wiki.warframe.com/…" # 参考リンク
note = "..."                        # メモ
updated = 2026-03-18T03:43:00       # 最終更新日時
done = false
```

`name` 以外は省略可。表の列は、カテゴリ内に値があるものだけ表示される。
カテゴリを増やすときは `data/08-<id>.toml` を作り、先頭に `[category]` の `title` と `order` を書く。

## SQL で集計する

`build/todo.db` はビルドのたびに作り直される SQLite DB。

```bash
python -c "import sqlite3; [print(*r) for r in sqlite3.connect('TODO/build/todo.db').execute('SELECT title, done, total FROM category_progress')]"
```
