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
    serve.py          ローカルサーバー + 自動再ビルド + 編集 API
    todo_store.py     編集 API から TOML の 1 項目を書き換える
  site/
    templates/        HTML テンプレート (string.Template)
    static/           CSS / JS
  build/              生成物（git 管理外）
```

## 編集モード（ブラウザから更新）

TODO ページ右上の「編集モード」を押すと、ブラウザから直接 `data/*.toml` を書き換えられる（`serve.py` で起動しているときだけ表示される）。

- 必要数のない項目（装備・シーンなど）: チェックで完了／未完了を切り替え
- 必要数のある項目（アルケイン）: − / + で残りの必要数を増減。0 になると完了、1 以上に戻すと未完了。`updated` も自動で更新される
- パーツのある項目（装備）: 項目の下に並ぶパーツごとのチェックで入手済みを切り替え。全パーツそろうと完了になり、項目のチェックを切り替えると全パーツも同じ状態になる

変更はその場で表示に反映され、完了した項目が末尾に回るのは次に読み込んだとき。

## 項目の編集（ファイルを直接）

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

装備はパーツを `parts` に書くと、項目の下にパーツごとのチェックボックスの行が並ぶ。
同じパーツが 2 つ要るもの（二丁拳銃のバレルなど）は同じ名前を 2 回書く。
パーツによって入手場所が違うもの（Prime のレリックなど）は、パーツに `source` を書くと入手場所の列に出る。全パーツが同じ場所で手に入るなら、項目の `source` だけでよい。

```toml
[[items]]
name = "Aksondol"
parts = [
  { name = "設計図", done = false },
  { name = "バレル", done = false },
  { name = "バレル", done = false },
  { name = "レシーバー", done = false },
  { name = "レシーバー", done = false },
  { name = "リンク", done = false },
]
done = false

[[items]]
name = "Afentis Prime"
parts = [
  { name = "設計図", source = "Axi A22（レア）", done = false },
  { name = "バレル", source = "Neo C10（アンコモン）", done = false },
  { name = "ブレード", source = "Meso A12（レア）", done = false },
  { name = "ハンドル", source = "Meso D9（コモン）", done = false },
]
done = false
```

`name` 以外は省略可。表の列は、カテゴリ内に値があるものだけ表示される。
カテゴリを増やすときは `data/09-<id>.toml` を作り、先頭に `[category]` の `title` と `order` を書く。

## 新アップデートの追加要素を登録する

Claude Code で「Update 41 の追加要素を TODO に入れて」のように頼むと、プロジェクトスキル
[`wd-update-todo`](../.claude/skills/wd-update-todo/SKILL.md) が起動する。
パッチノートと Wiki を調べて候補を出し、選んだものだけを `data/*.toml` に追記する（`note` に「<アップデート名> で追加」が入る）。

## SQL で集計する

`build/todo.db` はビルドのたびに作り直される SQLite DB。

```bash
python -c "import sqlite3; [print(*r) for r in sqlite3.connect('TODO/build/todo.db').execute('SELECT title, done, total FROM category_progress')]"
```
