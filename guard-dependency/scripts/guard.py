# -*- coding: utf-8 -*-
"""guard-dependency 主引擎：第三方依赖的漏洞与投毒护栏。

开源依赖一旦被投毒（依赖混淆 / typosquatting / 安装钩子执行恶意代码 / 锁文件缺失/
走明文 http 源被中间人篡改），后果是整条供应链沦陷。本引擎在合入依赖、发布前
静态扫一遍依赖清单与安装配置，算一笔「依赖风险指数」，落实物报告让你看清治理缺口再决定。

设计立场同系列：看清后果再决定，不硬禁止——硬禁止会逼人把依赖写死进 vendored 黑箱，更糟。
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

# 严重度权重（依赖风险指数）
SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}

# 可审的文本扩展名
TEXT_EXTS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".jsonl", ".yaml",
    ".yml", ".toml", ".sh", ".bash", ".bat", ".ps1", ".cfg", ".ini", ".skills",
    ".lock", ".sql", ".html", ".csv", ".xml", ".env", ".txt", ".rb", ".php",
    ".go", ".java", ".npmrc", ".conf", ".txt", ".lock.json",
}

# 跳过的目录
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea",
             ".vscode", "dist", "build"}

# 上下文白名单（示例/教学/虚构语境，命中则放过）
# 本系列引擎用全局常量，不读 rules.json 的 allowlist（与 guard #3–#9 一致）。
ALLOW_KEYWORDS = {
    "your-", "xxxx", "dummy", "test", "testing", "placeholder",
    "changeme", "sample", "mock", "fake", "todo", "fixme", "demo", "foobar",
    "示例", "虚构", "仅为演示", "仅供测试", "教学", "练习题",
}

RC_NAME = {0: "通过", 1: "参数错", 2: "IO错", 3: "未知命令", 4: "已拦截"}

# 依赖域专用文案（把"可逆性"换成"可治理性"——检测到的依赖风险是否可经治理消除）
REVERSIBLE_LABEL = "可治理性"
RECOVERABLE_WORD = "可治理"
IRRECOVERABLE_WORD = "不可治理"


def die(msg, rc):
    sys.stderr.write("【%s】%s\n" % (RC_NAME.get(rc, "错误"), msg))
    sys.exit(rc)


# ---------------------------------------------------------------------------
# 资源加载
# ---------------------------------------------------------------------------
def load_resource(name):
    p = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", name))
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
# 依赖风险检测（纯模式匹配 + 复合规则）
# ---------------------------------------------------------------------------
def scan_files(root, cfg):
    """逐文件检测依赖清单/安装配置的漏洞与投毒风险。"""
    findings = []
    rules = cfg.get("rules", [])
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

        for rule in rules:
            # 安全变体层：仅鼓励信号，不当命中
            if rule.get("safe_signal"):
                continue
            pat = rule.get("pattern")
            req = rule.get("req_regex")
            absent = rule.get("absent_patterns")

            # 复合规则：文件级单次命中（有地址但无完整性哈希 等）
            if (req or absent) and not pat:
                if req:
                    mreq = re.search(req, content, re.IGNORECASE)
                    if not mreq:
                        continue
                else:
                    mreq = None
                if absent:
                    hit_absent = False
                    for ap in absent:
                        try:
                            if re.search(ap, content, re.IGNORECASE):
                                hit_absent = True
                                break
                        except re.error:
                            continue
                    if hit_absent:
                        continue
                line_no = _line_no(content, mreq.start()) if mreq else 1
                snippet = lines[line_no - 1].strip() if 1 <= line_no <= len(lines) else ""
                sev = rule.get("severity", "中")
                findings.append({
                    "layer": rule.get("layer", "dependency"),
                    "rule_id": rule["id"], "name": rule["name"],
                    "category": rule.get("category", "未知"),
                    "severity": sev, "intent": rule.get("intent", ""),
                    "recoverable": rule.get("recoverable", "unknown"),
                    "note": rule.get("note", ""),
                    "file": rel, "line": line_no,
                    "snippet": snippet[:200],
                })
                continue

            # 纯模式匹配：逐命中
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
                    "layer": rule.get("layer", "dependency"),
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


def risk_index(findings):
    """依赖风险指数（0-100）：命中严重度权重累加，封顶 100。"""
    return min(100, sum(SEV_WEIGHT.get(f["severity"], 0) for f in findings))


def avoided_govern_hours(verdict):
    # 拦下后估算避免的"依赖治理与漏洞修复"工时（非精确）：极端 8h / 高 4h / 中 1h / 低 0h
    return {"极端": 8, "高": 4, "中": 1, "低": 0}.get(verdict, 0)


def count_recoverable(findings):
    rec = [f for f in findings if f.get("recoverable") is True]
    irr = [f for f in findings if f.get("recoverable") is False]
    return len(rec), len(irr)


# ---------------------------------------------------------------------------
# 报告
# ---------------------------------------------------------------------------
def build_report(root, findings, verdict, score):
    now = _now()
    lines = []
    lines.append("# guard-dependency 依赖漏洞与投毒护栏检测报告")
    lines.append("")
    lines.append("- 扫描时间：%s" % now)
    lines.append("- 目标：%s" % os.path.abspath(root))
    lines.append("- 引擎版本：%s" % ENGINE_VERSION)
    lines.append("")
    lines.append("## 一、判定")
    lines.append("")
    lines.append("- **风险等级：%s**" % verdict)
    lines.append("- **依赖风险指数：%d / 100**" % score)
    rec, irr = count_recoverable(findings)
    lines.append("- **%s：%d 处可治理 / %d 处不可治理**" % (REVERSIBLE_LABEL, rec, irr))
    lines.append("- **处置建议：%s**" % (
        "禁止合入（无例外，先升级/替换/加锁/换 https 源再引入）" if verdict == LEVEL_EXTREME
        else "拦下，人工确认后再决定；依赖风险必须先治理" if verdict == LEVEL_HIGH
        else "可继续，但补齐缺失的锁文件/完整性哈希/固定版本" if verdict == LEVEL_MID
        else "未发现明显依赖风险"))
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
        lines.append("（未发现依赖风险）")
    lines.append("")
    lines.append("## 三、命中清单")
    lines.append("")
    if findings:
        lines.append("| 严重度 | 类型 | %s | 规则 | 文件:行 | 片段 | 备注 |" % RECOVERABLE_WORD)
        lines.append("|---|---|---|---|---|---|---|")
        for f in findings:
            snip = f["snippet"].replace("|", "\\|").replace("\n", " ")
            rec_word = {True: RECOVERABLE_WORD, False: IRRECOVERABLE_WORD, "unknown": "未知"}[f.get("recoverable")]
            lines.append("| %s | %s | %s | %s(%s) | %s:%d | %s | %s |" % (
                f["severity"], f["category"], rec_word, f["name"],
                f["rule_id"], f["file"], f["line"], snip, f.get("note", "")))
    else:
        lines.append("（无）")
    lines.append("")
    lines.append("## 四、安全控制价值量化")
    lines.append("")
    lines.append("- 本次若放行，估算可避免损失：约 %d 小时依赖治理与漏洞修复" % avoided_govern_hours(verdict))
    lines.append("")
    lines.append("> 说明：本工具立场是「看清后果再决定」，不是硬禁止——硬禁止会逼人把依赖写死进 vendored 黑箱，那是更坏结局。"
                 "判定依据为命中的严重度优先级链，非平均。诚实边界：仅做静态检测，不实际拦依赖解析；"
                 "对运行时真实依赖树无感知；依赖后果取决于该包是否真被安装且被加载，本工具只量化静态可见风险。")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps({
        "time": now,
        "target": os.path.abspath(root),
        "verdict": verdict,
        "risk_index": score,
        "governable": rec, "ungovernable": irr,
        "findings": len(findings),
        "avoided_govern_hours": avoided_govern_hours(verdict),
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
    score = risk_index(findings)

    report = build_report(root, findings, verdict, score)
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "dependency_report.md")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as e:
        die("扫描报告写入失败：%s" % e, 2)

    if args.json:
        print(json.dumps({"verdict": verdict, "risk_index": score,
                          "findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(report)

    if verdict in (LEVEL_HIGH, LEVEL_EXTREME):
        die("扫描判定为【%s】，建议不要直接合入（详见 %s）" % (verdict, out), 4)
    return 0


def cmd_rules(args):
    cfg = load_resource("rules.json")
    print("依赖漏洞与投毒护栏规则总数：%d" % len(cfg.get("rules", [])))
    print("")
    labels = [
        ("manifest", "依赖清单"), ("version", "版本风险"), ("confusion", "混淆/投毒"),
        ("integrity", "完整性"), ("source", "来源可信"), ("safe", "安全变体"),
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
        die("在 %s 下未找到任何 dependency_report.md" % root, 1)
    total_hours = sum(r.get("avoided_govern_hours", 0) for r in records)
    counts = {"极端": 0, "高": 0, "中": 0, "低": 0}
    for r in records:
        counts[r.get("verdict", "低")] = counts.get(r.get("verdict", "低"), 0) + 1
    out = os.path.join(root, "guard-ledger.md")
    blocks = []
    blocks.append("# guard 安全控制价值账本（依赖漏洞与投毒护栏）")
    blocks.append("")
    blocks.append("- 聚合时间：%s" % _now())
    blocks.append("- 扫描记录数：%d" % len(records))
    blocks.append("")
    blocks.append("## 判定分布")
    blocks.append("- 极端（禁止合入）：%d" % counts["极端"])
    blocks.append("- 高（拦下需确认）：%d" % counts["高"])
    blocks.append("- 中（需补护栏）：%d" % counts["中"])
    blocks.append("- 低（可信）：%d" % counts["低"])
    blocks.append("")
    blocks.append("## 价值量化")
    blocks.append("- 累计拦下估算避免损失：**约 %d 小时依赖治理与漏洞修复**" % total_hours)
    blocks.append("")
    blocks.append("> 依赖一旦被投毒，整条供应链沦陷，修复成本（替换、回溯、通知下游）远高于事前锁版本/校验/换源。"
                  "本账本把「没发生的投毒」折算成可感知数字。")
    blocks.append("")
    for r in records:
        blocks.append("- [%s] %s | 判定=%s | 依赖风险=%s | 可治理=%s | 避免=%dh" % (
            r.get("time", "?"), r.get("target", "?"), r.get("verdict", "?"),
            r.get("risk_index", "?"), r.get("governable", "?"), r.get("avoided_govern_hours", 0)))
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(blocks))
    except OSError as e:
        die("账本写入失败：%s" % e, 2)
    print("已生成 %s（%d 条记录，累计避免约 %d 小时）" % (out, len(records), total_hours))
    return 0


def cmd_version(args):
    print("guard-dependency 引擎 v%s" % ENGINE_VERSION)
    return 0


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv):
    KNOWN = {"scan", "rules", "ledger", "version"}
    if argv and argv[0] not in KNOWN and not argv[0].startswith("-"):
        die("未知子命令：%s（可用 scan/rules/ledger/version）" % argv[0], 3)
    parser = argparse.ArgumentParser(prog="guard.py", description="guard-dependency 依赖护栏引擎")
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="扫描目录并出依赖风险报告")
    p_scan.add_argument("path", nargs="?")
    p_scan.add_argument("--json", action="store_true")
    p_scan.add_argument("--out")

    sub.add_parser("rules", help="列出依赖护栏规则库")
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
