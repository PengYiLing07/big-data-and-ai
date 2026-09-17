#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
git_flow.py -- 本地仓库 Git 全流程助手（skill: git-push-repo）

子命令:
    check   体检：是否仓库 / 分支 / 远端 / 身份 / 变更 / 风险文件（敏感文件、大文件）
    init    初始化仓库 + 生成 .gitignore（可单独用，也被 push --init 内部调用）
    commit  暂存并提交（不做远端操作）
    push    全流程：按需 init -> .gitignore -> 身份 -> 体检门禁 -> add -> commit -> remote -> push

示例:
    python git_flow.py check
    python git_flow.py check --json
    python git_flow.py push -m "feat: 新增学习地图 13 次课版"
    python git_flow.py push --init --branch main -m "chore: 初始提交"
    python git_flow.py push --url https://github.com/user/repo.git -m "docs: 更新 README"
    python git_flow.py push --pull-rebase -m "fix: 变量名拼写"
    python git_flow.py push --dry-run -m "test: 演练"

退出码: 0 成功 / 1 失败 / 2 需要人工决策（缺身份、有风险文件、非快进被拒等）
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BIG_FILE_MB = 50
SCAN_LIMIT = 20000

SECRET_RE = re.compile(
    r"(^|/)("
    r"\.env(\..+)?|"
    r"\.aws/credentials|"
    r"id_rsa|id_dsa|id_ecdsa|id_ed25519|"
    r"credentials\.json|service-account.*\.json|"
    r"secrets?\.(ya?ml|json|toml|ini)|"
    r"\.npmrc|\.pypirc|\.netrc"
    r")$"
    r"|\.(pem|key|p12|pfx|keystore|jks|ppk|asc)$",
    re.IGNORECASE,
)

BINARY_LOG = ""


def out(msg=""):
    print(msg)


def section(title):
    out("")
    out("=" * 60)
    out(title)
    out("=" * 60)


# ---------------------------------------------------------------- git helpers
def find_git():
    return shutil.which("git")


def git(args, cwd, dry=False, timeout=180):
    """执行 git 命令，返回 (code, stdout, stderr)。dry=True 时只回显。"""
    global BINARY_LOG
    printable = "git " + " ".join(args)
    if dry:
        out("  [DRY-RUN] " + printable)
        return 0, "", ""
    try:
        p = subprocess.run(
            ["git"] + list(args),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 124, "", "命令超时: " + printable
    except OSError as exc:
        return 127, "", "无法执行 git: %s" % exc
    BINARY_LOG += printable + "\n"
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def is_repo(cwd):
    code, so, _ = git(["rev-parse", "--is-inside-work-tree"], cwd)
    return code == 0 and so.strip() == "true"


def repo_root(cwd):
    code, so, _ = git(["rev-parse", "--show-toplevel"], cwd)
    return so if code == 0 else ""


def cfg(cwd, key):
    code, so, _ = git(["config", "--get", key], cwd)
    return so if code == 0 else ""


# ---------------------------------------------------------------- scan helpers
def parse_status(cwd):
    """返回 (staged, modified, untracked, untracked_files)。"""
    code, so, _ = git(["status", "--porcelain", "-uall"], cwd)
    staged = modified = 0
    untracked = []
    if code != 0:
        return 0, 0, 0, []
    for line in so.splitlines():
        if line.startswith("??"):
            untracked.append(line[3:].strip().strip('"'))
            continue
        x, y = line[0], line[1]
        if x not in (" ", "?"):
            staged += 1
        if y not in (" ", "?"):
            modified += 1
    return staged, modified, len(untracked), untracked


def scan_risky(cwd, candidates, deep=False):
    """扫描敏感文件与超大文件。candidates: 相对路径列表。"""
    secrets, big = [], []
    limit = BIG_FILE_MB * 1024 * 1024

    todo = list(candidates)
    if deep:
        code, so, _ = git(["ls-files"], cwd)
        if code == 0:
            todo += [p for p in so.splitlines() if p.strip()]

    seen = set()
    for rel in todo[:SCAN_LIMIT]:
        rel = rel.strip()
        if not rel or rel in seen:
            continue
        seen.add(rel)
        if SECRET_RE.search(rel.replace("\\", "/")):
            secrets.append(rel)
        full = Path(cwd) / rel
        try:
            if full.is_file():
                size = full.stat().st_size
                if size > limit:
                    big.append({"path": rel, "mb": round(size / 1024 / 1024, 1)})
        except OSError:
            pass
    return secrets, big


# ---------------------------------------------------------------- preflight
def collect(cwd, deep=False):
    info = {
        "cwd": str(cwd),
        "git": find_git() or "",
        "is_repo": is_repo(cwd),
        "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if not info["git"]:
        info["error"] = "未找到 git，请先安装 Git 并加入 PATH"
        return info
    info["git_version"] = git(["--version"], cwd)[1]

    if not info["is_repo"]:
        return info

    root = repo_root(cwd)
    info["root"] = root
    cwd = root

    info["branch"] = git(["branch", "--show-current"], cwd)[1] or "(detached HEAD)"
    info["head"] = git(["log", "-1", "--pretty=%h %s"], cwd)[1]
    info["head_count"] = git(["rev-list", "--count", "HEAD"], cwd)[1] or "0"

    remotes = {}
    for line in git(["remote", "-v"], cwd)[1].splitlines():
        parts = line.split()
        if len(parts) >= 2:
            remotes[parts[0]] = parts[1]
    info["remotes"] = remotes

    info["user_name"] = cfg(cwd, "user.name")
    info["user_email"] = cfg(cwd, "user.email")
    info["autocrlf"] = cfg(cwd, "core.autocrlf")

    upstream = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd)
    info["upstream"] = upstream[1] if upstream[0] == 0 else ""

    info["ahead"] = info["behind"] = None
    if info["upstream"]:
        lr = git(["rev-list", "--left-right", "--count", info["upstream"] + "...HEAD"], cwd)
        if lr[0] == 0:
            nums = lr[1].split()
            if len(nums) == 2:
                info["behind"], info["ahead"] = int(nums[0]), int(nums[1])

    staged, modified, untracked, files = parse_status(cwd)
    info.update(staged=staged, modified=modified, untracked=untracked)
    info["untracked_files"] = files
    info["gitignore"] = os.path.isfile(os.path.join(cwd, ".gitignore"))

    secrets, big = scan_risky(cwd, files, deep=deep)
    info["secret_files"] = secrets
    info["big_files"] = big

    if info["upstream"]:
        info["unpushed"] = git(
            ["log", "--oneline", "@{u}..HEAD"], cwd
        )[1].splitlines()
    else:
        info["unpushed"] = []
    return info


def gate(info, allow_risky=False):
    """体检结论：返回 (ok, blocking_notes)。"""
    notes = []
    if not info["git"]:
        return False, ["未安装 git"]
    if not info["is_repo"]:
        return False, ["当前目录不是 git 仓库，需先 init（加 --init）"]
    if info["secret_files"]:
        notes.append("疑似敏感文件: " + ", ".join(info["secret_files"]))
    if info["big_files"]:
        notes.append(
            "超大文件(>%dMB): " % BIG_FILE_MB
            + ", ".join("%s %.1fMB" % (b["path"], b["mb"]) for b in info["big_files"])
        )
    if notes and not allow_risky:
        return False, notes
    return True, notes


def print_report(info):
    section("Git 体检报告  " + info["now"])
    if not info["git"]:
        out("[FAIL] 未找到 git 可执行文件")
        return
    out("[OK]   %s" % info["git_version"])
    out("目录   %s" % info["cwd"])

    if not info["is_repo"]:
        out("[FAIL] 不是 git 仓库 —— 需先 git init（或用 push --init）")
        return

    out("仓库根 %s" % info["root"])
    out("分支   %s   |  HEAD: %s   |  提交总数: %s"
        % (info["branch"], info["head"] or "(无提交)", info["head_count"]))
    out("远端   %s" % (", ".join("%s -> %s" % kv for kv in info["remotes"].items()) or "(未配置)"))
    out("身份   %s <%s>" % (info["user_name"] or "(缺失)", info["user_email"] or "(缺失)"))
    if info["autocrlf"]:
        out("换行   core.autocrlf=%s" % info["autocrlf"])
    out("跟踪   upstream=%s  领先 %s  落后 %s"
        % (info["upstream"] or "(无)",
           "-" if info["ahead"] is None else info["ahead"],
           "-" if info["behind"] is None else info["behind"]))
    out("变更   已暂存 %d / 未暂存 %d / 未跟踪 %d" % (info["staged"], info["modified"], info["untracked"]))
    out("忽略文件 .gitignore %s" % ("存在" if info["gitignore"] else "缺失"))

    if info["unpushed"]:
        out("")
        out("尚未推送的提交 (%d):" % len(info["unpushed"]))
        for line in info["unpushed"][:20]:
            out("  " + line)

    warn = False
    if info["secret_files"]:
        warn = True
        out("")
        out("[WARN] 疑似敏感文件（勿提交）:")
        for p in info["secret_files"]:
            out("  - " + p)
    if info["big_files"]:
        warn = True
        out("")
        out("[WARN] 超大文件（GitHub 单文件上限 100MB，建议 Git LFS 或忽略）:")
        for b in info["big_files"]:
            out("  - %s  %.1fMB" % (b["path"], b["mb"]))
    if not info["user_name"] or not info["user_email"]:
        warn = True
        out("")
        out("[WARN] user.name / user.email 缺失，commit 会失败：")
        out('  git config user.name "你的名字" && git config user.email "你的邮箱"')
    if not warn:
        out("")
        out("[OK]   未发现阻断性问题")


# ---------------------------------------------------------------- commands
def ensure_gitignore(cwd, dry=False, quiet=False):
    path = Path(cwd) / ".gitignore"
    if path.exists():
        return "skip"
    tpl = Path(__file__).resolve().parent.parent / "assets" / "gitignore-template.txt"
    text = tpl.read_text(encoding="utf-8") if tpl.exists() else "*.log\n__pycache__/\n.env\n"
    if dry:
        out("  [DRY-RUN] 写入 .gitignore（%d 行）" % len(text.splitlines()))
        return "dry"
    path.write_text(text, encoding="utf-8")
    if not quiet:
        out("[OK]   已生成 .gitignore")
    return "written"


def do_init(cwd, branch, dry=False, write_gitignore=True):
    if is_repo(cwd):
        out("[SKIP] 已是 git 仓库")
        return 0
    code, _, err = git(["init", "-b", branch], cwd, dry=dry)
    if code != 0:
        # 旧版 git 不支持 -b
        code, _, err = git(["init"], cwd, dry=dry)
        if code == 0:
            git(["symbolic-ref", "HEAD", "refs/heads/" + branch], cwd, dry=dry)
    if code != 0:
        out("[FAIL] git init 失败: " + err)
        return 1
    out("[OK]   已初始化仓库，默认分支 %s" % branch)
    if write_gitignore:
        ensure_gitignore(cwd, dry=dry)
    return 0


def cmd_check(a):
    cwd = Path(a.dir).resolve()
    info = collect(cwd, deep=a.deep)
    if a.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print_report(info)
    ok, _ = gate(info, allow_risky=True)
    return 0 if ok else 1


def cmd_init(a):
    cwd = Path(a.dir).resolve()
    code = do_init(cwd, a.branch, dry=a.dry_run, write_gitignore=not a.no_gitignore)
    if code == 0 and a.write_gitignore:
        ensure_gitignore(cwd, dry=a.dry_run)
    return code


def do_commit(cwd, message, paths, dry=False, allow_risky=False, quiet=False):
    """暂存 + 提交。返回 (code, committed, note)。"""
    info = collect(cwd)
    if not info["is_repo"]:
        return 1, False, "不是 git 仓库"

    if not info["user_name"] or not info["user_email"]:
        return 2, False, "缺少 git 身份，无法提交"

    staged_now, modified, untracked, files = parse_status(cwd)
    secrets, big = scan_risky(cwd, files)
    if (secrets or big) and not allow_risky:
        detail = []
        if secrets:
            detail.append("敏感文件: " + ", ".join(secrets))
        if big:
            detail.append("大文件: " + ", ".join("%s(%.1fMB)" % (b["path"], b["mb"]) for b in big))
        return 2, False, "体检未通过 -> " + " | ".join(detail)

    if staged_now == 0 and modified == 0 and untracked == 0:
        if not quiet:
            out("[INFO] 工作区干净，没有需要提交的变更")
        return 0, False, "nothing-to-commit"

    if not message:
        return 2, False, "有变更但未提供提交信息（-m）"

    add_args = ["add", "--"] + list(paths) if paths else ["add", "-A"]
    code, _, err = git(add_args, cwd, dry=dry)
    if code != 0:
        return 1, False, "git add 失败: " + err

    code, so, err = git(["commit", "-m", message], cwd, dry=dry)
    if code != 0:
        if "nothing to commit" in (so + err):
            return 0, False, "nothing-to-commit"
        return 1, False, "git commit 失败: " + (err or so)
    if not quiet:
        out("[DRY-RUN] 未实际提交（演练）" if dry else "[OK]   已提交: %s" % message)
    return 0, True, "committed"


def do_push(cwd, remote, branch, dry=False, pull_rebase=False, quiet=False):
    """推送；非快进时可选自动 pull --rebase 后重试一次。"""
    url = git(["remote", "get-url", remote], cwd)
    if url[0] != 0:
        return 2, "远端 %s 不存在（用 --url 配置）" % remote
    url = url[1]

    if not quiet:
        out("推送到 %s -> %s" % (remote, url))
    code, so, err = git(["push", "-u", remote, branch], cwd, dry=dry)
    if code == 0:
        if dry:
            if not quiet:
                out("[DRY-RUN] 未实际推送（演练）")
            return 0, "dry-run"
        if not quiet:
            out("[OK]   推送成功")
        return 0, "pushed"

    blob = (so + "\n" + err).lower()
    if any(k in blob for k in ("non-fast-forward", "rejected", "fetch first", "updates were rejected")):
        if pull_rebase:
            out("[WARN] 远端有新提交，先 pull --rebase 再重试")
            code2, so2, err2 = git(["pull", "--rebase", remote, branch], cwd, dry=dry)
            if code2 != 0:
                git(["rebase", "--abort"], cwd, dry=dry)
                return 1, "pull --rebase 冲突，已 abort，需人工解决: " + (err2 or so2)
            code3, so3, err3 = git(["push", "-u", remote, branch], cwd, dry=dry)
            if code3 == 0:
                return 0, "pushed-after-rebase"
            return 1, "rebase 后推送仍失败: " + (err3 or so3)
        return 2, (
            "推送被拒（非快进）。建议: git pull --rebase %s %s（或加 --pull-rebase 自动处理）；"
            "若确认要先备份，再谈 --force。禁止对共享分支强推。" % (remote, branch)
        )

    if any(k in blob for k in ("authentication failed", "permission denied", "could not read username",
                               "publickey", "403", "terminal prompts disabled", "invalid username or password")):
        return 2, "认证失败。HTTPS 需用 Personal Access Token（不是登录密码）；SSH 需把公钥加到平台账号。详见 references/remotes.md"
    if "does not appear to be a git repository" in blob or "repository not found" in blob:
        return 2, "远端地址无效或无权限: %s" % url

    return 1, "推送失败: " + (err or so)


def cmd_commit(a):
    cwd = Path(a.dir).resolve()
    code, committed, note = do_commit(cwd, a.message, a.paths, dry=a.dry_run,
                                      allow_risky=a.allow_risky)
    if code != 0:
        out("[FAIL] " + note)
    elif note == "nothing-to-commit":
        out("[INFO] 无变更，跳过提交")
    return code


def cmd_push(a):
    cwd = Path(a.dir).resolve()
    section("Git 全流程推送")
    out("目录: %s" % cwd)
    out("模式: %s" % ("演练 (dry-run)" if a.dry_run else "实际执行"))

    # 1) 仓库
    if not is_repo(cwd):
        if not a.init:
            out("[FAIL] 不是 git 仓库；如需自动初始化请加 --init")
            return 1
        code = do_init(cwd, a.branch, dry=a.dry_run, write_gitignore=not a.no_gitignore)
        if code != 0:
            return code

    # 2) .gitignore
    if not a.no_gitignore:
        ensure_gitignore(cwd, dry=a.dry_run)

    # 3) 身份
    if a.name or a.email:
        if a.name:
            git(["config", "user.name", a.name], cwd, dry=a.dry_run)
        if a.email:
            git(["config", "user.email", a.email], cwd, dry=a.dry_run)
        out("[OK]   已写入本地仓库 git 身份")

    info = collect(cwd)
    if not info["user_name"] or not info["user_email"]:
        out("[FAIL] user.name / user.email 缺失，先配置后再推送：")
        out('  python git_flow.py push --name "你的名字" --email "you@example.com" -m "..."')
        return 2

    ok, notes = gate(info, allow_risky=a.allow_risky)
    if not ok:
        out("[FAIL] 体检未通过：")
        for n in notes:
            out("  - " + n)
        out("确认无风险后可加 --allow-risky 继续（慎用）")
        return 2
    for n in notes:
        out("[WARN] " + n)

    # 4) 提交
    code, committed, note = do_commit(cwd, a.message, a.paths, dry=a.dry_run,
                                      allow_risky=a.allow_risky)
    if code == 2:
        out("[FAIL] " + note)
        return 2
    if code == 1:
        out("[FAIL] " + note)
        return 1
    if note == "nothing-to-commit":
        out("[INFO] 工作区无变更，跳过提交")

    # 5) 远端
    code, so, _ = git(["remote", "get-url", a.remote], cwd)
    if a.url:
        if code == 0:
            git(["remote", "set-url", a.remote, a.url], cwd, dry=a.dry_run)
            out("[OK]   已更新远端 %s -> %s" % (a.remote, a.url))
        else:
            git(["remote", "add", a.remote, a.url], cwd, dry=a.dry_run)
            out("[OK]   已添加远端 %s -> %s" % (a.remote, a.url))
    elif code != 0:
        out("[FAIL] 未配置远端。请提供仓库地址：")
        out('  python git_flow.py push --url https://github.com/<user>/<repo>.git -m "..."')
        return 2

    # 6) 分支与推送
    branch = git(["branch", "--show-current"], cwd)[1] or a.branch
    code, note = do_push(cwd, a.remote, branch, dry=a.dry_run,
                         pull_rebase=a.pull_rebase)
    if code == 2:
        out("[FAIL] " + note)
        return 2
    if code == 1:
        out("[FAIL] " + note)
        return 1

    if a.dry_run:
        section("演练结束：以上为将执行的步骤，未做任何实际改动")
        return 0

    # 7) 校验
    after = collect(cwd)
    section("结果")
    out("分支 %s   远端 %s" % (branch, after["remotes"].get(a.remote, "?")))
    out("最新提交 %s" % after["head"])
    out("领先/落后  %s / %s" % (after["ahead"], after["behind"]))
    if after["ahead"] == 0 and after["upstream"]:
        out("[OK]   本地与远端已同步")
    return 0


# ---------------------------------------------------------------- entry
def main():
    ap = argparse.ArgumentParser(description="本地仓库 Git 全流程助手")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--dir", default=".", help="仓库目录，默认当前目录")
        p.add_argument("--dry-run", action="store_true", help="只回显将执行的 git 命令")

    c = sub.add_parser("check", help="体检")
    common(c)
    c.add_argument("--json", action="store_true", help="以 JSON 输出")
    c.add_argument("--deep", action="store_true", help="同时扫描已跟踪文件的大小")
    c.set_defaults(func=cmd_check)

    i = sub.add_parser("init", help="初始化仓库")
    common(i)
    i.add_argument("--branch", default="main")
    i.add_argument("--write-gitignore", action="store_true")
    i.add_argument("--no-gitignore", action="store_true")
    i.set_defaults(func=cmd_init)

    m = sub.add_parser("commit", help="暂存并提交")
    common(m)
    m.add_argument("-m", "--message", required=True)
    m.add_argument("--paths", nargs="*", default=[])
    m.add_argument("--allow-risky", action="store_true")
    m.set_defaults(func=cmd_commit)

    p = sub.add_parser("push", help="全流程：init/体检/提交/推送")
    common(p)
    p.add_argument("-m", "--message", default="")
    p.add_argument("--paths", nargs="*", default=[])
    p.add_argument("--remote", default="origin")
    p.add_argument("--url", default="")
    p.add_argument("--branch", default="main")
    p.add_argument("--init", action="store_true", help="不是仓库时自动初始化")
    p.add_argument("--pull-rebase", action="store_true", help="被拒时自动 pull --rebase 后重试")
    p.add_argument("--allow-risky", action="store_true", help="风险文件门禁放行（慎用）")
    p.add_argument("--no-gitignore", action="store_true", help="不自动生成 .gitignore")
    p.add_argument("--name", default="", help="缺失时写入 user.name")
    p.add_argument("--email", default="", help="缺失时写入 user.email")
    p.set_defaults(func=cmd_push)

    a = ap.parse_args()
    if not find_git():
        out("[FAIL] 未找到 git，请安装 Git 并加入 PATH")
        return 1
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
