"""作業ブランチを main にマージし、アーティファクト用のサイトをビルドする。

wf-publish スキルから呼ぶ。Claude のトークン消費を抑えるため、出力は最小限にしている。

    python scripts/release.py merge [--branch NAME] [--no-push]
        作業ブランチを main にマージして push する。
        --branch を省略すると現在のブランチ。main 上で省略した場合は、
        main より進んでいる origin のブランチを一覧して終了する。
    python scripts/release.py build
        scripts/build_artifact.py を実行し、前回公開時から変わったファイルだけを
        Artifact ツールに渡す引数（JSON）として出力する。
    python scripts/release.py mark-published
        公開に成功したら実行する。今のビルド内容を公開済みとして記録する。

終了コード: 0 成功 / 1 中断（理由を表示）/ 2 マージの衝突（衝突ファイルを表示）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "artifact"
CONFIG = ROOT / "scripts" / "artifact.json"
STATE = ROOT / "build" / "artifact-published.json"  # build/ は Git 管理外
MAIN = "main"
TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} が失敗しました:\n{r.stderr.strip()}")
    return r.stdout.strip()


def merge_ref(ref: str, title: str) -> None:
    r = subprocess.run(["git", "merge", "--no-ff", "-m", f"{title}\n\n{TRAILER}", ref], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        conflicts = git("diff", "--name-only", "--diff-filter=U", check=False)
        if conflicts:
            print("衝突しました。解決して `git commit --no-edit` してから再実行してください:\n" + conflicts)
            sys.exit(2)
        sys.exit(r.stderr.strip())
    print(f"マージしました: {ref} -> {MAIN}")


def cmd_merge(branch: str | None, push: bool) -> None:
    dirty = git("status", "--porcelain", "--untracked-files=no")
    if dirty:
        sys.exit("未コミットの変更があるので中断しました。先にコミットするか退避してください:\n" + dirty)
    git("fetch", "-q", "origin")
    current = git("rev-parse", "--abbrev-ref", "HEAD")
    branch = branch or (current if current != MAIN else None)
    if not branch and git("rev-list", "--count", f"{MAIN}..origin/{MAIN}") == "0":
        ahead = [b for b in git("branch", "-r", "--format=%(refname:short)").splitlines()
                 if b not in (f"origin/{MAIN}", "origin/HEAD", "origin")
                 and any(l.startswith("+") for l in git("cherry", MAIN, b).splitlines())]
        sys.exit("マージするブランチを --branch で指定してください。main より進んでいるブランチ:\n"
                 + ("\n".join(f"  {b}" for b in ahead) or "  （なし）"))
    ref = None
    if branch:
        ref = branch
        if git("rev-parse", "--verify", "--quiet", branch, check=False) == "":
            ref = f"origin/{branch.removeprefix('origin/')}"
    if current != MAIN:
        git("checkout", "-q", MAIN)
    # origin/main に先行コミットがあれば取り込む（分岐していてもマージで合流させる）
    if git("rev-list", "--count", f"{MAIN}..origin/{MAIN}") != "0":
        merge_ref(f"origin/{MAIN}", f"[merge]origin/mainを取り込み")
    if ref:
        # ハッシュが違っても同じ変更が main にあれば取り込み済みとみなす
        pending = [l for l in git("cherry", MAIN, ref).splitlines() if l.startswith("+")]
        if not pending:
            print(f"{ref} は main に取り込み済みです")
        else:
            merge_ref(ref, f"[merge]{ref.removeprefix('origin/')}をmainにマージ")
    if push:
        git("push", "-q", "origin", MAIN)
        print("push しました: origin/main")


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def current_files() -> dict[str, str]:
    return {p.relative_to(OUT).as_posix(): digest(p) for p in sorted(OUT.rglob("*")) if p.is_file()}


def cmd_build() -> None:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_artifact.py")], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit("ビルドに失敗しました:\n" + (r.stderr or r.stdout)[-2000:])
    url = json.loads(CONFIG.read_text(encoding="utf-8"))["url"]
    now = current_files()
    old = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    changed = [f for f, h in now.items() if old.get(f) != h and f != "index.html"]
    removed = [f for f in old if f not in now]
    if old and not changed and not removed and old.get("index.html") == now["index.html"]:
        print("変更なし（公開は不要）")
        return
    rel = OUT.relative_to(ROOT).as_posix()
    files: dict[str, str | None] = {f: f"{rel}/{f}" for f in changed}
    files.update({f: None for f in removed})
    args = {"action": "publish", "url": url, "file_path": f"{rel}/index.html"}
    if files:
        args["files"] = files
    print(json.dumps(args, ensure_ascii=False))


def cmd_mark() -> None:
    STATE.write_text(json.dumps(current_files(), indent=0), encoding="utf-8")
    print("公開済みとして記録しました")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--branch")
    m.add_argument("--no-push", action="store_true")
    sub.add_parser("build")
    sub.add_parser("mark-published")
    a = ap.parse_args()
    if a.cmd == "merge":
        cmd_merge(a.branch, not a.no_push)
    elif a.cmd == "build":
        cmd_build()
    else:
        cmd_mark()


if __name__ == "__main__":
    main()
