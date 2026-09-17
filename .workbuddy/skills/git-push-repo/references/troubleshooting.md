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
