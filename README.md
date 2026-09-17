# big-data-and-ai · 大数据与人工智能 个人课程仓库

本仓库是「大数据与人工智能」课程的个人学习仓库，同时作为个人作品集的工具基础。
它既保存了**可复用的技能（Skill）**，也保存了**由这些技能生成、并经人工核查的学习资料**。

---

## 一、仓库用途

1. **沉淀可复用的学习工具**：仓库内的项目级技能（`concept-learner`）能接收任意新概念，自动产出一份结构完整、可核查的概念学习资料；`git-push-repo` 负责把本仓库的改动安全地提交并推送到远端。
2. **保存经过人工核查的学习成果**：`learning-materials/` 下存放已生成并核查过的概念资料。
3. **保存学习路线与课程脚本**：根目录的两份《Python 学习地图》说明「什么时候学什么」，`scripts/` 下存放课堂练习与自检脚本。
4. **作为后续课程项目的基础**：可持续往里新增概念资料与新的个人技能。

---

## 二、目录结构

```
big-data-and-ai/
├── .workbuddy/
│   └── skills/
│       ├── concept-learner/          # ⭐ 项目级「概念学习资料生成 Skill」
│       │   ├── SKILL.md              #    技能说明书（含 name/description、流程、自检）
│       │   ├── references/source-policy.md
│       │   └── assets/learning-template.html
│       ├── git-push-repo/            # ⭐ 项目级「提交并推送」Skill（带敏感文件门禁）
│       │   ├── SKILL.md
│       │   ├── scripts/git_flow.py
│       │   ├── references/{remotes,troubleshooting}.md
│       │   └── assets/gitignore-template.txt
│       └── agent-skill-101/          # 早期实验：讲解“Agent Skill”这个概念的示例技能
├── learning-materials/               # ⭐ 学习成果（由 concept-learner 生成并人工核查）
│   ├── index.html                    #    目录页：概念分布、前置依赖表、跨课复用表
│   ├── _concepts.json                #    17 个概念的结构化清单（含前置 / 后继 / 所属板块）
│   ├── variables-and-data-types.html #    Python 基础 17 页（第 1–13 课 + 选修 + 结课实践）
│   ├── strings-and-text.html
│   ├── booleans-and-conditionals.html
│   ├── lists.html · loops.html · dictionaries-and-sets.html · comprehensions.html
│   ├── functions.html · file-io-and-encoding.html · exceptions.html · modules-and-packages.html
│   ├── regular-expressions.html · numpy-and-vectorization.html
│   ├── pandas-dataframe.html · matplotlib-basics.html
│   ├── text-analysis-project.html · classes-and-objects.html
│   ├── agent.html                    #    AI 概念 5 页（早期资料，目录页「拓展阅读」已收录）
│   ├── llm-context.html · skill.html · concept-relationship.html · context-window.html
├── Python学习地图_13次课版.html / .md  # ⭐ 13 次课教学路线（新闻学专业定制）
├── Python学习地图_新闻学专业版.html/.md # ⭐ 早期 4 课时版路线
├── scripts/
│   ├── 01.py                         # 第 1 课：环境自检脚本（可运行，打印版本 / 解释器 / pip 源）
│   ├── 01.ipynb                      # 第 1 课：Jupyter 练习（自带执行输出）
│   └── quiz_selftest.js              # 自测判分逻辑的离线校验脚本（node 运行）
├── hello.py                          # 早期课程示例
├── agent-skill-guide*.html           # 早期实验产物（教学 HTML）
├── README.md
└── .gitignore
```

> 说明：`agent-skill-101` 与 `agent-skill-guide*.html` 是早期学习「Agent Skill」概念时做的实验性技能与页面。
> `concept-learner` 是通用概念学习引擎；`git-push-repo` 是本仓库的提交推送工具。
> `learning-materials/` 下的资料按主题分两批：前 17 页对应 Python 基础 13 次课，后 5 页为早期 AI 概念资料。

---

## 三、项目级 Skill 的存放路径

- **项目级 Skill 位置**：`.workbuddy/skills/`（仓库根目录下，随 git 共享）。
- **入口文件**：各技能目录下的 `SKILL.md`，顶部 YAML 含 `name` 与 `description`。
- **技能清单**：
  | 技能 | 定位 |
  |---|---|
  | `concept-learner` | 通用概念学习引擎。接收任意新概念，按统一 9 板块结构产出学习资料，并强制遵守「来源可核查、辅助说明与权威结论分开、交付前自检」。 |
  | `git-push-repo` | 本仓库的提交与推送流程。含敏感文件门禁（`.env`、密钥默认阻断）、大文件告警、非快进被拒时的 `--pull-rebase` 处置；不提供任何强推或改写历史的自动命令。 |
  | `agent-skill-101` | 早期实验技能，用于讲解「Agent Skill」这个概念本身。 |

---

## 四、如何在 WorkBuddy 中调用这些技能

当 WorkBuddy 在这个仓库目录下工作时，项目级技能会被自动发现。调用方式：

1. 在对话中自然表达意图，例如：
   - “帮我学一下 **Agent** 这个概念”
   - “用概念学习 skill 帮我搞懂 **大模型的上下文**”
   - “调用 concept-learner，学习一下 **模块与包**”
   - “把这次改动提交并推送到 GitHub”
2. 命中 `description` 后，WorkBuddy 会加载对应 `SKILL.md`，按其流程执行。
3. 概念资料的产物保存到 `learning-materials/<概念>.html`；推送走 `git-push-repo` 的 `check` → `push`。

也可以直接引用技能名来显式触发。生成任何新概念时，建议**人工阅读并核查**结果后再提交（来源不得伪造、概念不得整段照搬）。

---

## 五、已生成的学习资料（并已人工核查）

### 5.1 Python 基础（17 页，对应 13 次课）

| 板块 | 概念页 | 主题要点 |
|------|------|---------|
| 一 · Python 起步（第 1–3 课） | `variables-and-data-types.html` | 赋值是贴标签；str / int / float / bool 与转换 |
| | `strings-and-text.html` | 索引切片、split / join / strip / replace、f-string |
| | `booleans-and-conditionals.html` | 比较运算、if / elif / else、and / or / not |
| 二 · 循环与容器（第 4–6 课） | `lists.html` | 增删改查、索引切片、sort 与 sorted |
| | `loops.html` | for / while、range、enumerate、break / continue |
| | `dictionaries-and-sets.html` | 键值映射与去重、get / setdefault、词频统计 |
| | `comprehensions.html` | 列表与字典推导式 |
| 三 · 函数与工程化（第 7–9 课） | `functions.html` | def、参数与返回值、作用域、docstring |
| | `file-io-and-encoding.html` | open / with、读写 txt 与 CSV、utf-8 与 gbk |
| | `exceptions.html` | try / except / else / finally、读懂报错栈 |
| | `modules-and-packages.html` | import 机制、`__name__`、包与 `__init__.py`、pip 与虚拟环境 |
| 四 · AI 前置数据能力（第 10–13 课） | `regular-expressions.html` | 元字符、字符类、量词、分组清洗 |
| | `numpy-and-vectorization.html` | ndarray、形状与维度、广播、向量化 |
| | `pandas-dataframe.html` | 读写 CSV / Excel、筛选排序、缺失值、groupby |
| | `matplotlib-basics.html` | 直方图 / 柱状图 / 折线图与中文乱码 |
| 选修与综合 | `classes-and-objects.html` | 读懂 class：属性、方法、实例化 |
| | `text-analysis-project.html` | 清洗 → 统计 → 分组 → 出图的完整流水线 |

### 5.2 AI 概念（5 页，早期资料）

| 文件 | 主题 | 核心内容 |
|------|------|---------|
| `learning-materials/agent.html` | AI Agent（智能体） | 通俗解释、可视化图解（组成结构/分界对比/执行流程）、LLM+工具+指令/记忆+编排循环、订票场景、与聊天机器人的区别 |
| `learning-materials/llm-context.html` | 大模型的上下文 | 通俗解释、可视化图解（内容构成/容量误区/信息取舍）、上下文窗口=有限工作记忆、内含组成、越大≠越好、对话压缩/RAG |
| `learning-materials/skill.html` | Skill（智能体技能） | 通俗解释、可视化图解（目录结构/三级披露/与Prompt对比）、SKILL.md、三级渐进式披露、个人 vs 项目级 |
| `learning-materials/concept-relationship.html` | 三者关系 | 上下文影响 Agent 的表现、Skill 沉淀可复用任务知识、关系图与工作流 |
| `learning-materials/context-window.html` | 上下文窗口（拓展） | 输入与输出共享预算、token 粒度、位置 U 型曲线、context rot、标称≠有效窗口、RAG 精排 |

---

## 六、AI 使用情况与人工核查、修改记录

本仓库内容大量借助 AI 完成，但每一份成果都经过人工阅读与核查，主要动作如下：

1. **来源核查**：所有概念资料标注的 URL，均在 AI 联网搜索后由人工抽查确认真实可达、来源正当（官方文档/开源教材/权威技术博客）；**未使用任何凭空捏造的链接**。对无法确证的表述，标注为“待核”。
2. **辅助理解在场且克制**：每份资料都有“💡 一个类比 / ✅ 核查说明（人工）”块，与权威结论明确区分。全文统一第三人称客观表述，不出现“我 / 我的”等第一人称；类比用陈述句而非命令句，读者指称用“用户/读者”而非通篇“你”，判断句用“通常/常见误解是”，尽量减少主观色彩。
3. **内容方向核对**：各页核心表述与多个独立来源交叉比对后采信（详见各页“核查说明”）。以 `modules-and-packages.html` 为例，模块定义、`__init__.py` 的作用、搜索路径构成与同名遮蔽、`__name__` 与相对导入的关系，分别核对 Python 官方教程第 6 章、官方文档《`__main__`》、PEP 328 与 Python 打包用户指南。
4. **示例代码实跑验证**：`modules-and-packages.html` 第六节的应用场景代码，先在临时目录以 `news_tools` 包的形式实际运行通过（`python -m news_tools` 输出与页中记录一致），页面定稿后又从 HTML 中反抽代码重跑一次；同时保留对照组证据——直接执行包内模块会报 `ImportError: attempted relative import with no known parent package`。`scripts/01.py` 与 `scripts/01.ipynb` 同样经过实跑。
5. **结构自检**：按 Skill 中定义的自检清单核对 9 板块齐全（含可视化图解）、来源可点、无敏感信息后再提交；自测题的判分逻辑用 `scripts/quiz_selftest.js` 离线校验（全对得满分、全错得 0 分、单选错判定正确）。目录页的站内链接做过全量断链检查。
6. **一次纠错记录**：在早期开发 HTML 学习页时，发现并修复了“判分把未选中项当错误”的逻辑 bug——教训是：规则类交互应先做逻辑自测再交付，本仓库的 Skill 已把“交付前自检”写进规范。另一次修正是目录页的状态标记：17 页全部生成完成后，把原先的“生成中”标记统一更正为“已生成”，避免索引与实际文件状态不一致。

> 诚实说明：本仓库不是“纯手工”资料，而是**AI 辅助产出 + 人工核查把关**的成果；这也正是本作业对“AI 使用规范”的回应——善用 AI 但不盲信，人为主导、来源可查。

---

## 七、版本与安全

- 本仓库已用 git 管理并 **push 到 GitHub**（见提交历史），保持公开可访问。
- 已配置 `.gitignore`，**排除** API Key、密码、`.env`、密钥、个人隐私等敏感文件。
- 提交与推送统一走 `git-push-repo` 技能：推送前先做体检（远端、分支、身份、变更、未推送提交）与敏感文件门禁；被拒时按提示 `--pull-rebase`，不使用强推。
- 请勿向本仓库提交任何敏感凭据；如需存密钥，应放到仓库外的私有位置。
