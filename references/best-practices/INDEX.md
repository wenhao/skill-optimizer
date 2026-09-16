# INDEX — Skills 最佳实践路由表

> 用法：按需求场景定位文件，读对应 JSON 的相关字段。字段含义见 `fields.yaml`。更新日期：2026-09-16（例行核对 11 源，无实质新增；docs.claude.com 已迁移至 platform.claude.com）。

## 路由表

| 需求场景 | 文件（results/ 下） | 核心结论速览 |
|---|---|---|
| 写/改 SKILL.md 的基础规范 | `Anthropic_Agent_Skills_官方编写最佳实践.json` | 渐进式披露三层级（~100 token 元数据常驻 / 正文 <5000 token <500 行 / 资源按需）；description 是触发判据不是摘要；单一职责；引用一层深；name 与目录一致 |
| description 与触发设计 | `Claude_Code_Skills_实践.json`、`社区与市场实践.json` | 为模型而非人类写；关键用例放最前（1536 字符截断）；when_to_use / disable-model-invocation / user-invocable / paths 四层控制；无反触发边界（do not/skip/not for）的 skill 别用于生产 |
| 什么该做成 skill、怎么分类 | `Lessons_from_building_Claude_Code_How_we_use_skills.json` | 反复粘贴的流程或 CLAUDE.md 长成流程的节 → 抽成 skill；九大分类法（库参考/产品验证/数据分析/业务流程/脚手架/代码审查/CI-CD/Runbook/运维）；最好的 skill 干净归入一类；gotchas 区是信号密度最高的内容 |
| 文件与目录组织 | `anthropics_skills_官方仓库与_skill-creator_模板.json` | SKILL.md + scripts/（确定性代码，不进上下文）+ references/（按需文档，>10k 词给 grep 模式）+ assets/（产出资源）；信息只住一处 |
| Token 预算与上下文成本 | `Token_预算与上下文工程量化.json` | 找最大化期望结果概率的最小高信号 token 集；U 型注意力（关键指令放两端）；预载 vs 按需（JIT）成本模型；just-in-case 预载、肥 always-on 指令是反模式 |
| 通用上下文工程理论底座 | `通用上下文工程原则.json` | 上下文工程 = 设计 agent 运行的整个信息环境；长程三技术：压缩、结构化笔记、子代理；指令设计黄金区（勿硬编码勿纯高层） |
| 组合、子代理、动态注入 | `组合子代理执行与动态上下文注入.json` | manifest 而非 manual（父 skill 只做索引 <100 行，内容下沉叶子）；context:fork 隔离执行；!command 注入实时数据（claude.ai synced skill 不执行注入）；按名称引用组合；fork 型 skill 指令必须自足 |
| 测试与评估闭环 | `Skill_测试与评估闭环.json` | 该触发的有没有触发、触发后输出达不达标是两件事分开测；with/without 双基线、全新会话隔离；should-trigger / should-not-trigger 实测；delta 视角（多花 token 买到什么） |
| 工具接口设计（MCP/工具同源思想） | `Writing_effective_tools_for_agents_工程博客.json` | 宁缺毋滥；返回高信号字段而非技术标识符；合并多步链为单次调用；工具描述微小精炼可带来戏剧性改进（SWE-bench SOTA 案例） |
| 跨平台兼容与开放标准 | `Agent_Skills_开放标准_agentskills_io.json` | 2025-12-18 开放标准，26+ 平台；核心 = 目录 + SKILL.md；跨平台分发勿用非标准 frontmatter 字段（打包硬报错） |
| 选 skill / 装机策略 | `社区与市场实践.json` | 三个装前过滤器；装机 ≤3 个（超过可见降低质量）；避开 50 合 1 大礼包；管道安装（curl\|bash）是危险信号 |

## 跨文件关键数字（速查）

- 渐进式披露：元数据 ~100 token 常驻 / SKILL.md 正文 <5000 token、<500 行 / 资源按需无上限
- 父 skill（索引型）<100 行，内容下沉叶子
- 装机量 ≤3 个；单次加载约束条目 ≤50 条（skills-optimizer RB-01 同源）
- description/when_to_use 合计 1536 字符截断（Claude Code）
- auto-compaction 后 skill 重挂预算：每个保前 5000 token、合计 25000 token
- 好的测试断言：先跑一轮看输出再写断言；PASS 必须要证据

## grep 关键词表（按文件）

| 文件 | grep 关键词 |
|---|---|
| Anthropic_Agent_Skills_官方编写最佳实践 | progressive_disclosure, description_writing, anti_patterns |
| Claude_Code_Skills_实践 | trigger_design, frontmatter, context:fork, skillOverrides |
| Lessons_from_building_Claude_Code | taxonomy, degrees_of_freedom, railroading, gotchas |
| anthropics_skills_官方仓库 | file_organization, package_skill, description tuning |
| Token_预算与上下文工程量化 | U 型, attention sink, just-in-case, 黄金区 |
| 通用上下文工程原则 | compaction, structured note-taking, sub-agent, JIT |
| 组合子代理执行与动态上下文注入 | manifest, context:fork, !command, 叶子 |
| Skill_测试与评估闭环 | should-trigger, baseline, delta, LLM-as-judge |
| Writing_effective_tools_for_agents | affordance, 高信号, schedule_event, response_format |
| Agent_Skills_开放标准_agentskills_io | 开放标准, 26+, frontmatter 硬校验 |
| 社区与市场实践 | 安慰剂, 装机量, 反触发, em-dash-bouncer |
