# 故障处理手册

先跑 `python scripts/git_flow.py check` 拿到现状，再对症下药。

## 一、认证类

| 报错关键词 | 原因 | 处置 |
|---|---|---|
| `Authentication failed` / `could not read Username` | HTTPS 用了登录密码 | 换 Personal Access Token 填入密码位 |
| `Permission denied (publickey)` | SSH 公钥没加到平台账号 | `ssh-keygen` → 上传公钥 → `ssh -T git@github.com` |
| `terminal prompts disabled` | 在非交互环境跑 push，无法输密码 | 改用令牌 + `credential.helper`，或 SSH 免密 |
| `403` / `remote: You do not have permission` | 令牌权限不足或不是该仓库成员 | 重新生成令牌并勾选 `Contents: Read and write` |
| `Repository not found` | URL 拼错，或私有仓库无权限 | `git remote -v` 核对，注意 `.git` 后缀与用户名大小写 |

## 二、推送被拒（非快进）

```
! [rejected]  main -> main (fetch first)
```

含义：远端有本地没有的提交。三种处置：

1. **推荐**：`git pull --rebase origin main` 后重推（本 skill 加 `--pull-rebase` 可自动做，冲突会 abort 并交回人工）。
2. 合并式：`git pull --no-rebase origin main` 产生一个合并提交。
3. 确认远端内容可弃（**仅限自己的分支**）：`git push --force-with-lease`。
   - 严禁对 `main` / `master` / 共享分支强推。
   - `--force-with-lease` 比 `--force` 安全：远端被别人推过就会失败而不是覆盖。

## 三、rebase 冲突

```bash
git status                 # 看 "both modified" 的文件
# 手工编辑冲突文件，删掉 <<<<<<< ======= >>>>>>> 标记
git add <冲突文件>
git rebase --continue
# 想放弃：git rebase --abort（回到 rebase 前状态）
```

## 四、提交错了文件 / 写错信息

| 情况 | 命令 | 注意 |
|---|---|---|
| 提交信息写错，**未推送** | `git commit --amend -m "新信息"` | 会改写最后一次提交 |
| 多提交了文件，**未推送** | `git reset --soft HEAD~1` 再重新 add | `--soft` 保留改动，`--mixed` 取消暂存但保留文件 |
| 已推送，想撤内容 | `git revert <sha>` | 生成反向提交，安全，适合共享分支 |
| 已推送，只想改信息 | 不建议；如必须，`git commit --amend` + `push --force-with-lease`，且先通知协作者 |

## 五、误提交了密钥 / 密码

**第一优先级是去平台把密钥作废重发**——历史里的密钥永远视为已泄露，删文件不等同于解除泄露。

```bash
# 1) 从当前版本移除并加入忽略
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "chore: 移除敏感文件"
git push

# 2) 若需从全部历史抹除（会改写历史，须与协作者协调，另需备份）
#    推荐用 git-filter-repo，而不是已弃用的 filter-branch
pip install git-filter-repo
git filter-repo --path .env --invert-paths
```

## 六、大文件推不上去

- GitHub 单文件硬上限 100MB、仓库建议 <1GB；Gitee 单文件上限更小。
- 方案：
  1. 从暂存区移除并忽略：`git rm --cached big.csv` + 写进 `.gitignore`；
  2. 已进入历史：`git filter-repo --path big.csv --invert-paths`；
  3. 确实要版本管理大数据：装 Git LFS（`git lfs install` / `git lfs track "*.parquet"` / `git add .gitattributes`）。

## 七、Windows 相关

| 现象 | 处置 |
|---|---|
| 满屏 `LF will be replaced by CRLF` 警告 | 无害；`git config --global core.autocrlf true` |
| 文件权限位莫名变化 | `git config core.filemode false` |
| 中文文件名显示成 `\346\226\207` | `git config --global core.quotepath false` |
| 路径太长报 `Filename too long` | `git config --global core.longpaths true` |
| 换行符整文件 diff | 加 `.gitattributes`：`* text=auto eol=lf` |

## 八、其它

| 报错 | 处置 |
|---|---|
| `src refspec main does not match any` | 还没有任何提交：先 commit，或首次用 `git push -u origin HEAD` |
| `remote origin already exists` | 已存在则用 `git remote set-url origin <url>` |
| `fatal: not a git repository` | 目录不对，或需 `git init`（本 skill `push --init`） |
| `dubious ownership in repository` | 目录属主与当前用户不一致：`git config --global --add safe.directory <path>` |
| `error: cannot lock ref` / `index.lock` 残留 | 确认没有其它 git 进程后删除 `.git/index.lock` |

## 九、追踪引用不更新（`.git/packed-refs` 里留了陈旧条目）

**现象**：远端明明已是最新，`git status` 却长期显示 `[ahead N]`；`git fetch` 输出 `xxx..yyy  main -> origin/main`，但 `git rev-parse refs/remotes/origin/main` 的值始终不变；`git push` 成功且远端 SHA 正确。

**判定**（逐条比对三个值）：

```
git ls-remote --heads origin            # 远端真实 SHA
git rev-parse HEAD                      # 本地 HEAD
git rev-parse refs/remotes/origin/main  # 本地追踪引用
grep origin/main .git/packed-refs       # 打包引用中的值
```

若「远端 SHA == 本地 HEAD ≠ 追踪引用」，说明问题只在本地记录，远端内容无误，可照常继续推送。

**处置**（把正确值写回）：

```
git update-ref refs/remotes/origin/main <远端 SHA>
git pack-refs --all     # 关键一步：让 packed-refs 采用当前值
git fetch origin        # 复核：值应保持不变，status 不再 ahead
```

**成因**：`refs/remotes/*` 一旦被 `pack-refs` 打包过，git 更新时会写入一个「松引用」`.git/refs/remotes/<remote>/<branch>`；本机曾出现松引用写入未生效、而 `packed-refs` 中的旧值持续被读取的情况，于是远端更新与本地记录脱钩。按上表手工写值再 `pack-refs --all` 可让两边重新对齐（本仓库 2026-09-17 实测有效）。

**规避**：只判断「是否需要推送」时不要依赖追踪引用，直接比对 `git rev-parse HEAD` 与 `git ls-remote --heads origin`。

---

## 十、如何独立核验「文件确实到远端了」

`git ls-remote` 只能证明**分支 SHA 一致**，证明不了文件内容。要把「作业/交付物确实在远端」讲实，用远端自身的接口取证，完全不经过本地 git：

| 目的 | 通道 |
|---|---|
| 远端最新提交与时间 | `https://api.github.com/repos/<owner>/<repo>/branches/<branch>` → `commit.sha` / `commit.commit.author.date` |
| 该分支下的**完整文件清单** | `https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1` → 遍历 `tree[].path` |
| **文件真实内容** | `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` |

要点：

1. **清单里有名字 ≠ 文件有内容**。曾遇到远端存在 `scripts/01.py` 但内容是命令行文本（跑起来 SyntaxError）、`.ipynb` 是空壳（无 `execution_count`、`outputs` 为空）。核验必须**读内容**：`.py` 看有没有 `import` / `def` / `print`；`.ipynb` 看每个 code cell 的 `execution_count` 是否有值、`outputs` 是否非空。
2. **本地 `curl` 可能被沙箱拦掉**（返回 `HTTP 000`），但 WebFetch 通道正常——用 WebFetch 拉上面的 URL，不要据此判定"仓库不存在"。
3. 公开仓库无需鉴权；私有仓库同样三条 URL 需要带 token。
4. Gitee 等平台有对应接口（`/api/v5/repos/<owner>/<repo>/git/trees/<sha>?recursive=1`），思路一致。

