---
name: skill-optimizer
description: 诊断并优化表现不佳的 Agent Skill。当用户反馈某个 skill 效果变差、加入大量参考资料后效果反而不如从前、评测显示 skill 输给更简单的竞品、核心目标达成率低/无效输出多，或需要给 skill 瘦身/重构/提升质量、做两版 skill 的 A/B 对比评估时使用此 skill。覆盖知识冗余、上下文超载、范围锁死、编排税、渐进式披露、条目改造、评估闭环等优化方向。
agent_created: true
---

# Skill 质量诊断与优化

对已有 skill 执行系统性诊断与重构。核心原则：skill 效果差不取决于装了多少知识，而取决于两件事——每次运行有多少"对的知识"以"对的形态"进入注意力窗口，以及指令设计有没有把模型锁死在错误的执行路径上。常见反直觉现象：内置大量领域规范的复杂 skill，评测发现率反而可能输给只有一份清单的简单 skill——知识是资产，但错误的交付形态会跟模型作对。

## 优化流程（按序执行，勿跳步）

### 第 0 步：基准评测（有数据则跳过）

没有数字就没有优化。若用户未提供评测数据，按 references/evaluation.md 构建最小 golden set：起步 2-3 个真实样本，跑 with-skill vs without-skill 双基线，全新会话隔离运行。核心目标达成（召回）与无效输出率必须分开度量。

### 第 1 步：盘点现状

机械检查交给脚本：

```bash
python scripts/skill_audit.py <目标skill目录>
```

脚本输出：frontmatter 合规性、description 触发质量（长度/触发词/反触发边界）、正文行数与 token 预算（红线 <500 行 / <5000 token）、references 体积与路由表存在性。在此基础上人工通读 SKILL.md 与全部资源文件，统计约束条目总数。

### 第 2 步：定位根因

对照 references/optimization-rulebook.md 的行为学诊断表，把评测症状映射到根因。五大根因常叠加：指令超载、知识冗余、行为模式劣化、范围锁死、编排税。诊断结论必须写明：命中哪几条根因，各自的证据是什么（SKILL.md 原文行号 + 评测数字）。未命中任何根因时，考虑问题出在 description 触发词或模型能力，勿强行套用本流程。

### 第 3 步：处方（一次只治一个病）

按 rulebook 处方表执行针对性重写，铁律：

- 每轮迭代只改评测数据里掉分最多的维度，改完重测
- 删除优先于添加：pass rate 平台期时先删指令再考虑加
- 推理式指令：写 "Do X because Y tends to cause Z"，不写 "ALWAYS X / NEVER Y"
- 保留被验证的编排：脚本产出的确定性数据照用——要砍的是让模型复述脚本输出的环节，不是脚本本身
- 改动前快照 `cp -r <skill> <skill>-snapshot-v<N>/`，支持回滚

知识提纯与条目改造细则见 references/rewrite-guide.md（四元组格式、路由表、两阶段执行模式、骨架模板）。跨生态编写最佳实践（Anthropic 官方/开放标准/社区实证，11 项深度调研）沉淀于 references/best-practices/——先读其 INDEX.md 按主题路由，按需读对应 JSON，勿全量载入。

### 第 4 步：结构重构

- SKILL.md 瘦身为四件事：工作流程 + 路由表 + 优先级框架 + 输出格式
- 详细知识移入 references/，按"触发特征"拆分，不按"学科"拆分
- 大 reference（>10k 词）加 grep 关键词索引；引用保持一层深；跨文件零重复——同一知识只住一处
- 目录按 scripts/（确定性代码）+ references/（按需文档）+ assets/（产出模板）组织
- description 重写：为模型而非人类写（何时触发+做什么+触发词），并加 When NOT to use 边界

### 第 5 步：评估闭环

任何改动未经评估不得宣称完成。按 references/evaluation.md 四指标做 A/B：核心目标召回/达成率 > 无效输出率 > 低价值条目占比 > 输出长度（指标名按 skill 领域自适应：评审类=缺陷召回率/误报率，写作类=需求覆盖率/跑题率，其余类推）。触发质量单独测（should-trigger / should-not-trigger）。评估不通过则回滚。

### 第 6 步：沉淀 gotchas

把本轮确认的失败模式写回目标 skill 的 Gotchas 区（没有就建一个）——Anthropic 实证：这是任何 skill 里信号密度最高的内容。同时把可复用的教训记入本 skill 的 case 文件。发布前按 optimization-rulebook.md 的「最佳实践合规清单」逐项核对，不通过项回填对应处方。

## 硬性红线

- 单次运行进入上下文的约束条目控制在 50 条以内；SKILL.md 正文 <500 行
- 不向 skill 添加"模型本来就知道"的解释性内容
- 优化前后各保留一版快照，支持回滚
- 全程祈使句写作；description 用第三人称并写明触发场景
- 不臆造评测数据；诊断结论必须可追溯到原文或数字
