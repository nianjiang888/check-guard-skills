# -*- coding: utf-8 -*-
"""guard-delete 主引擎：破坏性操作拦截。

rm -rf / DROP TABLE / git push --force 之前，先算一遍爆炸半径：
  扫描（检测破坏性模式）→ 干跑预览（列出会删哪些文件/多少行）→ 爆炸半径估算
  → 生成可存档的 blast_report.md，并把「拦下的灾难」折算成可感知数字。

设计立场：不是「禁止」，是「让你看清后果再决定」。硬禁止会逼用户 --no-verify 绕过，那是更坏结局。

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

# 严重度权重（爆炸半径指数）
SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}

# 可审的文本扩展名
TEXT_EXTS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".jsonl", ".yaml",
    ".yml", ".toml", ".sh", ".bat", ".ps1", ".cfg", ".ini", ".skills",
    ".lock", ".sql", ".sql.tmpl", ".html", ".csv", ".xml", ".env", ".rb", ".php",
}

# 跳过的目录
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode", "dist", "build"}

# 上下文白名单（示例/教学/虚构语境，命中则放过）
# 注意：本系列引擎用全局常量，不读 rules.json 的 allowlist（与 guard-secret/prompt 一致）。
ALLOW_KEYWORDS = {
    "your-", "xxxx", "dummy", "test", "testing", "placeholder",
    "changeme", "sample", "mock", "fake", "todo", "fixme", "demo", "foobar",
    "示例", "虚构", "仅为演示", "仅供测试", "教学", "练习题",
}

RC_NAME = {0: "通过", 1: "参数错", 2: "IO错", 3: "未知命令", 4: "已拦截"}


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


def _has_where_ahead(content, pos, span=400):
    """检查匹配点之后一段范围内是否出现 WHERE 子句（用于 SQL 全表/全量判定）。"""
    ahead = content[pos:pos + span]
    return bool(re.search(r"\bwhere\b", ahead, re.IGNORECASE))


# ---------------------------------------------------------------------------
# 破坏性模式检测
# ---------------------------------------------------------------------------
def scan_files(root, cfg):
    """逐文件检测破坏性操作模式，给出严重度、可逆性与爆炸半径提示。"""
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
            # 安全变体层（safe）：仅是鼓励性信号，不作为破坏性命中
            if rule.get("safe_signal"):
                continue
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
                note = ""
                # SQL 全表/全量判定：带 WHERE 则降一级，否则标注全表
                if rule.get("check_where"):
                    if _has_where_ahead(content, m.end()):
                        down = rule.get("downgrade_with_where", "中")
                        if SEV_WEIGHT.get(down, 0) < SEV_WEIGHT.get(sev, 0):
                            sev = down
                        note = "已带 WHERE，影响范围受限"
                    else:
                        note = "未带 WHERE 子句，疑似全表/全量操作"
                findings.append({
                    "layer": rule.get("layer", "delete"),
                    "rule_id": rule["id"], "name": rule["name"],
                    "category": rule.get("category", "未知"),
                    "severity": sev, "intent": rule.get("intent", ""),
                    "recoverable": rule.get("recoverable", "unknown"),
                    "note": note,
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
    """爆炸半径指数（0-100）：命中严重度权重累加，封顶 100。"""
    return min(100, sum(SEV_WEIGHT.get(f["severity"], 0) for f in findings))


def avoided_loss_hours(verdict):
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
    title = "guard-delete 破坏性操作检测报告" if mode == "scan" else "guard-delete 爆炸半径预览报告"
    lines.append("# %s" % title)
    lines.append("")
    lines.append("- 扫描时间：%s" % now)
    lines.append("- 目标：%s" % os.path.abspath(root))
    lines.append("- 引擎版本：%s" % ENGINE_VERSION)
    lines.append("")
    lines.append("## 一、判定")
    lines.append("")
    lines.append("- **风险等级：%s**" % verdict)
    lines.append("- **爆炸半径指数：%d / 100**" % score)
    rec, irr = count_recoverable(findings)
    lines.append("- **可逆性：%d 处可恢复 / %d 处不可逆**" % (rec, irr))
    lines.append("- **处置建议：%s**" % (
        "禁止执行（无例外，立即人工复核并备份）" if verdict == LEVEL_EXTREME
        else "拦下，人工确认后再决定；不可逆操作必须先备份" if verdict == LEVEL_HIGH
        else "可继续，但留意中危项（确认带 WHERE / 非强制推送）" if verdict == LEVEL_MID
        else "未发现破坏性操作"
    ))
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
        lines.append("（未发现破坏性操作模式）")
    lines.append("")
    lines.append("## 三、命中清单")
    lines.append("")
    if findings:
        lines.append("| 严重度 | 类型 | 可逆 | 规则 | 文件:行 | 片段 | 备注 |")
        lines.append("|---|---|---|---|---|---|---|")
        for f in findings:
            snip = f["snippet"].replace("|", "\\|").replace("\n", " ")
            rec = {True: "可恢复", False: "不可逆", "unknown": "未知"}[f.get("recoverable")]
            lines.append("| %s | %s | %s | %s(%s) | %s:%d | %s | %s |" % (
                f["severity"], f["category"], rec, f["name"],
                f["rule_id"], f["file"], f["line"], snip, f.get("note", "")))
    else:
        lines.append("（无）")
    lines.append("")
    lines.append("## 四、安全控制价值量化")
    lines.append("")
    lines.append("- 本次若放行，估算可避免损失：约 %d 小时事故响应与恢复" % avoided_loss_hours(verdict))
    lines.append("")
    lines.append("> 说明：本工具立场是「看清后果再决定」，不是硬禁止——硬禁止会逼用户 --no-verify 绕过，"
                 "那是更坏结局。判定依据为命中的严重度优先级链，非平均。"
                 "诚实边界：仅做静态检测，不实际执行任何破坏性命令；对运行时即时命令无感知。")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps({
        "time": now,
        "target": os.path.abspath(root),
        "verdict": verdict,
        "exposure_index": score,
        "recoverable": rec, "irrecoverable": irr,
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

    report = build_report(root, findings, verdict, score, mode="scan")
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "blast_report.md")
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
        die("扫描判定为【%s】，建议不要执行该操作（详见 %s）" % (verdict, out), 4)
    return 0


def _extract_path(target):
    """从命令字符串里抽取路径参数；抽取不到则原样返回（当作路径）。"""
    m = re.search(
        r'(?:rm\s+-[^\n]*?|rmdir\s+[^\n]*?|git\s+clean\s+-[^\n]*?|mv\s+[^\n]*?|'
        r'truncate\s+[^\n]*?|drop\s+[^\n]*?)\s+([^\s;|&]+)', target, re.IGNORECASE)
    if m:
        return m.group(1).strip("'\"")
    return target.strip().strip("'\"") if target.strip().startswith(("/", "./", "~", "../")) else target.strip()


def _is_git_tracked(path):
    cur = os.path.abspath(path)
    while True:
        if os.path.isdir(os.path.join(cur, ".git")):
            return True
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return False


def cmd_blast(args):
    if not args.target:
        die("缺少目标路径或命令（用法：guard.py blast <路径或命令>）", 1)
    target = args.target
    path = _extract_path(target)
    absp = os.path.abspath(path) if not path.startswith("/") else path

    # 极端命令直接判极端
    extreme_cmd = bool(re.search(r'rm\s+-[a-z]*r[a-z]*f[a-z]*\s+(/|~)', target)) or \
                  bool(re.search(r'rm\s+-[a-z]*r[a-z]*f[a-z]*\s+--no-verify', target))

    # 防止遍历整盘：根目录/盘符根不做 walk，直接判极端
    is_root = (absp in ("/", "\\")) or re.match(r'^[A-Za-z]:\\?$', absp) is not None
    if is_root:
        note_lines = [
            "# guard-delete 爆炸半径预览报告", "",
            "- 扫描时间：%s" % _now(),
            "- 目标：%s" % target,
            "- 解析路径：%s" % absp,
            "- 引擎版本：%s" % ENGINE_VERSION, "",
            "## 一、爆炸半径", "",
            "- **风险等级：极端**",
            "- **影响范围：根目录/盘符根，拒绝遍历整盘（可能波及全量文件）**", "",
            "## 二、建议", "",
            "- 这是最高危操作，强烈建议不要执行。",
            "- 若确需清理，请指向具体子目录并先备份。",
            "",
            "> 本预览仅做统计，不实际执行任何删除/修改命令。",
        ]
        out = os.path.abspath(args.out) if args.out else os.path.join(os.getcwd(), "blast_report.md")
        try:
            with open(out, "w", encoding="utf-8") as f:
                f.write("\n".join(note_lines))
        except OSError as e:
            die("预览报告写入失败：%s" % e, 2)
        print("\n".join(note_lines))
        die("目标为根目录/盘符根（如 rm -rf /），属于极端危险操作，强烈建议不要执行", 4)

    if os.path.isdir(absp) or (os.path.exists(absp) and os.path.isfile(absp)):
        # 干跑预览：只数不删
        file_count = 0
        total_bytes = 0
        if os.path.isdir(absp):
            for dp, _, fns in os.walk(absp):
                for fn in fns:
                    file_count += 1
                    try:
                        total_bytes += os.path.getsize(os.path.join(dp, fn))
                    except OSError:
                        pass
        else:
            file_count = 1
            try:
                total_bytes = os.path.getsize(absp)
            except OSError:
                pass
        recoverable = _is_git_tracked(absp)
        sev = "极端" if (extreme_cmd or file_count > 1000) else ("高" if file_count > 0 else "低")
        note_lines = [
            "# guard-delete 爆炸半径预览报告", "",
            "- 扫描时间：%s" % _now(),
            "- 目标：%s" % target,
            "- 解析路径：%s" % absp,
            "- 引擎版本：%s" % ENGINE_VERSION, "",
            "## 一、爆炸半径", "",
            "- **影响文件数：%d**" % file_count,
            "- **影响总大小：%.2f KB**" % (total_bytes / 1024.0),
            "- **是否可恢复：%s**" % ("是（在 git 版本库内，可 checkout/stash 还原）" if recoverable else "否（非 git 跟踪或含未跟踪文件，删除即丢失）"),
            "- **风险等级：%s**" % sev, "",
            "## 二、建议", "",
            "- 不可逆操作前先做备份：%s" % ("`git stash` 或打 tag 后再操作" if recoverable else "先复制一份到安全位置"),
            "- 能用可逆替代就别硬删：如 `mv` 进回收站目录而非 `rm -rf`",
            "- 强制推送（git push -f）会改写历史，务必确认目标分支与远端状态",
            "",
            "> 本预览仅做统计，不实际执行任何删除/修改命令。",
        ]
        out = os.path.abspath(args.out) if args.out else os.path.join(os.getcwd(), "blast_report.md")
        try:
            with open(out, "w", encoding="utf-8") as f:
                f.write("\n".join(note_lines))
        except OSError as e:
            die("预览报告写入失败：%s" % e, 2)
        print("\n".join(note_lines))
        # 预览工具本身不拦截（rc=0）；极端命令额外提示
        if extreme_cmd:
            die("目标为极端危险命令（如 rm -rf /），强烈建议不要执行", 4)
        return 0
    else:
        # 路径不存在：仍提示命令危险性
        if extreme_cmd:
            die("命令含极端危险模式（如 rm -rf /），强烈建议不要执行", 4)
        print("目标路径不存在：%s（无法估算爆炸半径；若这是命令，请确认其危险性）" % absp)
        return 0


def cmd_rules(args):
    cfg = load_resource("rules.json")
    print("破坏性操作模式总数：%d" % len(cfg.get("rules", [])))
    print("")
    for layer, label in (("dos", "拒绝服务"), ("delete", "删除"), ("db", "数据库"),
                          ("vcs", "版本控制"), ("file", "文件"), ("perm", "权限"), ("safe", "安全变体")):
        rs = [r for r in cfg.get("rules", []) if r.get("layer") == layer]
        if not rs:
            continue
        print("== %s（%d 条）==" % (label, len(rs)))
        for r in rs:
            rec = {True: "可恢复", False: "不可逆", "unknown": "未知"}[r.get("recoverable")]
            print("  %s | %s | %s | %s | %s" % (r["id"], r["severity"], r["category"], r["name"], rec))
    return 0


def cmd_ledger(args):
    root = os.path.abspath(args.path) if args.path else os.getcwd()
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)
    records = []
    for dirpath, _, files in os.walk(root):
        if "blast_report.md" in files:
            p = os.path.join(dirpath, "blast_report.md")
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
        die("在 %s 下未找到任何 blast_report.md" % root, 1)
    total_hours = sum(r.get("avoided_loss_hours", 0) for r in records)
    counts = {"极端": 0, "高": 0, "中": 0, "低": 0}
    for r in records:
        counts[r.get("verdict", "低")] = counts.get(r.get("verdict", "低"), 0) + 1
    out = os.path.join(root, "guard-ledger.md")
    blocks = []
    blocks.append("# guard 安全控制价值账本（破坏性操作拦截）")
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
    blocks.append("- 累计拦下估算避免损失：**约 %d 小时事故响应与恢复**" % total_hours)
    blocks.append("")
    blocks.append("> 破坏性操作的代价天然隐蔽（删完才看见）。本账本把「没发生的灾难」折算成可感知数字。")
    blocks.append("")
    for r in records:
        blocks.append("- [%s] %s | 判定=%s | 爆炸半径=%s | 可恢复=%s | 避免=%dh" % (
            r.get("time", "?"), r.get("target", "?"), r.get("verdict", "?"),
            r.get("exposure_index", "?"), r.get("recoverable", "?"), r.get("avoided_loss_hours", 0)))
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(blocks))
    except OSError as e:
        die("账本写入失败：%s" % e, 2)
    print("已生成 %s（%d 条记录，累计避免约 %d 小时）" % (out, len(records), total_hours))
    return 0


def cmd_version(args):
    print("guard-delete 引擎 v%s" % ENGINE_VERSION)
    return 0


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv):
    KNOWN = {"scan", "blast", "rules", "ledger", "version"}
    if argv and argv[0] not in KNOWN and not argv[0].startswith("-"):
        die("未知子命令：%s（可用 scan/blast/rules/ledger/version）" % argv[0], 3)
    parser = argparse.ArgumentParser(prog="guard.py", description="guard-delete 破坏性操作拦截引擎")
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="扫描目录并出报告")
    p_scan.add_argument("path", nargs="?")
    p_scan.add_argument("--json", action="store_true")
    p_scan.add_argument("--out")

    p_blast = sub.add_parser("blast", help="干跑预览破坏性命令的爆炸半径")
    p_blast.add_argument("target", nargs="?")
    p_blast.add_argument("--out")

    sub.add_parser("rules", help="列出破坏性操作规则库")
    p_ledger = sub.add_parser("ledger", help="聚合扫描报告生成价值账本")
    p_ledger.add_argument("path", nargs="?")
    sub.add_parser("version", help="打印引擎版本")

    args = parser.parse_args(argv)
    if not args.cmd or args.cmd == "version":
        return cmd_version(args)

    dispatch = {
        "scan": cmd_scan, "blast": cmd_blast, "rules": cmd_rules, "ledger": cmd_ledger,
    }
    if args.cmd not in dispatch:
        die("未知子命令：%s（可用 scan/blast/rules/ledger/version）" % args.cmd, 3)
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
