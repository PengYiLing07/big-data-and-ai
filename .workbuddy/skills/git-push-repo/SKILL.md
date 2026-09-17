---
name: git-push-repo
description: 把本地目录走完完整 Git 流程并推送到远端——覆盖仓库初始化、.gitignore 生成、身份配置、体检门禁（敏感文件/大文件检测）、暂存提交、远端配置、推送与结果校验，并处置认证失败、非快进被拒、rebase 冲突、误提交密钥、大文件超限等故障。当用户说"推送代码/推送本地仓库/提交并推送/git push/初始化仓库并上传/同步到远端/上传到 GitHub 或 Gitee"，或需要排查 push 被拒、Authentication failed、Permission denied、误提交 .env 等问题时使用。
agent_created: true
---

# 推送本地仓库（Git 全流程）

## 这个 skill 解决什么

把一个本地目录从"没有版本控制"一路送到"远端仓库上能看到内容"：init → .gitignore → 身份 → 体检 → add → commit → remote → push → 校验。
同时把三个最容易翻车的点做成硬门禁：**敏感文件被提交**、**大文件超限**、**对共享分支强推**。

## 铁律（先记住，任何情况下不破）

1. **推送前必须先展示将提交的内容**（哪些文件、多少改动、提交信息），得到用户确认或按用户已给出的明确指令执行；信息不全时先问，不要猜。
2. **不做破坏性操作**：`push --force` / `--force-with-lease`、`reset --hard`、`filter-repo`、删除远端分支——只有用户明确点名要求时才可执行，且要先说明会改写历史。
3. **绝不强推 `main` / `master` / 共享分支**。被拒时优先 `pull --rebase` 重试。
4. **绝不提交密钥/凭据**（`.env`、`*.pem`、`token`、`credentials.json`）。发现后默认阻断流程，并向用户说明；已推送过的要提示去平台作废重发。
5. **凭据不落盘**：不要把 `https://user:token@host/...` 写进 remote URL，改用系统凭据管理器或 SSH。
6. **不动用户没让动的仓库**：默认在用户指定目录操作；`--dir` 指到个人目录（Desktop/Downloads/Documents）时先确认。

## 标准流程

### 第 0 步：先体检（必做，不跳）

```bash
python "<skill_dir>/scripts/git_flow.py" check --dir "<目标目录>"
```

输出会明确给出：是否已是仓库、分支与 HEAD、远端、身份是否齐全、暂存/未暂存/未跟踪数量、**疑似敏感文件**、**超过 50MB 的文件**、未推送的提交列表。
若目标还不在版本控制下，先问清远端地址（GitHub / Gitee / 自建 / 局域网裸仓库 / 纯本地备份），再往下走。

### 第 1 步：判断走哪条路

| 体检结果 | 动作 |
|---|---|
| 不是仓库 | `push --init`（会自动生成 .gitignore 并按 `main` 建分支） |
| 是仓库但缺远端 | 先向用户要地址，用 `--url` 配置 |
| 是仓库已有远端 | 直接进入提交与推送 |
| 有敏感/大文件告警 | **停下来**，先与用户确认是移除、忽略还是改用 Git LFS，不得直接 `--allow-risky` 绕过 |
| 缺 user.name/email | 补配置（见 references/remotes.md 第 5 节） |

### 第 2 步：提交信息

按 Conventional Commits 风格写，用中文也行，关键是"动词 + 对象"：

```
feat: 新增学习地图 13 次课版
fix: 修正舆情统计脚本的编码错误
docs: 补充作业说明
chore: 初始提交
```

一次提交只讲一件事；批量杂改可以 `chore: 批量更新<范围>`。**不要**用 `update` / `修改一下` 这类无信息量的信息。提交信息里需要引用文件路径时，避免让 shell 转义出错——用双引号包住整个 `-m` 参数。

### 第 3 步：执行全流程

```bash
# 已存在的仓库，常规推送
python "<skill_dir>/scripts/git_flow.py" push -m "feat: 新增学习地图 13 次课版"

# 从零开始：初始化 + 首次推送
python "<skill_dir>/scripts/git_flow.py" push --init --branch main \
  --url https://github.com/<user>/<repo>.git \
  -m "chore: 初始提交"

# 远端有他人提交导致被拒，自动 rebase 后重试
python "<skill_dir>/scripts/git_flow.py" push --pull-rebase -m "fix: 修正路径"

# 不实际执行，先演练看命令
python "<skill_dir>/scripts/git_flow.py" push --dry-run -m "test: 演练"

# 只提交不推送
python "<skill_dir>/scripts/git_flow.py" commit -m "wip: 草稿"
```

退出码：`0` 成功 / `1` 执行失败 / `2` 需人工决策（缺身份、有风险文件、认证失败、非快进被拒）。

### 第 4 步：校验与汇报

```bash
git -C "<目标目录>" status -sb
git -C "<目标目录>" log --oneline -3
git -C "<目标目录>" log --oneline @{u}..HEAD     # 应为空，空即已同步
```

给用户的汇报固定回答这四句：**推到了哪个远端与分支** / **本次提交的 sha 与信息** / **本次涉及的文件范围** / **还有没有未同步的内容或需要他决策的事**。

## 遇到问题

- 认证失败、非快进被拒、rebase 冲突、误提交密钥、大文件、Windows 换行与长路径 → 读 `references/troubleshooting.md`，里面按报错关键词给了处置动作。
- 远端地址形态、HTTPS 令牌 / SSH 配置、代理、Windows 全局配置 → 读 `references/remotes.md`。

## 脚本说明

`scripts/git_flow.py` 只依赖标准库，用 `git` 子进程完成全部动作，不需要装额外包。
调用时用绝对路径，脚本目录即本 SKILL.md 所在目录下的 `scripts/`。

| 子命令 | 作用 | 关键参数 |
|---|---|---|
| `check` | 体检并输出报告 | `--dir` `--json` `--deep` |
| `init` | 初始化仓库 + 生成 .gitignore | `--branch` `--no-gitignore` |
| `commit` | 暂存并提交 | `-m` `--paths` `--allow-risky` |
| `push` | 全流程 | `-m` `--url` `--remote` `--branch` `--init` `--pull-rebase` `--dry-run` `--allow-risky` `--name` `--email` |

`assets/gitignore-template.txt` 是针对"Python 数据分析 + 中文文档"场景的忽略模板（含密钥、数据文件、Office 临时文件、`.workbuddy/memory/`）。

`scripts/smoke_test.sh` 是自检脚本：在临时目录造裸仓库当远端，依次验证"敏感文件被拦 → 首次推送成功 → 非快进被拒 → `--pull-rebase` 自动修复"四条路径，改动脚本后跑一遍确认没坏。它会全程使用临时目录，不碰用户仓库。

## 刻意不做的事

- 不自动创建远端仓库（GitHub/Gitee 建仓需登录网页或 CLI，由用户完成，本 skill 只负责配置地址并推送）。
- 不擅自改写历史、不删远端分支、不处理 submodule。
- 不代替用户解决 rebase 冲突内容——冲突需人来判断保留哪一版，脚本只会 `abort` 并把控制权交回。
- 不管理 CI/CD、不配置部署。
