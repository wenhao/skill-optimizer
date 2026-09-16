# 优化规则手册（Rulebook）

每条规则 = 证据 + 症状 + 处方。诊断时逐条核对，结论必须绑定证据（SKILL.md 原文行号或评测数字）。

来源标注：[AO] = Anthropic 官方/实证（2025-2026，详见 references/best-practices/，入口 INDEX.md）；[CP] = 社区一手实践；[SR] = 学术研究（Lost in the Middle 等）。

## 认知层根因

### RB-01 指令遵循非线性衰减 [SR+AO]

- 证据：模型可靠遵循的约束约 5-7 条量级，之后合规率急剧下降——12 条规则的违规数常多于 6 条规则；lost in the middle：长上下文中部注意力系统性低于首尾；context rot：填充率 >50% 后多事实推理退化、>75% 后仅剩召回
- 症状：规范明确写了的要点被遗漏；小输入尚可、大输入崩坏
- 处方：单次加载约束 ≤50 条（硬上限），理想 5-15 条；关键指令放开头结尾；长文件中部只放被动查阅的参考材料

### RB-02 知识冗余（模型已内化的通用知识）[AO]

- 证据：Anthropic 原则"只添加模型不知道的上下文，默认假设模型已经很聪明"；Don't state the obvious——复述默认行为只加上下文不加价值；研究显示"看似相关实则冗余"的内容比等量无关内容更伤准确率
- 症状：加了参考资料后反而变差；SKILL.md 存在大量"这不是常识吗"条目
- 处方：逐条增量测试（给"懂领域但不懂本组织"的资深从业者看："哦原来你们不这么做"→保留；"这不是常识吗"→删除）；只留四类增量：组织特有约束、与业界默认相反的规定、自研工具用法、历史事故禁令；经验值：内容密集型 skill 提纯后可删 60-80%

### RB-03 行为模式劣化（checklist 诱发浅层执行）[AO+CP]

- 证据：大 checklist 使模型从"深度推理"切换为"规则匹配打分"，产出容易命中的表层条目挤占高价值发现；表现为输出更长但更浅
- 症状：低价值条目（格式/命名类）占比 >50%；对照组（无清单版）反而发现更多逻辑/安全问题
- 处方：两阶段执行——Pass 1 不加载任何规范做自由深度推理产出候选，Pass 2 只加载路由命中项做定向核对；P2 类（风格）合并汇总不逐条展开

## 设计层根因

### RB-04 范围锁死（railroading 的范围变体）[AO]

- 证据：Anthropic《Lessons from building Claude Code》反 railroading 原则——指令过死剥夺模型因地制宜的能力；工具设计同理：应让 agent 追求多种有效策略而非单一路径
- 症状：输出范围被输入范围锚定——输入范围外的问题/要点达成率显著偏低（如 diff 评审只报 diff 内问题但根因在 diff 外；写作 skill 只覆盖需求清单字面条目、漏掉隐含诉求；调研 skill 只引用用户给的资料）。评测集按"范围内/范围外"拆分时范围外得分塌陷
- 处方：①把"只看 X""一个不多一个不少"类硬边界改为"以 X 为主，范围外但相关的发现允许并鼓励上报"；②输出 schema 给范围外发现留字段位（引用字段允许指向输入之外的来源/文件，另加 inScope 标记区分）；③参考加载双通道——脚本/关键词 hint 只是起点，明示"hint 必然有遗漏，模型语义判断兜底"

### RB-05 编排税（orchestration tax）[AO+CP+实证案例]

- 证据：Claude Code 官方文档——skill 内容驻留上下文=持续 token 成本；上下文工程 n² 注意力预算——每个预载 token 挤占推理 token；实证（某代码评审 skill 案例）：复杂编排 skill 的范围内发现率（92.6%）反而低于简单 skill（98.9%），编排开销（多脚本调用链+status 表+多份参考加载）吃掉了本该用于分析任务本身的注意力
- 症状：简单版竞品全面胜出或持平；执行 transcript 显示模型大量轮次花在跑脚本、查表、加载文件而非分析任务本身
- 处方：①砍掉非必要脚本环节，status 处理表只留异常分支；②把"每步做完的标准"从复述脚本输出改为检查产出物（如"有输出文件即可，不必核对每个字段"）；③参考加载体量与任务体量挂钩（小任务不触发全量参考）；④高价值确定性产出（脚本扫描/检索结果）保留——税在复述不在脚本

### RB-06 反触发缺失 [CP+AO]

- 证据：社区质量分析——加 When NOT to use 节是全榜最高杠杆编辑；装前检查也搜 "do not/skip/not for/out of scope" 判断作者是否想过误触发
- 症状：误报多；skill 在不该触发的场景被激活；与兄弟 skill 边界模糊互相抢触发
- 处方：description 与正文各加 When NOT to use；写明越界时改用哪个 skill；触发测试用 should-trigger/should-not-trigger 两组 prompt 实测

### RB-07 胖常驻层 [AO+CP]

- 证据：全部 skill 的 description 共享上下文窗口 1% 预算（回退上限 8000 字符）；每个未用 skill 的描述每轮占上下文；社区实证 3 个 skill 约 400 token，多装从未让输出更好
- 症状：token 异常；description 超长或写成了功能清单
- 处方：description ≤1024 字符且信息密度最大化（做什么+何时用+触发词+反触发）；装机量收敛，删从未触发的 skill

### RB-08 触发设计缺陷 [AO]

- 证据：description 是给模型看的触发判据而非摘要——Claude 启动时扫描全部 skill 描述决定"这个请求有没有对应 skill"
- 症状：该触发不触发（undertriggering）；不该触发乱触发
- 处方：description 含具体触发词与示例请求；Claude Code 可加 when_to_use；用 skill-creator 式 description tuning 实测命中率后迭代

## 结构与合规层根因

### RB-09 结构与文件组织缺陷 [AO]

- 证据：Anthropic 官方最佳实践——skill = 目录（SKILL.md + scripts/references/assets 约定目录）而非单个 markdown；引用保持一层深、避免嵌套引用链；>10k 词的参考提供 grep 检索模式；确定性逻辑写进脚本（不进上下文直接执行），别写成给模型念的步骤
- 症状：references 互相嵌套引用、模型要连跳多跳才到内容；SKILL.md 里大段"怎么算"的过程性描述本可以是脚本；参考文件巨大无索引；frontmatter name 与目录名不一致、含大写/连续连字符（跨平台即报错）
- 处方：①目录按 scripts/（确定性代码）+ references/（按需文档）+ assets/（产出模板）组织；②引用链压平到一层深；③大参考加 grep 关键词索引（INDEX 路由）；④命名规范化：小写字母-数字-连字符、动宾式（verb-ing-noun）、与目录名一致

### RB-10 跨平台 frontmatter 不合规 [标准]

- 证据：agentskills.io 开放标准（2025-12，26+ 平台采用）frontmatter 仅 6 字段：name、description、license、compatibility、metadata、allowed-tools（实验性）；Claude Code 私有扩展字段（when_to_use/context/agent/paths 等）在 claude.ai 上传、Skills API、package_skill 打包时硬报错拒绝；非标准字段是打包硬失败的头号原因
- 症状：skill 只在单一平台可用；打包/上传报 "Unexpected key(s) in SKILL.md frontmatter"
- 处方：跨平台分发的 skill 只用标准 6 字段，平台扩展字段放条件分发或构建期剥离；用官方 skills-ref validate CLI 校验；描述写法遵循 description（做什么+何时用+触发词，≤1024 字符、关键用例放最前——列表场景 1536 字符截断）

### RB-11 组合膨胀（缺 manifest 模式）[AO+CP]

- 证据：社区与官方高级模式共识——"manifest 而非 manual"：父 skill 只做索引（<100 行），内容下沉叶子文件按需加载；fork 型子代理看不到主会话上下文，指令必须自足；组合靠按名称引用而非复制粘贴内容
- 症状：单个 skill 长到必须全量加载才可用；多个 skill 间大段重复内容（同一知识住多处，改一处漏三处）；fork 运行后子代理空转返回
- 处方：①父级瘦身成索引/路由表，知识下沉叶子；②跨 skill 重复内容抽成单一来源按名称引用——信息只住一处；③fork 型 skill 的指令写自足（含输入约定与完成判据），纯指南型内容不要 fork

## 症状→根因速查表

| 评测症状 | 优先怀疑 | 次要怀疑 |
|---|---|---|
| 范围外目标达成率低 | RB-04 范围锁死 | RB-01、RB-05 |
| 范围内目标达成率也低 | RB-05 编排税 | RB-01、RB-03 |
| 漏掉规范明确写了的 | RB-01 指令衰减 | RB-02（被冗余稀释） |
| 输出长而浅、nitpick 多 | RB-03 浅层执行 | RB-02 |
| 误报多 | RB-06 反触发缺失 | RB-04（边界过宽） |
| 简单竞品全面胜出 | RB-05 编排税 | RB-02+RB-01 叠加 |
| token 异常高 | RB-07 胖常驻层 | RB-05（参考过载） |
| 该触发不触发 | RB-08 触发缺陷 | RB-06 |
| 加资料后反而变差 | RB-02 知识冗余 | RB-01+RB-03 |
| 引用链深/参考成死资产 | RB-09 结构缺陷 | RB-05 |
| 打包/跨平台上传报错 | RB-10 frontmatter 不合规 | — |
| 多 skill 大段重复/fork 空转 | RB-11 组合膨胀 | RB-02（重复即冗余） |

## 最佳实践合规清单（优化完成后发布前核对）

逐项核对，不通过项回填对应 RB 处方。细节溯源 references/best-practices/（先读其 INDEX.md）：

- [ ] frontmatter：name 小写连字符、与目录名一致、无保留词；description ≤1024 字符且含触发场景与关键词（RB-09/10）
- [ ] 跨平台分发仅用标准 6 字段，平台扩展字段已剥离或有条件分发（RB-10）
- [ ] SKILL.md 正文 <500 行 / <5000 token，开头结尾放关键指令（RB-01）
- [ ] 单次运行进入上下文的约束条目 ≤50 条（RB-01）
- [ ] references 按"触发特征"拆分、路由表存在、引用一层深、>10k 词文件有 grep 索引、跨文件零重复（RB-09/11）
- [ ] 确定性逻辑已脚本化，正文无复述脚本输出的环节（RB-05/09）
- [ ] description 与正文均有 When NOT to use 反触发边界（RB-06）
- [ ] 无"模型本来就知道"的通用知识（RB-02）
- [ ] 有 evals/：with/without 双基线 + should-trigger/should-not-trigger 各至少 2 例（evaluation.md）
- [ ] 有 Gotchas 区且为本轮确认的失败模式（SKILL.md 第 6 步）

## 处方优先级（按投入产出比）

1. 删通用知识（RB-02）——零风险高收益，通常可删 60-80%
2. 加 When NOT to use + 反触发（RB-06）——单点编辑最高杠杆
3. 解除范围锁死（RB-04）——改几条硬边界语句+输出 schema 留位
4. 两阶段执行（RB-03）——Pass1 自由推理 + Pass2 定向核对
5. 砍编排税（RB-05）——砍环节不砍脚本
6. 结构重构与路由表（提纯后做，避免提前优化）

## 排除项（不属于本手册范畴，先排查再进流程）

- skill 从未被触发 → description 缺触发词（RB-08 单独处理）
- 触发了但完全没执行 → 正文指令含糊或与模型默认行为冲突
- 仅输出格式错误 → 输出模板缺失或前后矛盾，改模板即可

## 证据来源

- Anthropic：《Lessons from building Claude Code: How we use skills》(2026-06)、《Writing effective tools for agents》(2025-09)、Agent Skills 开放规范与评估指南（agentskills.io）、Claude Code Skills 官方文档
- 学术研究：UC Berkeley "Lost in the Middle" (2023)、Together AI 指令遵循研究、context rot 相关长上下文研究
- 社区实践：Claude skill 质量分析（claudskills 等）、机构一手实践（mrktcorrect 等）
