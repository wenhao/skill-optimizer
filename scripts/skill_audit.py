#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skill_audit.py — skills-optimizer 的机械审计脚本。

对目标 skill 目录做结构合规扫描，输出结构化报告（JSON + 人读文本）。
检查项对应 optimization-rulebook.md 的 RB-06/07/08 与 SKILL.md 红线。

用法:
    python skill_audit.py <skill-dir> [--eval-data <eval.json>]

退出码: 0=通过(仅提示) 1=发现错误 2=用法错误
"""

import argparse
import json
import os
import re
import sys

# 简易 YAML frontmatter 解析（不依赖 PyYAML）
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return None, None
    fm_raw, body = m.group(1), text[m.end():]
    fm = {}
    lines = fm_raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m2 = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if not m2:
            i += 1
            continue
        key, val = m2.group(1), m2.group(2).strip()
        if val in ("|", ">", "|-", ">-", "|+", ">+"):
            # YAML 块标量：收集后续缩进行
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            fm[key] = " ".join(b for b in block if b)
        else:
            fm[key] = val.strip("'\"")
            i += 1
    return fm, body

def count_tokens_approx(text):
    # 中文 ~1 token/字，英文 ~0.75 token/词 的粗略折中：字符数/2.5
    return int(len(text) / 2.5)

ANTITRIGGER_WORDS = ["do not", "skip", "not for", "out of scope", "when not",
                     "不要", "不属于", "排除", "不适用", "越界"]

def audit(skill_dir, eval_path=None):
    issues, warns, infos = [], [], []
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return {"error": "SKILL.md not found in %s" % skill_dir, "exit": 2}

    text = open(skill_md, encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    if fm is None:
        issues.append("frontmatter: SKILL.md 未以 --- 开头的 YAML frontmatter（整文件会被当正文处理）")
        fm, body = {}, text

    # ---- description 检查（RB-06/07/08）----
    desc = fm.get("description", "")
    if not desc:
        issues.append("frontmatter: 缺 description（决定模型何时触发本 skill）")
    else:
        dl = len(desc)
        if dl < 60:
            issues.append("description 过短(%d 字符)：无触发信息，模型无从模式匹配（建议 ≥200 字符）" % dl)
        elif dl < 150:
            warns.append("description 偏短(%d 字符)：建议补触发场景与关键词" % dl)
        if dl > 1024:
            issues.append("description %d 字符超开放标准上限 1024" % dl)
        has_trigger = any(k in desc.lower() for k in ["use when", "当用户", "触发", "适用于"])
        if not has_trigger:
            warns.append("description 未写触发场景（Use when / 当用户…）——影响触发命中率")
        # 反触发边界（RB-06）
        antitrigger_in_desc = any(w in desc.lower() for w in ANTITRIGGER_WORDS)
        antitrigger_in_body = any(w in body.lower() for w in ANTITRIGGER_WORDS)
        if not antitrigger_in_desc and not antitrigger_in_body:
            warns.append("未发现反触发边界（When NOT to use / 不要 / 排除）——RB-06：最高杠杆的单点改进")
        # name
    name = fm.get("name", "")
    dirname = os.path.basename(os.path.normpath(skill_dir))
    if name and name != dirname:
        warns.append("frontmatter name(%r) 与目录名(%r) 不一致（跨平台规范要求一致）" % (name, dirname))

    # ---- 正文预算（红线 <500 行 / <5000 token）----
    lines = body.count("\n") + 1
    tokens = count_tokens_approx(body)
    if lines > 500:
        issues.append("正文 %d 行超红线 500 行——应拆分到 references/" % lines)
    elif lines > 300:
        warns.append("正文 %d 行接近红线，建议审视可下沉内容" % lines)
    if tokens > 5000:
        issues.append("正文估算约 %d token 超 5000 红线" % tokens)
    else:
        infos.append("正文 %d 行 / 估算约 %d token" % (lines, tokens))

    # ---- 目录组织 ----
    refs = os.path.join(skill_dir, "references") if os.path.isdir(os.path.join(skill_dir, "references")) \
        else (os.path.join(skill_dir, "reference") if os.path.isdir(os.path.join(skill_dir, "reference")) else None)
    if refs:
        ref_files = []
        for root, _, files in os.walk(refs):
            for f in files:
                if f.endswith((".md", ".txt")):
                    p = os.path.join(root, f)
                    ref_files.append((p, os.path.getsize(p)))
        big = [p for p, s in ref_files if s > 25000]
        if big:
            for p in big:
                warns.append("大参考文件 %s（%.0fKB）：RB 建议 >10k 词的文件在 SKILL.md 提供 grep 检索模式"
                             % (os.path.relpath(p, skill_dir), os.path.getsize(p) / 1024))
        infos.append("references: %d 个文件" % len(ref_files))
        # 路由表存在性：正文是否提及 references 文件名
        routed = sum(1 for p, _ in ref_files
                     if os.path.basename(p).replace(".md", "") in body)
        if ref_files and routed == 0:
            warns.append("SKILL.md 正文未引用任何 references 文件名——缺路由表（渐进披露失效，参考成死资产）")
        else:
            infos.append("路由覆盖: %d/%d 个 references 被正文引用" % (routed, len(ref_files)))
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        n_scripts = len([f for f in os.listdir(scripts_dir) if f.endswith((".py", ".sh", ".js"))])
        if n_scripts >= 5:
            warns.append("scripts/ 含 %d 个脚本——RB-05 编排税风险：核对每个环节是否真的需要模型经手" % n_scripts)
        infos.append("scripts: %d 个" % n_scripts)

    # ---- evals 目录（评估闭环）----
    if not os.path.isdir(os.path.join(skill_dir, "evals")):
        infos.append("无 evals/ 目录——建议建立最小评测集（2-3 用例起步）")

    # ---- 评测数据联动 ----
    eval_summary = None
    if eval_path and os.path.isfile(eval_path):
        try:
            ev = json.load(open(eval_path, encoding="utf-8"))
            eval_summary = ev
            # 评测驱动提示：发现率低时点名 RB-04/05
            for metric in (ev.get("metrics") or []):
                nm = str(metric.get("name", "")).lower()
                val = metric.get("value")
                # 对照/基线指标不参与本 skill 的诊断
                if any(k in nm for k in ("对照", "baseline", "对照-", "对照组")):
                    continue
                if val is not None and isinstance(val, (int, float)):
                    # 范围类指标（行外/out-of-scope/范围外）低于阈值 → RB-04
                    scope_keys = ("行外", "范围外", "out-of-scope", "out of scope", "outside")
                    if any(k in nm for k in scope_keys) and val < 30:
                        issues.append("评测: 范围外指标 %s = %.1f%% 塌陷——RB-04 范围锁死（检查硬边界语句与输出 schema）"
                                      % (metric.get("name"), val))
                    # 通用核心达成类指标偏低 → 提示对照症状速查表
                    core_keys = ("recall", "召回", "发现", "达成", "覆盖", "coverage", "accuracy", "准确",
                                 "precision", "精确")
                    if val < 50 and any(k in nm for k in core_keys):
                        warns.append("评测: %s = %.1f%% 偏低——对照症状速查表定位根因" % (metric.get("name"), val))
        except Exception as e:
            warns.append("评测文件解析失败: %s" % e)

    report = {
        "skill": skill_dir,
        "errors": issues,
        "warnings": warns,
        "info": infos,
        "frontmatter": fm,
        "eval_summary": eval_summary,
        "pass": len(issues) == 0,
    }
    return report

def main():
    ap = argparse.ArgumentParser(description="skill 结构审计（skills-optimizer 阶段 1 机械检查）")
    ap.add_argument("skill_dir")
    ap.add_argument("--eval-data", default=None, help="评测数据 JSON（含 metrics[].name/value）")
    ap.add_argument("--json", action="store_true", help="输出纯 JSON")
    args = ap.parse_args()

    report = audit(args.skill_dir, args.eval_data)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(report.get("exit", 0 if report["pass"] else 1))
    if "error" in report:
        print("[错误] %s" % report["error"]); sys.exit(2)
    print("=" * 60)
    print("[审计] %s" % report["skill"])
    print("=" * 60)
    for s in report["info"]:
        print("  [信息] %s" % s)
    for s in report["warnings"]:
        print("  [警告] %s" % s)
    for s in report["errors"]:
        print("  [错误] %s" % s)
    print("-" * 60)
    print("结论: %s（错误 %d / 警告 %d）" % ("通过" if report["pass"] else "不通过",
          len(report["errors"]), len(report["warnings"])))
    sys.exit(0 if report["pass"] else 1)

if __name__ == "__main__":
    main()
