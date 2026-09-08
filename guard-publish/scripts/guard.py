# -*- coding: utf-8 -*-
"""guard-publish 主引擎：发布前合规检查。

内容/工具在对外发布前，先按发布清单静态过一遍：有没有广告法极限词、疗效承诺、收益承诺，
有没有该配的免责声明、隐私政策、数据来源，有没有没清掉的密钥、内网地址、未脱敏个人信息、
调试残留。发布是不可逆动作——发出去的东西收不回来。本引擎在「点发布」前静态检一遍，
算一笔「发布合规指数」，落实物报告让你看清合规缺口再决定。

设计立场同系列：看清后果再决定，不硬禁止——硬禁止会逼人换渠道私下发，更糟。
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

# 严重度权重（发布合规指数）
SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}

# 可审的文本扩展名
TEXT_EXTS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".jsonl", ".yaml",
    ".yml", ".toml", ".sh", ".bash", ".bat", ".ps1", ".cfg", ".ini", ".skills",
    ".lock", ".sql", ".html", ".csv", ".xml", ".env", ".txt", ".rb", ".php",
    ".go", ".java", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf",
}

# 跳过的目录
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea",
             ".vscode", "dist", "build"}

# 上下文白名单（示例/教学/虚构语境，命中则放过）
# 本系列引擎用全局常量，不读 rules.json 的 allowlist（与 guard #3–#11 一致）。
ALLOW_KEYWORDS = {
    "your-", "xxxx", "dummy", "test", "testing", "placeholder",
    "changeme", "sample", "mock", "fake", "todo", "fixme", "demo", "foobar",
    "示例", "虚构", "仅为演示", "仅供测试", "教学", "练习题",
}

RC_NAME = {0: "通过", 1: "参数错", 2: "IO错", 3: "未知命令", 4: "已拦截"}

# 外发域专用文案（"可逆性"换成"可整改性"——这条缺口发布前补得上，还是发布即不可逆）
REVERSIBLE_LABEL = "可整改性"
RECOVERABLE_WORD = "可整改"
IRRECOVERABLE_WORD = "不可整改"


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
# 发布合规检测（纯模式匹配 + 复合规则）
# ---------------------------------------------------------------------------
def scan_files(root, cfg):
    """逐文件检测发布前的合规缺口与不可收回内容。"""
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

            # 复合规则：文件级单次命中（有内容但缺配套声明/元信息）
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
                    "layer": rule.get("layer", "publish"),
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
                    "layer": rule.get("layer", "publish"),
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


def release_index(findings):
    """发布合规指数（0-100）：命中严重度权重累加，封顶 100。"""
    return min(100, sum(SEV_WEIGHT.get(f["severity"], 0) for f in findings))


def avoided_fix_hours(verdict):
    # 拦下后估算避免的"发布后整改与召回"工时（非精确）：极端 8h / 高 4h / 中 1h / 低 0h
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
    lines.append("# guard-publish 发布前合规检查报告")
    lines.append("")
    lines.append("- 扫描时间：%s" % now)
    lines.append("- 目标：%s" % os.path.abspath(root))
    lines.append("- 引擎版本：%s" % ENGINE_VERSION)
    lines.append("")
    lines.append("## 一、判定")
    lines.append("")
    lines.append("- **风险等级：%s**" % verdict)
    lines.append("- **发布合规指数：%d / 100**" % score)
    rec, irr = count_recoverable(findings)
    lines.append("- **%s：%d 处可整改 / %d 处不可整改**" % (REVERSIBLE_LABEL, rec, irr))
    lines.append("- **处置建议：%s**" % (
        "禁止发布（无例外，先清掉密钥与个人信息、删除违规承诺再发）" if verdict == LEVEL_EXTREME
        else "拦下，人工确认后再发布；合规项必须先补齐" if verdict == LEVEL_HIGH
        else "可发布，但补齐缺失的发布清单项" if verdict == LEVEL_MID
        else "未发现明显发布合规风险"))
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
        lines.append("（未发现发布合规风险）")
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
    lines.append("- 本次若放行，估算可避免损失：约 %d 小时发布后整改与召回" % avoided_fix_hours(verdict))
    lines.append("")
    lines.append("> 说明：本工具立场是「看清后果再决定」，不是硬禁止——硬禁止会逼人换渠道私下发，那是更坏结局。"
                 "判定依据为命中的严重度优先级链，非平均。诚实边界：仅做静态内容检测，不实际拦发布；"
                 "对内容是否真的发布、发到哪个平台无感知；合规最终判定需结合业务与法务人工确认。")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps({
        "time": now,
        "target": os.path.abspath(root),
        "verdict": verdict,
        "release_index": score,
        "remedial": rec, "unremedial": irr,
        "findings": len(findings),
        "avoided_fix_hours": avoided_fix_hours(verdict),
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
    score = release_index(findings)

    report = build_report(root, findings, verdict, score)
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "publish_report.md")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as e:
        die("扫描报告写入失败：%s" % e, 2)

    if args.json:
        print(json.dumps({"verdict": verdict, "release_index": score,
                          "findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(report)

    if verdict in (LEVEL_HIGH, LEVEL_EXTREME):
        die("扫描判定为【%s】，建议不要直接发布（详见 %s）" % (verdict, out), 4)
    return 0


def cmd_rules(args):
    cfg = load_resource("rules.json")
    print("发布前合规检查规则总数：%d" % len(cfg.get("rules", [])))
    print("")
    labels = [
        ("meta", "发布元信息"), ("content", "内容合规"), ("legal", "法律声明"),
        ("privacy", "个人信息"), ("credential", "凭据与内网"), ("safe", "安全变体"),
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
        die("在 %s 下未找到任何 publish_report.md" % root, 1)
    total_hours = sum(r.get("avoided_fix_hours", 0) for r in records)
    counts = {"极端": 0, "高": 0, "中": 0, "低": 0}
    for r in records:
        counts[r.get("verdict", "低")] = counts.get(r.get("verdict", "低"), 0) + 1
    out = os.path.join(root, "guard-ledger.md")
    blocks = []
    blocks.append("# guard 安全控制价值账本（发布前合规检查）")
    blocks.append("")
    blocks.append("- 聚合时间：%s" % _now())
    blocks.append("- 扫描记录数：%d" % len(records))
    blocks.append("")
    blocks.append("## 判定分布")
    blocks.append("- 极端（禁止发布）：%d" % counts["极端"])
    blocks.append("- 高（拦下需确认）：%d" % counts["高"])
    blocks.append("- 中（需补清单项）：%d" % counts["中"])
    blocks.append("- 低（可信）：%d" % counts["低"])
    blocks.append("")
    blocks.append("## 价值量化")
    blocks.append("- 累计拦下估算避免损失：**约 %d 小时发布后整改与召回**" % total_hours)
    blocks.append("")
    blocks.append("> 发布是不可逆动作，发出去的东西收不回来：极限词、疗效/收益承诺、未清的密钥与个人信息，"
                  "一旦公开就是整改与召回。本账本把「没发生的发布事故」折算成可感知数字。")
    blocks.append("")
    for r in records:
        blocks.append("- [%s] %s | 判定=%s | 发布合规=%s | 可整改=%s | 避免=%dh" % (
            r.get("time", "?"), r.get("target", "?"), r.get("verdict", "?"),
            r.get("release_index", "?"), r.get("remedial", "?"), r.get("avoided_fix_hours", 0)))
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(blocks))
    except OSError as e:
        die("账本写入失败：%s" % e, 2)
    print("已生成 %s（%d 条记录，累计避免约 %d 小时）" % (out, len(records), total_hours))
    return 0


def cmd_version(args):
    print("guard-publish 引擎 v%s" % ENGINE_VERSION)
    return 0


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv):
    KNOWN = {"scan", "rules", "ledger", "version"}
    if argv and argv[0] not in KNOWN and not argv[0].startswith("-"):
        die("未知子命令：%s（可用 scan/rules/ledger/version）" % argv[0], 3)
    parser = argparse.ArgumentParser(prog="guard.py", description="guard-publish 发布合规护栏引擎")
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="扫描目录并出发布合规报告")
    p_scan.add_argument("path", nargs="?")
    p_scan.add_argument("--json", action="store_true")
    p_scan.add_argument("--out")

    sub.add_parser("rules", help="列出发布前合规检查规则库")
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
