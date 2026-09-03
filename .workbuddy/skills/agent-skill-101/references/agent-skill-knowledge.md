# Agent Skill（技能）核心知识库

> 本文档是 `agent-skill-101` 技能的知识底座。凡产出"Agent Skill 是什么"的学习材料，内容与"来源标注"必须以此为准。
> 每条知识点末尾的 **来源** 是给学习者看的真实链接/可核查位置，必须原样保留在交付物中。

---

## 一、概念：Skill 是什么

**一句话定义**
Skill（技能 / Agent Skill）是打包好的"能力扩展包"，让 AI 在面对特定任务时，不需要从零摸索，而是**读一份自带说明书（SKILL.md）**，按里面的流程和知识去执行。它像给新员工的一份"实习生上手手册"。

**类比**
> 普通 AI 像"有经验但没看过贵司文档的新员工"；加载了 Skill 的 AI 像"拿到部门 SOP 手册后上岗"的员工——知道规矩、流程、坑在哪。

**来源**
- WorkBuddy 官方文档（能力总览）：https://www.workbuddy.cn/docs/workbuddy/Overview
- skill-creator 技能（如何造技能的权威说明书）：见本机 `workbuddy-builtin/skills/skill-creator/SKILL.md`

---

## 二、一个 Skill 的内部结构

```
技能名/
├── SKILL.md            必填：技能说明书 + YAML 元信息
└── 可选资源
    ├── scripts/        可执行代码（Python/Shell，确定性任务）
    ├── references/     参考资料（按需加载进上下文的长文档）
    └── assets/         输出用素材（模板/图片/字体，不读进上下文）
```

**要点**
- `SKILL.md` 是**唯一强制文件**，其余按需取舍（不是每个技能都需要三类资源）。
- `scripts/` 里的脚本可被直接执行、**不占上下文**；`references/` 是"用到才读"的说明；`assets/` 是"复制去用"的产物。

**来源**
- skill-creator 技能 · "Anatomy of a Skill" 章节：见本机 `workbuddy-builtin/skills/skill-creator/SKILL.md`
- 真实实例：内置技能 `expert-manager/`、`wb-finance-skill/` 等，其 `references/`、`scripts/` 目录结构可直接查看核对。

---

## 三、SKILL.md 的 YAML frontmatter（必填元信息）

```yaml
---
name: 技能名
description: |
  一句话说明"这个技能做什么、什么时候该用"。
  触发词：……、……。
---
```

**要点**
- `name`（技能名）与 `description`（说明）**必填**。
- `description` 决定**何时触发**——写清楚场景与触发词，AI 才能在对的时刻加载它。
- 由 AI 自建的技能需标注 `agent_created: true`，以便后续可被修改/删除。

**来源**
- skill-creator 技能 · Metadata / Agent-Created 章节：见本机 `workbuddy-builtin/skills/skill-creator/SKILL.md`
- 真实实例 frontmatter：见本机 `workbuddy-builtin/skills/expert-manager/SKILL.md` 顶部

---

## 四、三级加载机制（Progressive Disclosure）

Skill 用"渐进式披露"节省上下文（AI 的"脑容量"），分三级：

| 级别 | 内容 | 何时进入上下文 |
|------|------|--------------|
| 1. 元数据 | `name` + `description`（约百字） | **始终常驻** |
| 2. SKILL.md 正文 | 操作流程与指引（宜 <5k 词） | 技能被触发时 |
| 3. 资源 | scripts / references / assets | 按需才加载 |

**要点**
- 越常用的信息越往前放；海量细节放资源层，**用到才读**，不占日常上下文。
- SKILL.md 保持精简，详细参考放 `references/`，是这套设计的核心原则。

**来源**
- skill-creator 技能 · "Progressive Disclosure Design Principle"：见本机 `workbuddy-builtin/skills/skill-creator/SKILL.md`

---

## 五、Skill 的使用流程（触发到沉淀）

1. **扫描**：AI 每次收到请求，先比对已装技能列表。
2. **触发**：请求与某个技能的 `description` 匹配 → 加载该技能。
3. **取用**：读 SKILL.md（必要时再读其 references/scripts）。
4. **执行**：按说明里的流程与脚本完成任务。
5. **沉淀（可选）**：完成任务后，若发现可复用方法，可沉淀成**新技能**或**更新旧技能**，供下次复用。

**来源**
- WorkBuddy 官方文档（Agent 执行模型 / 能力扩展）：https://www.workbuddy.cn/docs/workbuddy/Overview
- 系统级 Agent Skill 加载规范（本会话运行规则）

---

## 六、为什么要给学习者"标注来源"

- 保证知识**可核查**：学习者能回链到权威出处，而非轻信转述。
- 利于**持续跟进**：文档/规范会更新，有链接才能看最新版。
- 区分**定义性事实**（来自官方/说明书）与**操作性建议**（来自实践），让学习者知道深浅。

**来源**
- 本知识库设计约定（`agent-skill-101` 技能自身规范）

---

## 七、引用来源时应遵守

- 能给出**可点开的 URL** 就给 URL（如官方文档）。
- 对**本机权威文件**（内置技能），标注真实路径并说明"可在本机查看核对"。
- 每个知识点至少给 1 个来源；不确定的出处在材料中标注"（实践建议，非官方定论）"。
- 禁止编造不存在的文档 URL；无法确认就只给已知入口。

**来源**
- 本知识库设计约定（`agent-skill-101` 技能自身规范）
