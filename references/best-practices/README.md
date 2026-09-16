# Skills 最佳实践知识库（best-practices）

编写 AI Agent Skills 的最佳实践调研语料，是 skills-optimizer 的证据底座，也可被任意其他 skill 按下述契约消费。

## 消费契约（其他 skill 引用本库时遵守）

1. **先读 INDEX.md**：按需求场景在路由表定位目标文件，不要全量载入（results/ 共 11 个 JSON ≈ 70KB，全量载入即上下文超载）。
2. **按需读 JSON**：`results/*.json` 为扁平结构化 JSON，字段含义见 `fields.yaml`；只需引用相关字段，不复述全文。
3. **引用格式**：`references/best-practices/results/<文件名>.json`（skills-optimizer 内部）或绝对路径（跨 skill）。
4. **结论可溯源**：引用任何结论时保留来源文件名与本库的 sources 字段，不臆造。

## 目录结构

| 文件/目录 | 作用 |
|---|---|
| `INDEX.md` | 路由表：需求场景 → 文件 → 关键结论速览 → grep 关键词 |
| `outline.yaml` | 调研配置：11 个调研对象（官方规范/博客/开放标准/社区/方法论）、更新源 URL、批次 |
| `fields.yaml` | 字段定义：6 大类 26 字段（基本信息/设计原则/结构规范/编写要点/执行与组合/质量评估/安全治理） |
| `results/` | 11 个结构化调研 JSON（2026-09-15 首轮深度调研产出） |

## 更新机制（手动触发）

在任意会话中说一句「更新 skills 最佳实践知识库」（工作目录指向本仓库时），按以下 SOP 执行：

1. 读 `outline.yaml` 的 items，逐项核对源 URL（WebFetch/WebSearch），重点找最近一个月的新增或变更内容
2. 某主题有实质更新 → 按 `fields.yaml` 字段结构修订 `results/` 对应 JSON（保留历史 sources，新内容追加）；全新重要主题 → 同结构新增 JSON 并同步 outline items
3. 刷新 `INDEX.md`：路由表、跨文件关键数字、受影响条目的结论速览、头部更新日期
4. 在下方更新记录追加一行；无实质变更也记一行检查记录

## 更新记录

- 2026-09-15：首轮深度调研完成，13 项产出（含平台特定内容 2 项）
- 2026-09-16：移除平台特定内容（WorkBuddy skill 体系、WorkBuddy 安全审计 2 项），保留 11 项通用生态调研；整体并入 skills-optimizer/references/
- 2026-09-16：例行核对 11 源（近一个月无实质新增内容）；outline 中 docs.claude.com 域名迁移为 platform.claude.com（item 1/8）；INDEX 补 synced skill 不执行注入命令的安全提示
