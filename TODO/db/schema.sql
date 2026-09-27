-- ビルド時に data/ から毎回作り直す SQLite スキーマ。
-- 正本は data/*.toml で、DB は生成物 (build/todo.db)。

PRAGMA foreign_keys = ON;

CREATE TABLE categories (
    id          TEXT PRIMARY KEY,           -- ファイル名由来 (例: arcanes)
    title       TEXT NOT NULL,
    sort_order  INTEGER NOT NULL
);

CREATE TABLE items (
    id           INTEGER PRIMARY KEY,
    category_id  TEXT NOT NULL REFERENCES categories(id),
    name         TEXT NOT NULL,
    source       TEXT,                      -- 入手場所
    condition    TEXT,                      -- 入手条件
    required     INTEGER,                   -- 必要数
    url          TEXT,                      -- 参考リンク
    note         TEXT,
    done         INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
    updated_at   TEXT,                      -- ISO 8601
    sort_order   INTEGER NOT NULL,
    UNIQUE (category_id, name)
);

CREATE VIEW category_progress AS
SELECT c.id, c.title, c.sort_order,
       COUNT(i.id)              AS total,
       COALESCE(SUM(i.done), 0) AS done
FROM categories c
LEFT JOIN items i ON i.category_id = c.id
GROUP BY c.id
ORDER BY c.sort_order;
