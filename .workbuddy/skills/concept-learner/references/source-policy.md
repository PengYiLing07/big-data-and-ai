# 资料来源纪律（Source Policy）

本文件是 concept-learner 生成资料时关于“来源”的硬性规范。作业与评分都强调**来源可核查、不得伪造**，故把纪律单独成文。

## 一、什么是“可信来源”（可写进资料）

按可靠性从高到低：

1. **官方文档/厂商一手文档**：如 Claude 官方 Agent Skills 文档（platform.claude.com）、Claude 官方博客（claude.com/blog）、WorkBuddy 文档（workbuddy.cn/docs）、OpenAI/Google 文档等。
2. **学术教材/权威课程**：如《Artificial Intelligence: A Modern Approach》（AIMA）、DataWhale 开源教材（GitHub）、斯坦福/吴恩达课程等。
3. **知名技术博客/工程文档**：AWS Labs、Redis 官方博客、DataCamp、知名 AI 术语表等对概念的严谨讲解。
4. **政府/行业标准化文件**：如《国家人工智能产业综合标准化体系建设指南》相关解读。

## 二、禁止事项

- ❌ 不得**编造** URL、书名、作者、引文。
- ❌ 不得把 AI 随口生成的“来源”当真实出处写进资料。
- ❌ 不得整段照搬某篇 AI 对话/某博客文字冒充原创（可作为引用并注明出处）。
- ❌ 不得把无出处、查无实据的说法写成事实。

## 三、操作要求（每次生成前）

1. 对概念 X，先用网络搜索/抓取核实定义与机制，记录真实来源 URL。
2. 每条“权威结论”在资料第 7 板块给出可点链接。
3. 无法核实的 → 标“（个人理解，待核）”，不冒充权威。

## 四、区分“权威结论”与“个人理解”

- **权威结论**：来自上述可信来源，正文可写，来源附链接。
- **个人理解/类比/判断**：你自己的话，是加分项，但要用“我的理解”“可类比为……”等措辞与权威结论区分，让读者知道哪句是出处、哪句是你发挥。

## 五、本仓库已用到的来源（示例，供后续资料风格参考）

- **Agent（智能体）**：
  - 鹤壁市科技局科普《AI 智能体技术》（大脑/感知/行动三模块）— kjj.hebi.gov.cn
  - DataWhale《Hello-Agents》（GitHub 开源，引用 AIMA）— github.com/datawhalechina/Hello-Agents
  - DataCamp AI Agents Cheat Sheet — datacamp.com
- **大模型上下文（Context / Context Window）**：
  - Redis 官方博客 LLM context windows — redis.io/blog
  - AWS Labs 生成式 AI Atlas「Model Context and Memory」— awslabs.github.io
- **Skill（Agent Skill）**：
  - Anthropic Claude 官方文档 Agent Skills — platform.claude.com/docs
  - Claude 官方博客《Equipping agents for the real world with Agent Skills》— claude.com/blog
