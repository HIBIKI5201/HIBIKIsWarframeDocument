---
name: wf-publish
description: 作業ブランチを main にマージして push する。ストーリー資料は push すると GitHub Actions が GitHub Pages に公開する。「main にマージして公開」「マージして push して」「サイトを最新にして」などの依頼で使う。
---

# main へのマージと公開

処理は `scripts/release.py` にまとめてある。**スクリプトの出力だけを見て進め、スクリプト本体は読まない**（トークン節約のため）。

## 1. 未コミットの変更をコミットする

`git status --short` で確認する。変更があれば、内容ごとにまとめてコミットする（`git diff` は `--stat` だけで判断してよい）。

- メッセージは `[add]` / `[update]` / `[change]` / `[delete]` などの接頭辞 + 日本語（例: `[update]TODOデータを更新`）。
- `.claude/launch.json` のような個人設定や、コミットしてよいか判断できないファイルは、ユーザーに聞く。

## 2. main にマージする

```bash
python scripts/release.py merge [--branch <ブランチ名>]
```

- 作業ブランチ上ならそのブランチを、`--branch` を付ければ指定したブランチ（`origin/` なしでも可）を main にマージして push する。
- main 上で `--branch` を省略すると、main より進んでいるブランチの一覧を出して止まる。1 つだけならそれを、複数ならどれをマージするかユーザーに聞く。マージするブランチがなければ、未 push のコミットだけを push する。
- 終了コード 2 は衝突。表示されたファイルだけを読んで解決し、`git add` → `git commit --no-edit` の後、同じコマンドを再実行する（取り込み済みと表示され push される）。
- push したくないと言われたときは `--no-push` を付ける。

`main` の `StoryAnalysis/` に変更を push すると、GitHub Actions（`.github/workflows/pages.yml`）が GitHub Pages を自動で更新する（TODO は公開しない）。

## 3. 報告する

マージしたブランチと push の有無を 1〜2 行で報告する。
