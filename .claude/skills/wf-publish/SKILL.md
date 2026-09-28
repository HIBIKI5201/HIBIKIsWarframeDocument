---
name: wf-publish
description: 作業ブランチを main にマージして push し、TODO とストーリー資料をまとめた claude.ai のアーティファクト（Warframe Document）を最新の内容で更新する。「アーティファクトを更新して」「main にマージして公開」「スマホ用ページを最新にして」などの依頼で使う。
---

# main へのマージとアーティファクトの更新

処理はすべて `scripts/release.py` にまとめてある。**スクリプトの出力だけを見て進め、生成された HTML やスクリプト本体は読まない**（トークン節約のため）。公開先の URL は `scripts/artifact.json` にある。

## 1. 未コミットの変更をコミットする

`git status --short` で確認する。変更があれば、内容ごとにまとめてコミットする（`git diff` は `--stat` だけで判断してよい）。

- メッセージは `[add]` / `[update]` / `[change]` / `[delete]` などの接頭辞 + 日本語（例: `[update]TODOデータを更新`）。
- `.claude/launch.json` のような個人設定や、コミットしてよいか判断できないファイルは、ユーザーに聞く。

## 2. main にマージする

```bash
python scripts/release.py merge [--branch <ブランチ名>]
```

- 作業ブランチ上ならそのブランチを、`--branch` を付ければ指定したブランチ（`origin/` なしでも可）を main にマージして push する。
- main 上で `--branch` を省略すると、main より進んでいるブランチの一覧を出して止まる。1 つだけならそれを、複数ならどれをマージするかユーザーに聞く。マージするブランチがなければ手順 3 へ進む。
- 終了コード 2 は衝突。表示されたファイルだけを読んで解決し、`git add` → `git commit --no-edit` の後、同じコマンドを再実行する（取り込み済みと表示され push される）。
- push したくないと言われたときは `--no-push` を付ける。

## 3. ビルドする

```bash
python scripts/release.py build
```

- 「変更なし（公開は不要）」なら手順 4 は飛ばして報告する。
- それ以外は、Artifact ツールに渡す引数が 1 行の JSON で出る。前回公開時から変わったファイルだけが `files` に入り、消えたファイルは `null` になる。

## 4. アーティファクトを更新する

出力された JSON をそのまま Artifact ツールの引数にして 1 回呼ぶ（`action: "publish"`、`url`、`file_path`、`files`）。

- 「この会話で読んでいない」という理由で拒否されたら、`action: "read"` で同じ URL を 1 回読んでから同じ引数で再実行する。
- `overwrite_unread` を求められたら、拒否メッセージに出たパスを入れて再実行してよい（このスキルで生成したファイルで上書きするのが目的なので）。
- 公開に成功したら、次を実行して公開済みとして記録する。

```bash
python scripts/release.py mark-published
```

## 5. 報告する

マージしたブランチ、push の有無、公開したファイル数を 1〜3 行で報告する。
