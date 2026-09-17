#!/usr/bin/env bash
# 端到端演练 git-push-repo skill
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && { pwd -W 2>/dev/null || pwd; })"
S="$HERE/git_flow.py"
PY="${PY:-python}"
T=$(mktemp -d)
BARE="$T/remote.git"
echo "TMP=$T"

git init --bare "$BARE" -b main >/dev/null 2>&1
mkdir -p "$T/work1" && cd "$T/work1"
git init -b main >/dev/null 2>&1
echo "# 测试仓库" > README.md
echo "SECRET=abc123" > .env
mkdir -p data/raw && echo "a,b" > data/1.csv

echo "=== 1) check（未配置远端/含敏感文件）==="
"$PY" "$S" check --dir "$T/work1" | tail -22
echo "exit=${PIPESTATUS[0]}"

echo "=== 2) push --no-gitignore（应被门禁拦截，exit 2）==="
"$PY" "$S" push --dir "$T/work1" --no-gitignore --url "$BARE" -m "chore: 初始提交" | tail -8
echo "exit=${PIPESTATUS[0]}"

echo "=== 3) push（默认生成 .gitignore，应成功）==="
"$PY" "$S" push --dir "$T/work1" --url "$BARE" -m "chore: 初始提交" | tail -12
echo "exit=${PIPESTATUS[0]}"

echo "=== 4) 远端内容核验 ==="
git --git-dir="$BARE" log --oneline
echo "--- 远端文件树（.env 不应出现）---"
git --git-dir="$BARE" ls-tree -r --name-only HEAD

echo "=== 5) 制造非快进：另克隆一个副本并先推 ==="
git clone "$BARE" "$T/work2" >/dev/null 2>&1
cd "$T/work2" && echo "他人改动" > other.md
git add -A >/dev/null && git commit -m "docs: 他人提交" >/dev/null && git push >/dev/null 2>&1
echo "work2 pushed"

echo "=== 6) work1 直接 push（应被拒，exit 2）==="
cd "$T/work1" && echo "本地新改动" > local.md
"$PY" "$S" push --dir "$T/work1" -m "feat: 本地改动" | tail -6
echo "exit=${PIPESTATUS[0]}"

echo "=== 7) work1 push --pull-rebase（应自动 rebase 后成功）==="
"$PY" "$S" push --dir "$T/work1" --pull-rebase -m "feat: 本地改动" | tail -10
echo "exit=${PIPESTATUS[0]}"

echo "=== 8) 最终远端历史 ==="
git --git-dir="$BARE" log --oneline --graph
echo "=== 9) check --json 片段 ==="
"$PY" "$S" check --dir "$T/work1" --json | head -14
echo "=== 10) dry-run ==="
"$PY" "$S" push --dir "$T/work1" --dry-run -m "test: 演练" | tail -8
echo "ALL-DONE"
