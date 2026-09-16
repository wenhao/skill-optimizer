# skill-optimizer

诊断并优化表现不佳的 Agent Skill，适用于 Claude Code、ZCode 等支持 Agent Skills（SKILL.md 规范）的 AI 工具。

当某个 skill 出现以下症状时使用：效果变差、加入大量参考资料后反而不如从前、评测显示输给更简单的竞品、核心目标达成率低/无效输出多，或需要给 skill 瘦身、重构、做两版 skill 的 A/B 对比评估。

## 工作方式

按七步流程执行：基准评测 → 盘点现状（脚本审计）→ 定位根因 → 处方重写 → 结构重构 → 评估闭环 → 沉淀 gotchas。核心原则：skill 效果不取决于装了多少知识，而取决于每次运行有多少"对的知识"以"对的形态"进入注意力窗口。覆盖知识冗余、上下文超载、范围锁死、编排税、渐进式披露、条目改造、评估闭环等优化方向。

## 安装

本仓库即一个标准 skill 目录（根目录含 `SKILL.md`），克隆到目标工具的 skills 目录即可：

```bash
# Claude Code
git clone <repo-url> ~/.claude/skills/skill-optimizer

# 或作为项目级 skill
git clone <repo-url> .claude/skills/skill-optimizer
```

## 目录结构

```
skill-optimizer/
├── SKILL.md                      # 入口：优化流程 + 硬性红线（模型每次加载的主文档）
├── README.md                     # 面向人类的说明（加载器会忽略）
├── scripts/
│   └── skill_audit.py            # 确定性审计脚本：frontmatter、description、token 预算、references 体积
└── references/                   # 按需加载的文档（渐进式披露，不随 SKILL.md 全量进入上下文）
    ├── evaluation.md             # 最小 golden set 构建与 A/B 评估四指标
    ├── optimization-rulebook.md  # 行为学诊断表 + 处方表 + 最佳实践合规清单
    ├── rewrite-guide.md          # 知识提纯与条目改造细则（四元组、路由表、骨架模板）
    └── best-practices/           # 跨生态编写最佳实践知识库（11 项深度调研）
        ├── INDEX.md              # 路由表：需求场景 → 文件 → 关键结论 → grep 关键词
        ├── outline.yaml          # 调研对象与源 URL
        ├── fields.yaml           # 字段定义
        └── results/*.json        # 结构化调研结果
```

## 使用示例

在支持 skills 的 AI 工具中直接描述需求即可触发，例如：

- 「帮我优化这个 skill，加了参考资料之后效果反而变差了」
- 「对比这两个版本的 skill，哪个触发更可靠」
- 「审计一下 `<skill目录>` 的结构，看看有没有上下文超载」

## 依赖

- Python 3.8+（仅 `scripts/skill_audit.py` 需要，标准库实现，无第三方依赖）

## 更新最佳实践知识库

在仓库工作目录下的会话中说「更新 skills 最佳实践知识库」，会按 `references/best-practices/README.md` 中的 SOP 核对源 URL、修订 `results/` JSON 并刷新路由表。
