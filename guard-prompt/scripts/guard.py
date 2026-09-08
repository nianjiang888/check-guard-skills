# -*- coding: utf-8 -*-
"""guard-prompt 主引擎：提示注入检测。

识别藏在网页 / 文档 / 邮件 / 图片描述 / 检索结果里的隐形指令，防止 AI 被远程操控：
  三维检测（指令劫持信号 → 结构/分隔符注入 → 意图目标）
  → 输出注入类型（直接/间接）、严重度、意图目标
  → 生成可存档的 injection_report.md，并把「拦下的注入攻击」折算成可感知数字。

退出码：
  0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / 4 已拦截（高/极端风险）
"""
import sys
import os
import re
import json
import argparse

ENGINE_VERSION = "2.0.0"

# 四级风险
LEVEL_LOW, LEVEL_MID, LEVEL_HIGH, LEVEL_EXTREME = "低", "中", "高", "极端"

# 严重度权重（注入风险分）
SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}

# 可审的文本扩展名
TEXT_EXTS = {
    ".md", ".txt", ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".jsonl",
    ".yaml", ".yml", ".toml", ".sh", ".bat", ".ps1", ".cfg", ".ini",
    ".skills", ".lock", ".html", ".csv", ".xml", ".env", ".prompt",
}

# 跳过的目录
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode", "dist", "build"}

# 上下文白名单（示例/教学/虚构语境，命中则放过）
# 注意：「假设」「example」已从白名单移除——它们会与真实攻击内容撞车
# （「假设你是」是角色覆盖信号；「collect.example.com」是外传目的地）。
ALLOW_KEYWORDS = {
    "your-", "xxxx", "dummy", "test", "testing", "placeholder",
    "changeme", "sample", "mock", "fake", "todo", "fixme", "demo", "foobar",
    "示例", "虚构", "仅为演示", "仅供测试", "教学", "练习题",
}

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
# 扫描基础设施
# ---------------------------------------------------------------------------
def iter_text_files(root):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXTS:
                yield os.path.join(dirpath, fn)


def _path_allowed(path, allow_paths):
    low = path.replace("\\", "/").lower()
    for ap in allow_paths:
        a = ap.lower()
        if a.startswith("*"):
            if low.endswith(a[1:]):
                return True
        elif a in low.split("/"):
            return True
    return False


def _context_window(content, start, end, span=60):
    cs = max(0, start - span)
    ce = min(len(content), end + span)
    return content[cs:ce]


def _line_no(content, pos):
    return content.count("\n", 0, pos) + 1


def _is_allowlisted(ctx):
    low = ctx.lower()
    return any(k in low for k in ALLOW_KEYWORDS)


# ---------------------------------------------------------------------------
# 三维检测
# ---------------------------------------------------------------------------
def scan_files(root, cfg):
    """逐文件跑三维检测：指令劫持信号(hijack) → 结构/分隔符注入(structure) → 意图目标(intent)。"""
    findings = []
    rules = cfg.get("rules", [])
    stealth = cfg.get("stealth_chars", [])
    allow_paths = set(cfg.get("allowlist", {}).get("paths", []))

    for path in iter_text_files(root):
        if _path_allowed(path, allow_paths):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        rel = os.path.relpath(path, root)
        lines = content.splitlines()

        # 规则匹配（三维合一，靠 layer 字段区分）
        for rule in rules:
            pat = rule.get("pattern")
            if not pat:
                continue
            try:
                rx = re.compile(pat, re.IGNORECASE)
            except re.error:
                continue
            for m in rx.finditer(content):
                line_no = _line_no(content, m.start())
                snippet = lines[line_no - 1].strip() if 1 <= line_no <= len(lines) else ""
                ctx = _context_window(content, m.start(), m.end())
                if _is_allowlisted(ctx):
                    continue
                sev = rule.get("severity", "中")
                findings.append({
                    "layer": rule.get("layer", "intent"),
                    "rule_id": rule["id"], "name": rule["name"],
                    "category": rule.get("category", "未知"),
                    "severity": sev, "intent": rule.get("intent", ""),
                    "file": rel, "line": line_no,
                    "snippet": snippet[:200],
                })

        # 隐形字符检测（零宽空格 / 软连字符 / BOM 注入）
        if stealth:
            for ch in stealth:
                if ch in content:
                    idx = content.find(ch)
                    line_no = _line_no(content, idx)
                    findings.append({
                        "layer": "structure", "rule_id": "PROMPT-STRUCT-03",
                        "name": "隐形/零宽字符注入", "category": "结构注入",
                        "severity": "高", "intent": "结构注入",
                        "file": rel, "line": line_no,
                        "snippet": "第 %d 行含不可见字符（零宽空格/软连字符/BOM），可能用于藏匿指令" % line_no,
                    })
                    break

    return _dedupe(findings)


def _dedupe(findings):
    seen = set()
    out = []
    for f in findings:
        key = (f["file"], f["line"], f["rule_id"])
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


# ---------------------------------------------------------------------------
# 判定与量化（原创量化点）
# ---------------------------------------------------------------------------
def infer_verdict(findings):
    """判定链：按严重度优先级收敛，不取平均。"""
    has_ext = any(f["severity"] == LEVEL_EXTREME for f in findings)
    has_high = any(f["severity"] == LEVEL_HIGH for f in findings)
    has_mid = any(f["severity"] == LEVEL_MID for f in findings)
    if has_ext:
        return LEVEL_EXTREME
    if has_high:
        return LEVEL_HIGH
    if has_mid:
        return LEVEL_MID
    return LEVEL_LOW


def exposure_index(findings):
    """注入风险分（0-100）：命中严重度权重累加，封顶 100。"""
    return min(100, sum(SEV_WEIGHT.get(f["severity"], 0) for f in findings))


def avoided_loss_hours(verdict):
    return {"极端": 8, "高": 4, "中": 1, "低": 0}.get(verdict, 0)


def classify_injection(findings):
    """判定注入类型（直接/间接）与意图目标清单。"""
    has_hijack = any(f["layer"] == "hijack" for f in findings)
    has_struct = any(f["layer"] == "structure" for f in findings)
    intents = sorted({f["intent"] for f in findings if f.get("intent")})
    if has_hijack:
        itype = "直接注入（direct：攻击者直接对模型下指令）"
    elif has_struct:
        itype = "间接注入（indirect：指令埋在检索内容/文档/图片描述里）"
    elif intents:
        itype = "意图信号（疑似间接注入）"
    else:
        itype = "无"
    return itype, intents


# ---------------------------------------------------------------------------
# 报告
# ---------------------------------------------------------------------------
def build_report(root, findings, verdict, score, itype, intents):
    now = _now()
    lines = []
    lines.append("# guard-prompt 提示注入检测报告")
    lines.append("")
    lines.append("- 扫描时间：%s" % now)
    lines.append("- 目标目录：%s" % os.path.abspath(root))
    lines.append("- 引擎版本：%s" % ENGINE_VERSION)
    lines.append("")
    lines.append("## 一、判定")
    lines.append("")
    lines.append("- **风险等级：%s**" % verdict)
    lines.append("- **注入风险分：%d / 100**" % score)
    lines.append("- **注入类型：%s**" % itype)
    if intents:
        lines.append("- **意图目标：%s**" % "、".join(intents))
    lines.append("- **处置建议：%s**" % (
        "禁止执行（无例外，立即人工复核并隔离来源）" if verdict == LEVEL_EXTREME
        else "拦下，人工确认后再决定；必要时隔离该段内容" if verdict == LEVEL_HIGH
        else "可继续，但留意中危项（角色覆盖/工具调用/上下文污染需人工判断）" if verdict == LEVEL_MID
        else "未发现注入信号"
    ))
    lines.append("")
    lines.append("## 二、命中汇总（%d 处）" % len(findings))
    lines.append("")
    if findings:
        by_sev = {"极端": 0, "高": 0, "中": 0, "低": 0}
        by_cat = {}
        by_layer = {}
        for f in findings:
            by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
            by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1
            by_layer[f["layer"]] = by_layer.get(f["layer"], 0) + 1
        lines.append("- 按严重度：极端 %d / 高 %d / 中 %d / 低 %d" % (
            by_sev["极端"], by_sev["高"], by_sev["中"], by_sev["低"]))
        lines.append("- 按维度：劫持 %d / 结构 %d / 意图 %d" % (
            by_layer.get("hijack", 0), by_layer.get("structure", 0), by_layer.get("intent", 0)))
        lines.append("- 按类型：" + "、".join("%s %d" % (k, v) for k, v in by_cat.items()))
    else:
        lines.append("（未发现提示注入信号）")
    lines.append("")
    lines.append("## 三、命中清单")
    lines.append("")
    if findings:
        lines.append("| 维度 | 严重度 | 类型 | 规则 | 文件:行 | 片段 |")
        lines.append("|---|---|---|---|---|---|")
        for f in findings:
            snip = f["snippet"].replace("|", "\\|").replace("\n", " ")
            lines.append("| %s | %s | %s | %s(%s) | %s:%d | %s |" % (
                f["layer"], f["severity"], f["category"], f["name"],
                f["rule_id"], f["file"], f["line"], snip))
    else:
        lines.append("（无）")
    lines.append("")
    lines.append("## 四、安全控制价值量化")
    lines.append("")
    lines.append("- 本次若放行，估算可避免损失：约 %d 小时事故响应与内容隔离" % avoided_loss_hours(verdict))
    lines.append("")
    lines.append("> 说明：提示注入是 Transformer 架构级缺陷（模型无法区分指令与数据），学界共识无单点银弹。"
                 "本工具三维检测（指令劫持信号 + 结构/分隔符注入 + 意图目标）目标精度 90–95%，"
                 "判定依据为命中的严重度优先级链，非平均。诚实边界写进文档：拦不住精心构造的多模态/编码注入。")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps({
        "time": now,
        "path": os.path.abspath(root),
        "verdict": verdict,
        "exposure_index": score,
        "injection_type": itype,
        "intents": intents,
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
def cmd_scan(args):
    if not args.path:
        die("缺少待扫描的目录路径（用法：guard.py scan <目录>）", 1)
    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)

    cfg = load_resource("rules.json")
    findings = scan_files(root, cfg)
    verdict = infer_verdict(findings)
    score = exposure_index(findings)
    itype, intents = classify_injection(findings)

    report = build_report(root, findings, verdict, score, itype, intents)
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "injection_report.md")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as e:
        die("扫描报告写入失败：%s" % e, 2)

    if args.json:
        print(json.dumps({
            "verdict": verdict, "exposure_index": score,
            "injection_type": itype, "intents": intents,
            "findings": findings,
        }, ensure_ascii=False, indent=2))
    else:
        print(report)

    if verdict in (LEVEL_HIGH, LEVEL_EXTREME):
        die("扫描判定为【%s】，建议不要执行该内容（详见 %s）" % (verdict, out), 4)
    return 0


def cmd_rules(args):
    cfg = load_resource("rules.json")
    print("检测维度：指令劫持(hijack) / 结构注入(structure) / 意图目标(intent)")
    print("规则总数：%d" % len(cfg.get("rules", [])))
    print("")
    for layer, label in (("hijack", "指令劫持"), ("structure", "结构注入"), ("intent", "意图目标")):
        rs = [r for r in cfg.get("rules", []) if r.get("layer") == layer]
        print("== %s（%d 条）==" % (label, len(rs)))
        for r in rs:
            print("  %s | %s | %s | %s" % (r["id"], r["severity"], r["category"], r["name"]))
    print("")
    print("隐形字符检测：零宽空格/软连字符/BOM（PROMPT-STRUCT-03，命中即高）")
    return 0


def cmd_ledger(args):
    root = os.path.abspath(args.path) if args.path else os.getcwd()
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)
    records = []
    for dirpath, _, files in os.walk(root):
        if "injection_report.md" in files:
            p = os.path.join(dirpath, "injection_report.md")
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
        die("在 %s 下未找到任何 injection_report.md" % root, 1)
    total_hours = sum(r.get("avoided_loss_hours", 0) for r in records)
    counts = {"极端": 0, "高": 0, "中": 0, "低": 0}
    for r in records:
        counts[r.get("verdict", "低")] = counts.get(r.get("verdict", "低"), 0) + 1
    out = os.path.join(root, "guard-ledger.md")
    blocks = []
    blocks.append("# guard 安全控制价值账本（提示注入检测）")
    blocks.append("")
    blocks.append("- 聚合时间：%s" % _now())
    blocks.append("- 扫描记录数：%d" % len(records))
    blocks.append("")
    blocks.append("## 判定分布")
    blocks.append("- 极端（禁止）：%d" % counts["极端"])
    blocks.append("- 高（拦下需确认）：%d" % counts["高"])
    blocks.append("- 中（可继续需留意）：%d" % counts["中"])
    blocks.append("- 低（可信）：%d" % counts["低"])
    blocks.append("")
    blocks.append("## 价值量化")
    blocks.append("- 累计拦下估算避免损失：**约 %d 小时事故响应与内容隔离**" % total_hours)
    blocks.append("")
    blocks.append("> 安全工具的价值天然不可见（什么都没发生 = 看起来没用）。"
                  "本账本把「没发生的注入事故」折算成可感知数字，是续用与传播的理由。")
    blocks.append("")
    for r in records:
        blocks.append("- [%s] %s | 判定=%s | 风险分=%s | 类型=%s | 避免=%dh" % (
            r.get("time", "?"), r.get("path", "?"), r.get("verdict", "?"),
            r.get("exposure_index", "?"), r.get("injection_type", "?"), r.get("avoided_loss_hours", 0)))
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(blocks))
    except OSError as e:
        die("账本写入失败：%s" % e, 2)
    print("已生成 %s（%d 条记录，累计避免约 %d 小时）" % (out, len(records), total_hours))
    return 0


def cmd_version(args):
    print("guard-prompt 引擎 v%s" % ENGINE_VERSION)
    return 0


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv):
    KNOWN = {"scan", "rules", "ledger", "version"}
    if argv and argv[0] not in KNOWN and not argv[0].startswith("-"):
        die("未知子命令：%s（可用 scan/rules/ledger/version）" % argv[0], 3)
    parser = argparse.ArgumentParser(prog="guard.py", description="guard-prompt 提示注入检测引擎")
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="扫描目录并出报告")
    p_scan.add_argument("path", nargs="?")
    p_scan.add_argument("--json", action="store_true")
    p_scan.add_argument("--out")

    sub.add_parser("rules", help="列出检测规则库")
    p_ledger = sub.add_parser("ledger", help="聚合扫描报告生成价值账本")
    p_ledger.add_argument("path", nargs="?")
    sub.add_parser("version", help="打印引擎版本")

    args = parser.parse_args(argv)
    if not args.cmd or args.cmd == "version":
        return cmd_version(args)

    dispatch = {
        "scan": cmd_scan, "rules": cmd_rules, "ledger": cmd_ledger,
    }
    if args.cmd not in dispatch:
        die("未知子命令：%s（可用 scan/rules/ledger/version）" % args.cmd, 3)
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
