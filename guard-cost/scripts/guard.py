# -*- coding: utf-8 -*-
"""guard-cost 主引擎：API 花费熔断（成本防护）。

rm -rf 会删库，无护栏的付费 API 调用会"删钱"：循环里调大模型、无限重试、
没预算上限、没熔断，月底账单能炸。本引擎在代码跑起来之前，先扫一遍这些成本雷区，
算一笔"花费暴露指数"，并干跑一笔投影花费让你看清上限。

设计立场同系列：看清后果再决定，不硬禁止——硬禁止会逼人绕过，更糟。
退出码：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / 4 已拦截（高/极端风险）。
"""

import sys
import os
import re
import json
import argparse

ENGINE_VERSION = "2.0.0"

# 四级风险
LEVEL_LOW, LEVEL_MID, LEVEL_HIGH, LEVEL_EXTREME = "低", "中", "高", "极端"

# 严重度权重（花费暴露指数）
SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}

# 可审的文本扩展名
TEXT_EXTS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".jsonl", ".yaml",
    ".yml", ".toml", ".sh", ".bat", ".ps1", ".cfg", ".ini", ".skills",
    ".lock", ".sql", ".html", ".csv", ".xml", ".env", ".rb", ".php", ".go", ".java",
}

# 跳过的目录
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode", "dist", "build"}

# 上下文白名单（示例/教学/虚构语境，命中则放过）
# 注意：本系列引擎用全局常量，不读 rules.json 的 allowlist（与 guard #3/#4 一致）。
ALLOW_KEYWORDS = {
    "your-", "xxxx", "dummy", "test", "testing", "placeholder",
    "changeme", "sample", "mock", "fake", "todo", "fixme", "demo", "foobar",
    "示例", "虚构", "仅为演示", "仅供测试", "教学", "练习题",
}

# 付费 API 调用信号（用于复合规则判定"文件里到底有没有调付费 API"）
API_CALL_RX = re.compile(
    r'\b(?:api|openai|llm|completions?|chat\.completions|client\.|fetch|'
    r'requests\.(?:get|post|put|delete)|invoke|generate|anthropic|claude|'
    r'gemini|deepseek|azure.*cognitive|bedrock)\b', re.I)

RC_NAME = {0: "通过", 1: "参数错", 2: "IO错", 3: "未知命令", 4: "已拦截"}

# 成本域专用文案（把"可逆性"换成"可规避性"，契合花费防护语义）
REVERSIBLE_LABEL = "可规避性"
RECOVERABLE_WORD = "可规避"
IRRECOVERABLE_WORD = "不可规避"

# 花费投影简写：model:callsxtokens（tokens 为每次调用总 token 数）
CAP_SHORTHAND_RX = re.compile(r'^([\w.\-]+):(\d+)(?:x(\d+))?$')


def die(msg, rc):
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
# 成本雷区检测
# ---------------------------------------------------------------------------
def scan_files(root, cfg):
    """逐文件检测付费 API 调用的成本风险：无界循环、缺预算、缺熔断、硬编码密钥等。"""
    findings = []
    rules = cfg.get("rules", [])
    allow_paths = set(cfg.get("allowlist", {}).get("paths", []))
    has_api_rx = API_CALL_RX

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
        file_has_api = bool(has_api_rx.search(content))

        for rule in rules:
            # 安全变体层：仅鼓励信号，不当命中
            if rule.get("safe_signal"):
                continue
            pat = rule.get("pattern")
            # 复合规则：要求文件含付费 API 调用
            if rule.get("require_api") and not file_has_api:
                continue
            # 复合规则：要求某些护栏模式都不存在
            absent = rule.get("absent_patterns")
            if absent:
                if any(re.search(re.escape(a), content, re.IGNORECASE) for a in absent):
                    continue
            if not pat:
                continue
            try:
                rx = re.compile(pat, re.IGNORECASE | re.DOTALL)
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
                    "layer": rule.get("layer", "cost"),
                    "rule_id": rule["id"], "name": rule["name"],
                    "category": rule.get("category", "未知"),
                    "severity": sev, "intent": rule.get("intent", ""),
                    "recoverable": rule.get("recoverable", "unknown"),
                    "note": rule.get("note", ""),
                    "file": rel, "line": line_no,
                    "snippet": snippet[:200],
                })

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
    """花费暴露指数（0-100）：命中严重度权重累加，封顶 100。"""
    return min(100, sum(SEV_WEIGHT.get(f["severity"], 0) for f in findings))


def avoided_spend_hours(verdict):
    # 拦下后估算避免的"对账/止损"工时（非精确）：极端 8h / 高 4h / 中 1h / 低 0h
    return {"极端": 8, "高": 4, "中": 1, "低": 0}.get(verdict, 0)


def count_recoverable(findings):
    rec = [f for f in findings if f.get("recoverable") is True]
    irr = [f for f in findings if f.get("recoverable") is False]
    return len(rec), len(irr)


# ---------------------------------------------------------------------------
# 报告
# ---------------------------------------------------------------------------
def build_report(root, findings, verdict, score, mode="scan"):
    now = _now()
    lines = []
    title = "guard-cost 成本风险检测报告" if mode == "scan" else "guard-cost 花费投影报告"
    lines.append("# %s" % title)
    lines.append("")
    lines.append("- 扫描时间：%s" % now)
    lines.append("- 目标：%s" % os.path.abspath(root))
    lines.append("- 引擎版本：%s" % ENGINE_VERSION)
    lines.append("")
    lines.append("## 一、判定")
    lines.append("")
    lines.append("- **风险等级：%s**" % verdict)
    lines.append("- **花费暴露指数：%d / 100**" % score)
    rec, irr = count_recoverable(findings)
    lines.append("- **%s：%d 处可规避 / %d 处不可规避**" % (REVERSIBLE_LABEL, rec, irr))
    lines.append("- **处置建议：%s**" % (
        "禁止上线（无例外，先加预算上限与熔断再发布）" if verdict == LEVEL_EXTREME
        else "拦下，人工确认后再决定；付费调用必须先加护栏" if verdict == LEVEL_HIGH
        else "可继续，但补齐缺失的预算/限速/熔断护栏" if verdict == LEVEL_MID
        else "未发现明显成本雷区"))
    lines.append("")
    lines.append("## 二、命中汇总（%d 处）" % len(findings))
    lines.append("")
    if findings:
        by_sev = {"极端": 0, "高": 0, "中": 0, "低": 0}
        by_cat = {}
        for f in findings:
            by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
            by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1
        lines.append("- 按严重度：极端 %d / 高 %d / 中 %d / 低 %d" % (
            by_sev["极端"], by_sev["高"], by_sev["中"], by_sev["低"]))
        lines.append("- 按类型：" + "、".join("%s %d" % (k, v) for k, v in by_cat.items()))
    else:
        lines.append("（未发现成本风险模式）")
    lines.append("")
    lines.append("## 三、命中清单")
    lines.append("")
    if findings:
        lines.append("| 严重度 | 类型 | %s | 规则 | 文件:行 | 片段 | 备注 |" % RECOVERABLE_WORD)
        lines.append("|---|---|---|---|---|---|---|")
        for f in findings:
            snip = f["snippet"].replace("|", "\\|").replace("\n", " ")
            rec = {True: RECOVERABLE_WORD, False: IRRECOVERABLE_WORD, "unknown": "未知"}[f.get("recoverable")]
            lines.append("| %s | %s | %s | %s(%s) | %s:%d | %s | %s |" % (
                f["severity"], f["category"], rec, f["name"],
                f["rule_id"], f["file"], f["line"], snip, f.get("note", "")))
    else:
        lines.append("（无）")
    lines.append("")
    lines.append("## 四、安全控制价值量化")
    lines.append("")
    lines.append("- 本次若放行，估算可避免损失：约 %d 小时账单对账与止损响应" % avoided_spend_hours(verdict))
    lines.append("")
    lines.append("> 说明：本工具立场是「看清后果再决定」，不是硬禁止——硬禁止会逼用户绕过护栏，那是更坏结局。"
                 "判定依据为命中的严重度优先级链，非平均。诚实边界：仅做静态检测，不实际拦请求；"
                 "对运行时动态调用频次无感知，单价以 cost-models.json 参考价为准，实际以账单为准。")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps({
        "time": now,
        "target": os.path.abspath(root),
        "verdict": verdict,
        "exposure_index": score,
        "recoverable": rec, "irrecoverable": irr,
        "findings": len(findings),
        "avoided_spend_hours": avoided_spend_hours(verdict),
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

    report = build_report(root, findings, verdict, score, mode="scan")
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "cost_report.md")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as e:
        die("扫描报告写入失败：%s" % e, 2)

    if args.json:
        print(json.dumps({"verdict": verdict, "exposure_index": score,
                          "findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(report)

    if verdict in (LEVEL_HIGH, LEVEL_EXTREME):
        die("扫描判定为【%s】，建议不要直接上线（详见 %s）" % (verdict, out), 4)
    return 0


def _cap_shorthand(target, models):
    """model:callsxtokens 简写 → 投影花费。"""
    m = CAP_SHORTHAND_RX.match(target)
    if not m:
        return None
    model = m.group(1).lower()
    calls = int(m.group(2))
    tokens = int(m.group(3)) if m.group(3) else 2000
    tbl = models.get("price_table", {})
    info = tbl.get(model)
    if info:
        in_p = info.get("per_1k_input", 0.0)
        out_p = info.get("per_1k_output", 0.0)
        blended = (in_p + out_p) / 2.0
        known = True
    else:
        blended = tbl.get("_default", {}).get("per_1k", 0.01)
        known = False
    cost = calls * tokens / 1000.0 * blended
    lines = [
        "# guard-cost 花费投影报告", "",
        "- 扫描时间：%s" % _now(),
        "- 模型：%s%s" % (model, "（参考单价）" if known else "（未知单价，按默认估算）"),
        "- 调用次数：%d" % calls,
        "- 单次 token 数：%d" % tokens,
        "- 投影花费：约 ¥%.2f / $%.2f" % (cost, cost),
        "",
        "## 建议",
        "- 给该调用加预算上限（MAX_COST / 熔断）后再上线；",
        "- 无限循环或重试务必有次数上限与退避；",
        "- 高单价模型考虑降级到 mini/轻量版。",
        "",
        "> 本投影仅按参考单价估算，实际以服务商账单为准。",
    ]
    return "\n".join(lines), cost, known


def cmd_cap(args):
    if not args.target:
        die("缺少目标路径或花费简写（用法：guard.py cap <路径 | model:调用次数x单次token>）", 1)
    target = args.target
    models = load_resource("cost-models.json")

    # 简写模式
    sh = _cap_shorthand(target, models)
    if sh is not None and not (os.path.exists(target) or target.startswith(("/", "./", "~"))):
        text, cost, known = sh
        out = os.path.abspath(args.out) if args.out else os.path.join(os.getcwd(), "cost_cap_report.md")
        try:
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
        except OSError as e:
            die("投影报告写入失败：%s" % e, 2)
        print(text)
        # 简写模式不拦截（只给数字）
        return 0

    # 路径模式：扫描 + 花费暴露指数
    root = os.path.abspath(target) if not target.startswith("/") else target
    is_root = (root in ("/", "\\")) or re.match(r'^[A-Za-z]:\\?$', root) is not None
    if is_root:
        die("目标为根目录/盘符根，拒绝遍历整盘，请指向具体子目录", 1)
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)

    cfg = load_resource("rules.json")
    findings = scan_files(root, cfg)
    verdict = infer_verdict(findings)
    score = exposure_index(findings)
    report = build_report(root, findings, verdict, score, mode="cap")
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "cost_report.md")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as e:
        die("投影报告写入失败：%s" % e, 2)
    print(report)
    if verdict in (LEVEL_HIGH, LEVEL_EXTREME):
        die("扫描判定为【%s】，建议不要直接上线（详见 %s）" % (verdict, out), 4)
    return 0


def cmd_rules(args):
    cfg = load_resource("rules.json")
    print("成本风险规则总数：%d" % len(cfg.get("rules", [])))
    print("")
    labels = [
        ("loop", "无界循环"), ("budget", "预算缺失"), ("rate", "限速/熔断缺失"),
        ("retry", "重试失控"), ("model", "高单价模型"), ("leakage", "密钥泄露"),
        ("safe", "安全变体"),
    ]
    for layer, label in labels:
        rs = [r for r in cfg.get("rules", []) if r.get("layer") == layer]
        if not rs:
            continue
        print("== %s（%d 条）==" % (label, len(rs)))
        for r in rs:
            rec = {True: RECOVERABLE_WORD, False: IRRECOVERABLE_WORD, "unknown": "未知"}[r.get("recoverable")]
            print("  %s | %s | %s | %s | %s" % (r["id"], r["severity"], r["category"], r["name"], rec))
    return 0


def cmd_ledger(args):
    root = os.path.abspath(args.path) if args.path else os.getcwd()
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)
    records = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.endswith("report.md"):
                p = os.path.join(dirpath, fn)
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
        die("在 %s 下未找到任何 cost_report.md / cost_cap_report.md" % root, 1)
    total_hours = sum(r.get("avoided_spend_hours", 0) for r in records)
    counts = {"极端": 0, "高": 0, "中": 0, "低": 0}
    for r in records:
        counts[r.get("verdict", "低")] = counts.get(r.get("verdict", "低"), 0) + 1
    out = os.path.join(root, "guard-ledger.md")
    blocks = []
    blocks.append("# guard 安全控制价值账本（API 花费熔断）")
    blocks.append("")
    blocks.append("- 聚合时间：%s" % _now())
    blocks.append("- 扫描记录数：%d" % len(records))
    blocks.append("")
    blocks.append("## 判定分布")
    blocks.append("- 极端（禁止上线）：%d" % counts["极端"])
    blocks.append("- 高（拦下需确认）：%d" % counts["高"])
    blocks.append("- 中（需补护栏）：%d" % counts["中"])
    blocks.append("- 低（可信）：%d" % counts["低"])
    blocks.append("")
    blocks.append("## 价值量化")
    blocks.append("- 累计拦下估算避免损失：**约 %d 小时账单对账与止损响应**" % total_hours)
    blocks.append("")
    blocks.append("> 无护栏的付费调用，代价在账单日才显现。本账本把「没发生的超支」折算成可感知数字。")
    blocks.append("")
    for r in records:
        blocks.append("- [%s] %s | 判定=%s | 花费暴露=%s | 可规避=%s | 避免=%dh" % (
            r.get("time", "?"), r.get("target", "?"), r.get("verdict", "?"),
            r.get("exposure_index", "?"), r.get("recoverable", "?"), r.get("avoided_spend_hours", 0)))
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(blocks))
    except OSError as e:
        die("账本写入失败：%s" % e, 2)
    print("已生成 %s（%d 条记录，累计避免约 %d 小时）" % (out, len(records), total_hours))
    return 0


def cmd_version(args):
    print("guard-cost 引擎 v%s" % ENGINE_VERSION)
    return 0


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv):
    KNOWN = {"scan", "cap", "rules", "ledger", "version"}
    if argv and argv[0] not in KNOWN and not argv[0].startswith("-"):
        die("未知子命令：%s（可用 scan/cap/rules/ledger/version）" % argv[0], 3)
    parser = argparse.ArgumentParser(prog="guard.py", description="guard-cost API 花费熔断引擎")
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="扫描目录并出成本风险报告")
    p_scan.add_argument("path", nargs="?")
    p_scan.add_argument("--json", action="store_true")
    p_scan.add_argument("--out")

    p_cap = sub.add_parser("cap", help="花费投影：路径扫描或 model:次数xtoken 简写")
    p_cap.add_argument("target", nargs="?")
    p_cap.add_argument("--out")

    sub.add_parser("rules", help="列出成本风险规则库")
    p_ledger = sub.add_parser("ledger", help="聚合扫描报告生成价值账本")
    p_ledger.add_argument("path", nargs="?")
    sub.add_parser("version", help="打印引擎版本")

    args = parser.parse_args(argv)
    if not args.cmd or args.cmd == "version":
        return cmd_version(args)

    dispatch = {
        "scan": cmd_scan, "cap": cmd_cap, "rules": cmd_rules, "ledger": cmd_ledger,
    }
    if args.cmd not in dispatch:
        die("未知子命令：%s（可用 scan/cap/rules/ledger/version）" % args.cmd, 3)
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
