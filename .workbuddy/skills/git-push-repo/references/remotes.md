# 远端配置与认证

## 1. 选哪种远端

| 场景 | 远端地址形态 | 说明 |
|---|---|---|
| GitHub | `https://github.com/<user>/<repo>.git` 或 `git@github.com:<user>/<repo>.git` | 新建仓库时不要勾选任何初始化文件，否则首次 push 会被拒 |
| Gitee（码云） | `https://gitee.com/<user>/<repo>.git` | 国内网络更稳，认证同样用私人令牌 |
| GitLab / 自建 | `https://gitlab.com/<group>/<repo>.git` | 自建实例替换域名即可 |
| 局域网裸仓库 | `//server/share/repo.git`、`D:/git-repos/repo.git` | 先 `git init --bare` 造一个裸仓库，再把它当远端推 |
| 纯本地备份 | `D:/backup/repo.git` | 无网络也能跑完整流程 |

造一个本地裸仓库（做无网演练或局域网共享）：

```bash
git init --bare D:/git-repos/myrepo.git
python git_flow.py push --url D:/git-repos/myrepo.git -m "chore: 首次推送"
```

## 2. HTTPS 认证（推荐新手上手）

GitHub / Gitee 早已不接受账号密码，必须用 **Personal Access Token**：

- GitHub：Settings → Developer settings → Personal access tokens → Fine-grained tokens，
  勾选目标仓库的 `Contents: Read and write`。生成后形如 `ghp_xxx` / `github_pat_xxx`。
- Gitee：头像 → 设置 → 私人令牌 → 生成新令牌，勾选 `projects`。
- 使用方式：提示 `Username` 填平台用户名，`Password` 填令牌。
- 避免明文落盘：不要用 `git remote set-url https://user:token@host/...`。
  要免输，用系统凭据管理器：
  - Windows：`git config --global credential.helper manager`
  - macOS：`git config --global credential.helper osxkeychain`
  - Linux：`git config --global credential.helper store`（会明文存 `~/.git-credentials`，公网机器不建议）

## 3. SSH 认证（长期省事）

```bash
ssh-keygen -t ed25519 -C "you@example.com"      # 一路回车，默认 ~/.ssh/id_ed25519
# 公钥内容复制到平台 Settings → SSH Keys
gh auth login          # 或者用 GitHub CLI 一键配好
ssh -T git@github.com  # 验证，出现 "successfully authenticated" 即通
git remote set-url origin git@github.com:<user>/<repo>.git
```

排错顺序：`ssh -T` 通不通 → 远端 URL 是否 SSH 形态 → 是否把公钥加到了**当前账号**。

## 4. 代理与网络

国内访问 GitHub 常需代理（不要写进仓库配置，改用户级或环境变量）：

```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
git config --global --unset http.proxy   # 用完取消
```

或只对 GitHub 走代理：

```bash
git config --global http.https://github.com.proxy http://127.0.0.1:7890
```

## 5. 常见配置一次性设定

```bash
git config --global user.name "你的名字"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global core.autocrlf true     # Windows 建议，提交时 LF、检出时 CRLF
git config --global pull.rebase true       # 拉取用 rebase，历史更干净
git config --global push.default simple
git config --global core.quotepath false   # 中文文件名正常显示
```
