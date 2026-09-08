# -*- coding: utf-8 -*-
"""guard-skill 主引擎：第三方技能 / MCP / 代码包供应链审查。

装任何 Skill / MCP / 第三方代码前，先做一轮"入职背调"：
  溯源（作者 / 版本 / 更新时间）→ 全文件代码审查（红线清单）
  → 权限范围评估 → 输出四级风险判定与可存档审查报告。

退出码：
  0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / 4 已拦截（高风险）
"""
import sys
import os
import re
import json
import argparse

ENGINE_VERSION = "2.0.0"

# 四级风险
LEVEL_LOW, LEVEL_MID, LEVEL_HIGH, LEVEL_EXTREME = "低", "中", "高", "极端"

# 严重度扣分权重（信任分模型）
SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}

# 可审的文本扩展名
TEXT_EXTS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".jsonl", ".txt",
    ".yaml", ".yml", ".toml", ".sh", ".bat", ".ps1", ".cfg", ".ini",
    ".skills", ".lock", ".html", ".csv", ".xml",
}

# 跳过的目录
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode"}

RC_NAME = {0: "通过", 1: "参数错", 2: "IO错", 3: "未知命令", 4: "已拦截"}


def die(msg, rc):
    """集中报错，中文友好，退出码文档化。"""
    sys.stderr.write("【%s】%s\n" % (RC_NAME.get(rc, "错误"), msg))
    sys.exit(rc)


# ---------------------------------------------------------------------------
# 资源加载
# ---------------------------------------------------------------------------
def load_resource(name):
    p = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", name)
    )
    if not os.path.isfile(p):
        die("找不到规则资源文件：%s" % p, 2)
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError) as e:
        die("规则资源文件解析失败：%s（%s）" % (p, e), 2)


# ---------------------------------------------------------------------------
# 扫描
# ---------------------------------------------------------------------------
def iter_text_files(root):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXTS:
                yield os.path.join(dirpath, fn)


def scan_files(root, rules):
    """逐文件逐规则扫描，返回命中清单。"""
    findings = []
    for path in iter_text_files(root):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        rel = os.path.relpath(path, root)
        lines = content.splitlines()
        for rule in rules:
            pat = rule.get("pattern")
            if not pat:
                continue
            try:
                rx = re.compile(pat)
            except re.error:
                continue
            for m in rx.finditer(content):
                line_no = content.count("\n", 0, m.start()) + 1
                snippet = lines[line_no - 1].strip() if 1 <= line_no <= len(lines) else ""
                findings.append({
                    "rule_id": rule["id"],
                    "name": rule["name"],
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "file": rel,
                    "line": line_no,
                    "snippet": snippet[:200],
                })
    return findings


def assess_provenance(root):
    """从 SKILL.md frontmatter 取溯源信息。"""
    skill_md = os.path.join(root, "SKILL.md")
    info = {
        "has_skill_md": os.path.isfile(skill_md),
        "name": None, "author": None,
        "version": None, "updated": None, "date": None,
    }
    if not info["has_skill_md"]:
        return info
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            text = f.read()
    except (UnicodeDecodeError, OSError):
        return info
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return info
    fm = m.group(1)
    for key in ("name", "author", "version", "updated", "date"):
        mm = re.search(r"^%s:\s*(.+)$" % re.escape(key), fm, re.M)
        if mm:
            info[key] = mm.group(1).strip()
    return info


def assess_scope(root):
    """统计网络 / 文件写入 / shell 三类信号，作为权限范围评估。"""
    net = fs_write = shell = 0
    for path in iter_text_files(root):
        try:
            with open(path, "r", encoding="utf-8") as f:
                c = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        net += len(re.findall(r"https?://", c))
        fs_write += len(re.findall(r"(os\.remove|shutil\.rmtree|os\.unlink|open\([^)]*,\s*['\"]w)", c))
        shell += len(re.findall(r"shell\s*=\s*True|os\.system\(|subprocess", c))
    return {"network_signals": net, "fs_write_signals": fs_write, "shell_signals": shell}


# ---------------------------------------------------------------------------
# 判定与量化（原创量化点）
# ---------------------------------------------------------------------------
def infer_verdict(findings, provenance):
    """判定链：按严重度优先级收敛，不取平均。

    极端(任一极端命中) > 高(任一高危红线) > 中(中危红线 或 溯源不全) > 低(干净且溯源完整)
    """
    has_extreme = any(f["severity"] == LEVEL_EXTREME for f in findings)
    has_high = any(f["severity"] == LEVEL_HIGH for f in findings)
    has_mid = any(f["severity"] == LEVEL_MID for f in findings)
    prov_incomplete = not (
        provenance.get("author") and (provenance.get("updated") or provenance.get("date"))
    )
    if has_extreme:
        return LEVEL_EXTREME
    if has_high:
        return LEVEL_HIGH
    if has_mid or prov_incomplete:
        return LEVEL_MID
    return LEVEL_LOW


def trust_score(findings, provenance):
    """供应链信任指数（0-100）：基准 100 减去命中扣分。"""
    penalty = 0
    for f in findings:
        penalty += SEV_WEIGHT.get(f["severity"], 0)
    if not (provenance.get("author") and (provenance.get("updated") or provenance.get("date"))):
        penalty += 8  # 溯源不全
    return max(0, 100 - penalty)


def avoided_loss_hours(verdict):
    return {"极端": 8, "高": 4, "中": 1, "低": 0}.get(verdict, 0)


# ---------------------------------------------------------------------------
# 报告
# ---------------------------------------------------------------------------
def build_report(root, findings, provenance, scope, verdict, score):
    now = _now()
    lines = []
    lines.append("# guard-skill 供应链审查报告")
    lines.append("")
    lines.append("- 审查时间：%s" % now)
    lines.append("- 被审包：%s" % os.path.abspath(root))
    lines.append("- 引擎版本：%s" % ENGINE_VERSION)
    lines.append("")
    lines.append("## 一、判定")
    lines.append("")
    lines.append("- **风险等级：%s**" % verdict)
    lines.append("- **供应链信任指数：%d / 100**" % score)
    lines.append("- **处置建议：%s**" % (
        "禁止安装（无例外）" if verdict == LEVEL_EXTREME
        else "拦下，需人工批准后再决定" if verdict == LEVEL_HIGH
        else "可安装，但留意中危项与溯源缺失" if verdict == LEVEL_MID
        else "可安装"
    ))
    lines.append("")
    lines.append("## 二、溯源（入职背调）")
    lines.append("")
    if provenance["has_skill_md"]:
        lines.append("- SKILL.md：存在")
        lines.append("- name：%s" % (provenance.get("name") or "（未声明）"))
        lines.append("- author：%s" % (provenance.get("author") or "（缺失）⚠️"))
        lines.append("- version：%s" % (provenance.get("version") or "（未声明）"))
        lines.append("- updated/date：%s" % (provenance.get("updated") or provenance.get("date") or "（缺失）⚠️"))
    else:
        lines.append("- SKILL.md：**缺失** ⚠️ 无法做元数据溯源")
    lines.append("")
    lines.append("## 三、红线命中清单（%d 条）" % len(findings))
    lines.append("")
    if findings:
        lines.append("| 严重度 | 类别 | 规则 | 文件:行 | 片段 |")
        lines.append("|---|---|---|---|---|")
        for f in findings:
            snip = f["snippet"].replace("|", "\\|").replace("\n", " ")
            lines.append("| %s | %s | %s(%s) | %s:%d | %s |" % (
                f["severity"], f["category"], f["name"], f["rule_id"], f["file"], f["line"], snip))
    else:
        lines.append("（未命中任何红线规则）")
    lines.append("")
    lines.append("## 四、权限范围评估")
    lines.append("")
    lines.append("- 网络外联信号：%d 处" % scope["network_signals"])
    lines.append("- 文件写入/删除信号：%d 处" % scope["fs_write_signals"])
    lines.append("- Shell/子进程信号：%d 处" % scope["shell_signals"])
    lines.append("")
    lines.append("## 五、安全控制价值量化")
    lines.append("")
    lines.append("- 本次若放行后被利用，估算可避免损失：约 %d 小时事故响应" % avoided_loss_hours(verdict))
    lines.append("")
    lines.append("> 说明：本工具为静态代码与元数据审查，不保证 100%% 拦住所有后门（学界共识无单点银弹）。"
                 "判定依据为规则命中的严重度优先级链，非平均。")
    lines.append("")
    # 机器可读尾块（供 ledger 聚合）
    lines.append("```json")
    lines.append(json.dumps({
        "time": now,
        "path": os.path.abspath(root),
        "verdict": verdict,
        "trust_score": score,
        "findings": len(findings),
        "avoided_loss_hours": avoided_loss_hours(verdict),
    }, ensure_ascii=False))
    lines.append("```")
    return "\n".join(lines)


def _now():
    try:
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# 子命令
# ---------------------------------------------------------------------------
def cmd_review(args):
    if not args.path:
        die("缺少待审查的包路径（用法：guard.py review <包目录>）", 1)
    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)

    rules_data = load_resource("rules.json")
    rules = rules_data.get("rules", [])
    findings = scan_files(root, rules)
    provenance = assess_provenance(root)
    scope = assess_scope(root)
    verdict = infer_verdict(findings, provenance)
    score = trust_score(findings, provenance)

    report = build_report(root, findings, provenance, scope, verdict, score)
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "verdict_report.md")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as e:
        die("审查报告写入失败：%s" % e, 2)

    if args.json:
        print(json.dumps({
            "verdict": verdict, "trust_score": score,
            "findings": findings, "provenance": provenance, "scope": scope,
        }, ensure_ascii=False, indent=2))
    else:
        print(report)

    if verdict in (LEVEL_HIGH, LEVEL_EXTREME):
        die("审查判定为【%s】，建议不要安装（详见 %s）" % (verdict, out), 4)
    return 0


def cmd_scan(args):
    if not args.path:
        die("缺少待扫描的包路径（用法：guard.py scan <包目录>）", 1)
    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)

    rules = load_resource("rules.json").get("rules", [])
    findings = scan_files(root, rules)
    if args.json:
        print(json.dumps({"path": root, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        if not findings:
            print("未发现红线命中。")
        for f in findings:
            print("[%s][%s] %s @ %s:%d — %s" % (
                f["severity"], f["category"], f["name"], f["file"], f["line"], f["snippet"]))
        print("共发现 %d 条红线命中" % len(findings))
    # 门禁：高危/极端 -> 4
    if any(f["severity"] in (LEVEL_HIGH, LEVEL_EXTREME) for f in findings):
        return 4
    return 0


def cmd_rules(args):
    rules = load_resource("rules.json").get("rules", [])
    for r in rules:
        print("%s | %s | %s | %s" % (r["id"], r["severity"], r["category"], r["name"]))
    print("共 %d 条红线" % len(rules))
    return 0


def cmd_ledger(args):
    root = os.path.abspath(args.path) if args.path else os.getcwd()
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)
    records = []
    for dirpath, _, files in os.walk(root):
        if "verdict_report.md" in files:
            p = os.path.join(dirpath, "verdict_report.md")
            try:
                with open(p, "r", encoding="utf-8") as f:
                    txt = f.read()
            except OSError:
                continue
            m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
            if m:
                try:
                    records.append(json.loads(m.group(1)))
                except ValueError:
                    continue
    if not records:
        die("在 %s 下未找到任何 verdict_report.md" % root, 1)
    total_hours = sum(r.get("avoided_loss_hours", 0) for r in records)
    counts = {"极端": 0, "高": 0, "中": 0, "低": 0}
    for r in records:
        counts[r.get("verdict", "低")] = counts.get(r.get("verdict", "低"), 0) + 1
    out = os.path.join(root, "guard-ledger.md")
    blocks = []
    blocks.append("# guard 安全控制价值账本")
    blocks.append("")
    blocks.append("- 聚合时间：%s" % _now())
    blocks.append("- 审查记录数：%d" % len(records))
    blocks.append("")
    blocks.append("## 判定分布")
    blocks.append("")
    blocks.append("- 极端（禁止）：%d" % counts["极端"])
    blocks.append("- 高（拦下需批准）：%d" % counts["高"])
    blocks.append("- 中（可装需留意）：%d" % counts["中"])
    blocks.append("- 低（可信）：%d" % counts["低"])
    blocks.append("")
    blocks.append("## 价值量化")
    blocks.append("")
    blocks.append("- 累计拦下估算避免损失：**约 %d 小时事故响应**" % total_hours)
    blocks.append("")
    blocks.append("> 安全工具的价值天然不可见（什么都没发生 = 看起来没用）。"
                  "本账本把「没发生的事故」折算成可感知数字，是续用与传播的理由。")
    blocks.append("")
    for r in records:
        blocks.append("- [%s] %s | 判定=%s | 信任分=%s | 避免=%dh" % (
            r.get("time", "?"), r.get("path", "?"),
            r.get("verdict", "?"), r.get("trust_score", "?"), r.get("avoided_loss_hours", 0)))
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(blocks))
    except OSError as e:
        die("账本写入失败：%s" % e, 2)
    print("已生成 %s（%d 条记录，累计避免约 %d 小时）" % (out, len(records), total_hours))
    return 0


def cmd_version(args):
    print("guard-skill 引擎 v%s" % ENGINE_VERSION)
    return 0


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv):
    KNOWN = {"review", "scan", "rules", "ledger", "version"}
    if argv and argv[0] not in KNOWN and not argv[0].startswith("-"):
        die("未知子命令：%s（可用 review/scan/rules/ledger/version）" % argv[0], 3)
    parser = argparse.ArgumentParser(prog="guard.py", description="guard-skill 供应链审查引擎")
    sub = parser.add_subparsers(dest="cmd")

    p_review = sub.add_parser("review", help="完整入职背调并出报告")
    p_review.add_argument("path", nargs="?")
    p_review.add_argument("--json", action="store_true")
    p_review.add_argument("--out")

    p_scan = sub.add_parser("scan", help="仅扫描列出红线命中")
    p_scan.add_argument("path", nargs="?")
    p_scan.add_argument("--json", action="store_true")

    sub.add_parser("rules", help="列出红线规则库")
    p_ledger = sub.add_parser("ledger", help="聚合审查报告生成价值账本")
    p_ledger.add_argument("path", nargs="?")
    sub.add_parser("version", help="打印引擎版本")

    args = parser.parse_args(argv)
    if not args.cmd or args.cmd == "version":
        return cmd_version(args)

    dispatch = {
        "review": cmd_review, "scan": cmd_scan,
        "rules": cmd_rules, "ledger": cmd_ledger,
    }
    if args.cmd not in dispatch:
        die("未知子命令：%s（可用 review/scan/rules/ledger/version）" % args.cmd, 3)
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
