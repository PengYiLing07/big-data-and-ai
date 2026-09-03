/*
 * agent-skill-101 · 分层测验题库 (agent-skill-guide 复用数据源)
 * 难度分档：E 入门 / M 进阶 / H 挑战。每题含 [题干, 选项, 答案, 难度, 考点, 来源]。
 * 内容与来源严格取自 references/agent-skill-knowledge.md，不得改动事实与链接。
 * 判分注意：答案 answers 为数组，单选数组长度 1，多选可为多元素。比较时用排序后序列化。
 */
window.AGENT_SKILL_QUIZ = {
  version: "agent-skill-101-v1.0",
  startLevel: "E",
  maxQuestions: 12,          // 题数上限
  hardWinStreak: 2,          // H 档连续答对 2 题提前通关
  pityLimit: 3,              // E 档累计答错 3 次回炉提示
  order: ["E", "M", "H"],
  bank: {
    E: [
      {
        q: "在 Agent Skill（技能）目录中，哪个文件是【必须存在】的核心文件？",
        opts: ["assets/logo.png", "SKILL.md", "references/说明书.md", "scripts/run.py"],
        answers: ["B"],
        source: "skill-creator：Anatomy of a Skill — SKILL.md (required)。本机 workbuddy-builtin/skills/skill-creator/SKILL.md",
        note: "只有 SKILL.md 是强制文件，其余资源目录按需取舍。"
      },
      {
        q: "Skill 常被比喻成什么，用来帮助初学者理解它？",
        opts: ["一份股票财报", "一本小说", "一份『实习生上岗手册 / 部门 SOP』", "一张地图"],
        answers: ["C"],
        source: "agent-skill-101 knowledge 文档 · 概念类比。本技能 references/agent-skill-knowledge.md",
        note: "『实习生手册』能贴切说明：Skill 就是给 AI 的、写清流程与规矩的自带说明书。"
      },
      {
        q: "SKILL.md 顶部的 YAML frontmatter 中，哪两项是【必填】的元信息？",
        opts: ["name 和 description", "icon 和 author", "version 和 license", "tags 和 category"],
        answers: ["A"],
        source: "skill-creator：Metadata Quality — name/description required。本机 skill-creator/SKILL.md",
        note: "name=技能名，description=『做什么/何时用』，后者决定触发时机。"
      },
      {
        q: "Skill 的『三级加载 / 渐进式披露』中，哪一级是【始终常驻】在 AI 上下文里的？",
        opts: ["全部资源文件", "SKILL.md 正文", "元数据（name + description）", "scripts 脚本"],
        answers: ["C"],
        source: "skill-creator：Progressive Disclosure — 元数据 Always in context。本机 skill-creator/SKILL.md",
        note: "元数据仅约百字，最省『脑容量』，所以常驻。"
      }
    ],
    M: [
      {
        q: "description（技能说明）的主要作用是什么？",
        opts: ["显示给用户的装饰文字", "决定『何时触发』这个技能", "控制动画效果", "给文件排序"],
        answers: ["B"],
        source: "skill-creator：Metadata Quality — 描述决定何时被使用。本机 skill-creator/SKILL.md",
        note: "写清楚场景与触发词，AI 才能在对的时刻加载它。"
      },
      {
        q: "references/ 目录适合放什么类型的材料？",
        opts: ["可直接执行的程序", "用于最终输出的 logo/模板", "较长、『用到才读』的参考文档", "Git 忽略文件"],
        answers: ["C"],
        source: "skill-creator：references/ — 按需加载进上下文的长文档。本机 skill-creator/SKILL.md",
        note: "references 只在 AI 判定需要时才读，帮助 SKILL.md 保持精简。"
      },
      {
        q: "scripts/ 目录里的脚本有一个重要特性是？",
        opts: ["必须人工逐行阅读", "可以【直接执行】且不占用上下文窗口", "只能在联网时用", "不能保存为文件"],
        answers: ["B"],
        source: "skill-creator：scripts/ — 可执行、可被直接运行、Token efficient。本机 skill-creator/SKILL.md",
        note: "确定性任务放脚本里，AI 不必把代码读进上下文即可运行。"
      },
      {
        q: "三级加载的正确顺序是？",
        opts: ["资源 → SKILL.md → 元数据", "SKILL.md → 元数据 → 资源", "元数据 → SKILL.md → 资源", "只加载 SKILL.md，其余永不读"],
        answers: ["C"],
        source: "skill-creator：Progressive Disclosure 三级列表。本机 skill-creator/SKILL.md",
        note: "常驻元数据 → 触发读 SKILL.md → 按需读资源，层层递进省上下文。"
      }
    ],
    H: [
      {
        q: "你要为团队写一个『每次都要把 PDF 旋转 90°』的稳定脚本，它应放在技能的哪个目录？",
        opts: ["assets/", "references/", "scripts/", "直接写进 SKILL.md 正文"],
        answers: ["C"],
        source: "skill-creator：scripts/ 用途 + 实例 rotate_pdf.py。本机 skill-creator/SKILL.md",
        note: "确定性、重复写的代码放 scripts/，可直接执行省上下文。"
      },
      {
        q: "品牌视觉素材（logo、PPT 模板、字体）要在产出物里被复制使用，应放哪个目录？",
        opts: ["assets/", "references/", "scripts/", "SKILL.md"],
        answers: ["A"],
        source: "skill-creator：assets/ — 用于最终输出的模板/素材。本机 skill-creator/SKILL.md",
        note: "assets 用于『产物里直接用的文件』，不读进上下文。"
      },
      {
        q: "设计技能时，一份 8000 词的企业政策长文档，最佳做法是放在哪里？",
        opts: ["SKILL.md 正文里", "references/ 里，SKILL.md 只留简要指引", "复制进每题选项", "删除不要"],
        answers: ["B"],
        source: "skill-creator：Avoid duplication / references 最佳实践。本机 skill-creator/SKILL.md",
        note: "详细资料放 references 保持 SKILL.md 精简；真核心流程才留 SKILL.md。"
      },
      {
        q: "按本学习工具的『分层自适应』规则，当你在最高档 H 连续答对几题时可【提前通关】？",
        opts: ["1 题", "2 题", "5 题", "永远不能提前"],
        answers: ["B"],
        source: "本工具 quiz-engine.md 设计规则（非官方标准）。本技能 references/quiz-engine.md",
        note: "注意：此题考察的是学习工具的分层规则，非官方 Skill 特性——材料中已作标注。"
      }
    ]
  }
};
