# big-data-and-ai · 大数据与人工智能 个人课程仓库

本仓库是「大数据与人工智能」课程的个人学习仓库，也是我的作品集工具基础。
它既保存了一个**可复用的「概念学习资料生成 Skill」**，也保存了**由该 Skill 生成、并经我本人核查的概念学习资料**。

---

## 一、仓库用途

1. **沉淀可复用的学习工具**：仓库内的项目级 Skill（`concept-learner`）能接收任意新概念，自动产出一份结构完整、可核查的概念学习资料。
2. **保存经过人工核查的学习成果**：`learning-materials/` 下存放已生成并核查过的概念资料（Agent、大模型的上下文、Skill 及三者关系）。
3. **作为后续课程项目的基础**：可持续往里新增概念资料与新的个人 Skill。

---

## 二、目录结构

```
big-data-and-ai/
├── .workbuddy/
│   └── skills/
│       ├── concept-learner/          # ⭐ 项目级「概念学习资料生成 Skill」（作业核心）
│       │   ├── SKILL.md              #    技能说明书（含 name/description、流程、自检）
│       │   ├── references/source-policy.md
│       │   └── assets/learning-template.html
│       └── agent-skill-101/          # 早期实验：讲解“Agent Skill”这个概念的示例技能（非本次核心）
├── learning-materials/               # ⭐ 学习成果（由 concept-learner 生成并人工核查）
│   ├── agent.html                    #    概念 1：AI Agent（智能体）
│   ├── llm-context.html              #    概念 2：大模型的上下文
│   ├── skill.html                    #    概念 3：Skill（智能体技能）
│   └── concept-relationship.html     #    三者关系说明
├── hello.py                          # 早期课程示例
├── agent-skill-guide*.html           # 早期实验产物（教学 HTML，非本次作业交付）
├── README.md
└── .gitignore
```

> 说明：`agent-skill-101` 与 `agent-skill-guide*.html` 是我早期学习「Agent Skill」概念时做的实验性技能与页面。
> 本次作业的核心是 `concept-learner`（通用概念学习引擎）与 `learning-materials/`（三份概念资料 + 关系说明）。

---

## 三、项目级 Skill 的存放路径

- **项目级 Skill 位置**：`.workbuddy/skills/concept-learner/`（仓库根目录的 `.workbuddy/skills/`，随 git 共享）。
- **入口文件**：`.workbuddy/skills/concept-learner/SKILL.md`，顶部 YAML 含 `name` 与 `description`。
- **技能定位**：能接收**任意新概念**（不限于本仓库三个），按统一 9 板块结构产出学习资料，并强制遵守“来源可核查、个人理解与权威结论分开、交付前自检”。

---

## 四、如何在 WorkBuddy 中调用这个 Skill

当 WorkBuddy 在这个仓库目录下工作时，项目级 Skill 会被自动发现。调用方式：

1. 在对话中自然表达学习意图，例如：
   - “帮我学一下 **Agent** 这个概念”
   - “用概念学习 skill 帮我搞懂 **大模型的上下文**”
   - “调用 concept-learner，学习一下 **Skill**”
2. 命中 `description` 后，WorkBuddy 会加载 `SKILL.md`，按其中“9 板块结构 + 可视化图解 + 联网核查来源 + 自检”的流程执行。
3. 产物会保存到 `learning-materials/<概念>.html`（可改文件名与格式）。

也可以让我直接引用该 Skill 的名字来显式触发。生成任何新概念时，建议**人工阅读并核查**结果后再提交（来源不得伪造、概念不得整段照搬）。

---

## 五、已生成的学习资料（并已人工核查）

| 文件 | 主题 | 核心内容 |
|------|------|---------|
| `learning-materials/agent.html` | AI Agent（智能体） | 通俗解释、LLM+工具+指令/记忆+编排循环、订票场景、与聊天机器人的区别 |
| `learning-materials/llm-context.html` | 大模型的上下文 | 上下文窗口=有限工作记忆、内含组成、越大≠越好、对话压缩/RAG |
| `learning-materials/skill.html` | Skill（智能体技能） | 目录结构、SKILL.md、三级渐进式披露、个人 vs 项目级 |
| `learning-materials/concept-relationship.html` | 三者关系 | 上下文影响 Agent 的表现、Skill 沉淀可复用任务知识、关系图与工作流 |

---

## 六、AI 使用情况与人工核查、修改记录

本仓库内容大量借助 AI 完成，但我对每一份成果都做了人工阅读与核查，主要动作如下：

1. **来源核查**：所有概念资料标注的 URL，均由 AI 联网搜索后我再抽查确认真实可达、来源正当（官方文档/开源教材/权威技术博客）；**未使用任何凭空捏造的链接**。对无法确证的表述，我标为“个人理解，待核”。
2. **辅助理解在场**：每份资料都有“💡 一个类比 / ✅ 核查说明（人工）”块，与权威结论明确区分，避免整段照搬 AI 输出。全文统一使用第三人称客观表述，不出现“我 / 我的”等第一人称。
3. **内容方向核对**：我对 Agent、上下文、Skill 三份资料的核心表述，与多个独立来源交叉比对后采信（详见各页“核查说明”）。
4. **结构自检**：按 Skill 中定义的自检清单核对 9 板块齐全（含可视化图解）、来源可点、无敏感信息后再提交。
5. **一次纠错记录**：在早期开发 HTML 学习页时，发现并修复了“判分把未选中项当错误”的逻辑 bug——教训是：规则类交互应先做逻辑自测再交付，本仓库的 Skill 已把“交付前自检”写进规范。

> 诚实说明：本仓库不是“纯手工”资料，而是**AI 辅助产出 + 我人工核查把关**的成果；这也正是本作业对“AI 使用规范”的回应——善用 AI 但不盲信，出自我手、来源可查。

---

## 七、版本与安全

- 本仓库已用 git 管理并 **push 到 GitHub**（见提交历史），保持公开可访问。
- 已配置 `.gitignore`，**排除** API Key、密码、`.env`、密钥、个人隐私等敏感文件。
- 请勿向本仓库提交任何敏感凭据；如需存密钥，应放到仓库外的私有位置。
