# -*- coding: utf-8 -*-
"""guard-secret 主引擎：密钥 / 凭据泄露扫描。

提交 / 发布 / 提交前扫一遍，别把钥匙插在门上：
  三层检测管线（正则查精度 → 熵值查召回 → 上下文 / 白名单降误报）
  → 输出密钥类型 / 置信度 / 是否疑似已泄露
  → 生成可存档的 secret_report.md，并把"拦下的泄露"折算成可感知数字。

退出码：
  0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / 4 已拦截（高/极端风险）
"""
import sys
import os
import re
import json
import math
import argparse

ENGINE_VERSION = "2.0.0"

# 四级风险
LEVEL_LOW, LEVEL_MID, LEVEL_HIGH, LEVEL_EXTREME = "低", "中", "高", "极端"

# 严重度扣分权重（密钥暴露面指数）
SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}

# 可审的文本扩展名
TEXT_EXTS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".jsonl", ".txt",
    ".yaml", ".yml", ".toml", ".sh", ".bat", ".ps1", ".cfg", ".ini",
    ".env", ".skills", ".lock", ".html", ".csv", ".xml", ".go", ".java",
    ".rb", ".php", ".sql", ".tf", ".tfvars",
}

# 跳过的目录
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode", "dist", "build"}

# 上下文关键字
ALLOW_KEYWORDS = {
    "example", "your-", "xxxx", "dummy", "test", "testing", "placeholder",
    "changeme", "sample", "mock", "fake", "todo", "fixme", "demo", "foobar",
}
CRED_KEYWORDS = {
    "key", "secret", "token", "password", "passwd", "pwd", "credential",
    "auth", "apikey", "api_key", "private", "client_secret", "access_token",
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
# 香农熵（三层管线第二层：召回）
# ---------------------------------------------------------------------------
def shannon_entropy(s):
    """H = -Σ p(x)·log2 p(x)，按字符频率计算。"""
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    h = 0.0
    for c in freq.values():
        p = c / n
        h -= p * math.log2(p)
    return h


def classify_charset(s):
    if re.fullmatch(r"[0-9a-fA-F]+", s):
        return "hex"
    if re.fullmatch(r"[A-Za-z0-9+/=_\-]+", s):
        return "base64"
    return "generic"


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
            # 后缀匹配，如 *.lock / *.min.js
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


def candidate_tokens(text, min_len):
    """抽取候选高熵串（字母数字及常见分隔符的长串）。"""
    return [(m.group(0), m.start()) for m in
            re.finditer(r"[A-Za-z0-9+/=_-]{%d,}" % min_len, text)]


def _is_allowlisted(ctx):
    low = ctx.lower()
    return any(k in low for k in ALLOW_KEYWORDS)


def _has_cred_ctx(ctx):
    low = ctx.lower()
    return any(k in low for k in CRED_KEYWORDS)


# ---------------------------------------------------------------------------
# 三层检测管线
# ---------------------------------------------------------------------------
def scan_files(root, cfg):
    """逐文件跑三层管线：正则(精度) → 熵值(召回) → 上下文/白名单(降误报)。"""
    findings = []
    entropy_cfg = cfg.get("entropy", {})
    min_len = entropy_cfg.get("min_length", 20)
    rules = cfg.get("rules", [])
    allow_paths = set(cfg.get("allowlist", {}).get("paths", []))
    thresholds = {
        "hex": entropy_cfg.get("hex_threshold", 4.0),
        "base64": entropy_cfg.get("base64_threshold", 5.5),
        "generic": entropy_cfg.get("generic_threshold", 4.5),
    }

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

        # 第一层：正则规则（高精度）
        for rule in rules:
            pat = rule.get("pattern")
            if not pat:
                continue
            try:
                rx = re.compile(pat)
            except re.error:
                continue
            for m in rx.finditer(content):
                line_no = _line_no(content, m.start())
                snippet = lines[line_no - 1].strip() if 1 <= line_no <= len(lines) else ""
                ctx = _context_window(content, m.start(), m.end())
                if _is_allowlisted(ctx):
                    continue
                conf = "高" if _has_cred_ctx(ctx) else "中"
                sev = rule.get("severity", "高")
                leaked = sev in (LEVEL_HIGH, LEVEL_EXTREME)
                findings.append({
                    "layer": "regex", "rule_id": rule["id"], "name": rule["name"],
                    "category": rule.get("category", "未知"), "severity": sev,
                    "confidence": conf, "leaked": leaked,
                    "file": rel, "line": line_no, "snippet": snippet[:200],
                })

        # 第二+三层：高熵串（召回）+ 上下文降误报
        for tok, pos in candidate_tokens(content, min_len):
            h = shannon_entropy(tok)
            charset = classify_charset(tok)
            thr = thresholds.get(charset, thresholds["generic"])
            if h < thr:
                continue
            end = pos + len(tok)
            line_no = _line_no(content, pos)
            snippet = lines[line_no - 1].strip() if 1 <= line_no <= len(lines) else ""
            ctx = _context_window(content, pos, end)
            if _is_allowlisted(ctx):
                continue
            if _has_cred_ctx(ctx):
                sev = LEVEL_HIGH
                conf = "高"
                leaked = True
                note = "高熵串 + 凭据上下文，疑似非标准格式密钥"
            else:
                sev = LEVEL_MID
                conf = "中"
                leaked = False
                note = "高熵串无凭据上下文，可能是哈希/编码数据，需人工确认"
            findings.append({
                "layer": "entropy", "rule_id": "SEC-ENT-%s" % charset,
                "name": "高熵随机串(%s)" % charset, "category": "高熵可疑串",
                "severity": sev, "confidence": conf, "leaked": leaked,
                "file": rel, "line": line_no,
                "snippet": "%s …熵=%.2f" % (snippet[:120], h),
                "note": note,
            })

    return _dedupe(findings)


def _dedupe(findings):
    """按 (file, line, rule_id) 去重，避免同一处多次入库。"""
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
    """密钥暴露面指数（0-100）：命中严重度权重累加，封顶 100。"""
    return min(100, sum(SEV_WEIGHT.get(f["severity"], 0) for f in findings))


def avoided_loss_hours(verdict):
    return {"极端": 8, "高": 4, "中": 1, "低": 0}.get(verdict, 0)


def must_rotate(findings):
    """疑似已泄露的凭据清单（高/极端且非测试上下文）。"""
    return [f for f in findings if f.get("leaked")]


# ---------------------------------------------------------------------------
# 报告
# ---------------------------------------------------------------------------
def build_report(root, findings, verdict, score):
    now = _now()
    lines = []
    lines.append("# guard-secret 密钥泄露扫描报告")
    lines.append("")
    lines.append("- 扫描时间：%s" % now)
    lines.append("- 目标目录：%s" % os.path.abspath(root))
    lines.append("- 引擎版本：%s" % ENGINE_VERSION)
    lines.append("")
    lines.append("## 一、判定")
    lines.append("")
    lines.append("- **风险等级：%s**" % verdict)
    lines.append("- **密钥暴露面指数：%d / 100**" % score)
    lines.append("- **处置建议：%s**" % (
        "禁止提交/发布（无例外，立即轮换凭据）" if verdict == LEVEL_EXTREME
        else "拦下，人工确认后决定；疑似泄露凭据必须轮换" if verdict == LEVEL_HIGH
        else "可提交，但留意中危项（高熵无上下文串需人工确认）" if verdict == LEVEL_MID
        else "可提交"
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
        lines.append("（未发现密钥/凭据命中）")
    lines.append("")
    lines.append("## 三、命中清单")
    lines.append("")
    if findings:
        lines.append("| 严重度 | 置信度 | 类型 | 规则 | 文件:行 | 片段 |")
        lines.append("|---|---|---|---|---|---|")
        for f in findings:
            snip = f["snippet"].replace("|", "\\|").replace("\n", " ")
            lines.append("| %s | %s | %s | %s(%s) | %s:%d | %s |" % (
                f["severity"], f["confidence"], f["category"], f["name"],
                f["rule_id"], f["file"], f["line"], snip))
    else:
        lines.append("（无）")
    lines.append("")
    lines.append("## 四、疑似已泄露凭据（必须轮换）")
    lines.append("")
    rot = must_rotate(findings)
    if rot:
        for f in rot:
            lines.append("- [%s] %s @ %s:%d — %s" % (
                f["severity"], f["name"], f["file"], f["line"], f.get("note", "")))
        lines.append("")
        lines.append("> **关键纠正**：Git 里「删掉那一行」没用——历史记录里凭据仍在。"
                     "正确动作是**立即轮换凭据**（吊销旧密钥、签发新密钥），再清理代码。")
    else:
        lines.append("（未检出疑似已泄露凭据）")
    lines.append("")
    lines.append("## 五、安全控制价值量化")
    lines.append("")
    lines.append("- 本次若放行，估算可避免损失：约 %d 小时凭据轮换与事故响应" % avoided_loss_hours(verdict))
    lines.append("")
    lines.append("> 说明：本工具为静态密钥扫描，不保证 100%% 拦住所有泄露（学界共识无单点银弹）。"
                 "三层管线（正则精度 + 熵值召回 + 上下文降误报）目标精度 90–95%，"
                 "判定依据为命中的严重度优先级链，非平均。")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps({
        "time": now,
        "path": os.path.abspath(root),
        "verdict": verdict,
        "exposure_index": score,
        "findings": len(findings),
        "must_rotate": len(rot),
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

    report = build_report(root, findings, verdict, score)
    out = os.path.abspath(args.out) if args.out else os.path.join(root, "secret_report.md")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as e:
        die("扫描报告写入失败：%s" % e, 2)

    if args.json:
        print(json.dumps({
            "verdict": verdict, "exposure_index": score,
            "findings": findings,
        }, ensure_ascii=False, indent=2))
    else:
        print(report)

    if verdict in (LEVEL_HIGH, LEVEL_EXTREME):
        die("扫描判定为【%s】，建议不要提交/发布（详见 %s）" % (verdict, out), 4)
    return 0


def cmd_rules(args):
    cfg = load_resource("rules.json")
    ent = cfg.get("entropy", {})
    print("熵阈值：长度≥%d | hex>%.1f / base64>%.1f / 通用>%.1f" % (
        ent.get("min_length", 20), ent.get("hex_threshold", 4.0),
        ent.get("base64_threshold", 5.5), ent.get("generic_threshold", 4.5)))
    for r in cfg.get("rules", []):
        print("%s | %s | %s | %s" % (r["id"], r["severity"], r["category"], r["name"]))
    print("共 %d 条正则规则" % len(cfg.get("rules", [])))
    return 0


def cmd_ledger(args):
    root = os.path.abspath(args.path) if args.path else os.getcwd()
    if not os.path.isdir(root):
        die("路径不存在或不是目录：%s" % root, 1)
    records = []
    for dirpath, _, files in os.walk(root):
        if "secret_report.md" in files:
            p = os.path.join(dirpath, "secret_report.md")
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
        die("在 %s 下未找到任何 secret_report.md" % root, 1)
    total_hours = sum(r.get("avoided_loss_hours", 0) for r in records)
    total_rotate = sum(r.get("must_rotate", 0) for r in records)
    counts = {"极端": 0, "高": 0, "中": 0, "低": 0}
    for r in records:
        counts[r.get("verdict", "低")] = counts.get(r.get("verdict", "低"), 0) + 1
    out = os.path.join(root, "guard-ledger.md")
    blocks = []
    blocks.append("# guard 安全控制价值账本（密钥泄露扫描）")
    blocks.append("")
    blocks.append("- 聚合时间：%s" % _now())
    blocks.append("- 扫描记录数：%d" % len(records))
    blocks.append("")
    blocks.append("## 判定分布")
    blocks.append("- 极端（禁止）：%d" % counts["极端"])
    blocks.append("- 高（拦下需确认）：%d" % counts["高"])
    blocks.append("- 中（可提交需留意）：%d" % counts["中"])
    blocks.append("- 低（可信）：%d" % counts["低"])
    blocks.append("")
    blocks.append("## 价值量化")
    blocks.append("- 累计拦下估算避免损失：**约 %d 小时凭据轮换与事故响应**" % total_hours)
    blocks.append("- 累计需轮换凭据：**%d 条**" % total_rotate)
    blocks.append("")
    blocks.append("> 安全工具的价值天然不可见（什么都没发生 = 看起来没用）。"
                  "本账本把「没发生的泄露事故」折算成可感知数字，是续用与传播的理由。")
    blocks.append("")
    for r in records:
        blocks.append("- [%s] %s | 判定=%s | 暴露面=%s | 需轮换=%s | 避免=%dh" % (
            r.get("time", "?"), r.get("path", "?"), r.get("verdict", "?"),
            r.get("exposure_index", "?"), r.get("must_rotate", 0), r.get("avoided_loss_hours", 0)))
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(blocks))
    except OSError as e:
        die("账本写入失败：%s" % e, 2)
    print("已生成 %s（%d 条记录，累计避免约 %d 小时，需轮换 %d 条）" % (
        out, len(records), total_hours, total_rotate))
    return 0


def cmd_version(args):
    print("guard-secret 引擎 v%s" % ENGINE_VERSION)
    return 0


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv):
    KNOWN = {"scan", "rules", "ledger", "version"}
    if argv and argv[0] not in KNOWN and not argv[0].startswith("-"):
        die("未知子命令：%s（可用 scan/rules/ledger/version）" % argv[0], 3)
    parser = argparse.ArgumentParser(prog="guard.py", description="guard-secret 密钥泄露扫描引擎")
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="扫描目录并出报告")
    p_scan.add_argument("path", nargs="?")
    p_scan.add_argument("--json", action="store_true")
    p_scan.add_argument("--out")

    sub.add_parser("rules", help="列出正则规则库与熵阈值")
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
