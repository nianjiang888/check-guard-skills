#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-tender-rejection —— 标书废标基线护栏（check-* 系列 #12，v1.0.0）
在标书提交前静态扫描：资质文件缺失/签章漏页/工期矛盾/报价超限/格式不符/偏离招标文件。
算废标风险指数并出可修正性报告。
仅静态检测，不修改文件、不拦截提交。退出码 0/1/2/3/4。
"""
import os
import sys
import json
import re
from datetime import datetime

ENGINE_VERSION = "1.0.0"
PKG_NAME = "check-tender-rejection"

SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}
AVOID_LOSS = {"极端": 500000, "高": 100000, "中": 50000, "低": 10000}
SEV_RANK = {"极端": 4, "高": 3, "中": 2, "低": 1}

# 白名单：仅跳过明显是测试/示例专用的文件，避免误伤真实标书
ALLOW_KEYWORDS = [
    "测试专用示例", "占位样例", "test_fixture", "dummy-fixture",
]

RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "rules.json")


def _die(msg, code):
    sys.stderr.write("【错误】" + msg + "\n")
    sys.exit(code)


def _load_rules():
    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        _die("规则文件读取失败：" + str(e), 2)


def _is_text(path):
    try:
        with open(path, "rb") as f:
            chunk = f.read(4096)
    except Exception:
        return False
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
    except Exception:
        return False
    return True


def _skip_file(path):
    base = os.path.basename(path).lower()
    if base.startswith("test_") or base.startswith("example") or base.startswith("sample") or "_test." in base:
        return True
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(2000)
    except Exception:
        return False
    low = head.lower()
    return any(k.lower() in low for k in ALLOW_KEYWORDS)


def _extract_dates(content):
    """提取所有日期，用于检查工期矛盾"""
    dates = []
    # 中文日期常见写法：2026年10月15日 / 2026 年 10 月 15 日 / 2026-10-15，故数字与分隔符间允许空格
    patterns = [
        r'\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日',
        r'\d{4}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{1,2}',
    ]
    for pat in patterns:
        for m in re.finditer(pat, content):
            dates.append(m.group(0))
    return dates


def _extract_amounts(content):
    """提取所有金额，用于检查报价"""
    amounts = []
    patterns = [
        r'[¥￥]\s*\d+[\d,\.]*',
        r'\d+[\d,\.]*\s*元',
        r'\d+[\d,\.]*\s*CNY',
    ]
    for pat in patterns:
        for m in re.finditer(pat, content):
            amounts.append(m.group(0))
    return amounts


def _check_page_numbers(content):
    """检查页码连续性"""
    page_nums = []
    for m in re.finditer(r'第\s*(\d+)\s*页', content):
        page_nums.append(int(m.group(1)))
    if not page_nums:
        return None
    page_nums.sort()
    for i in range(1, len(page_nums)):
        if page_nums[i] != page_nums[i-1] + 1:
            return (page_nums[i-1], page_nums[i])
    return None


def _scan_file(path, rules, content, root, root_abs, cache):
    findings = []
    rel = os.path.relpath(path, root) if os.path.isdir(root) else os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()

    # 缓存计算结果
    if "dates" not in cache:
        cache["dates"] = _extract_dates(content)
        cache["amounts"] = _extract_amounts(content)
        cache["page_gap"] = _check_page_numbers(content)

    for rule in rules:
        if rule.get("layer") == "safe":
            continue
        rid = rule.get("id")
        sev = rule.get("severity", "中")
        recoverable = bool(rule.get("recoverable", True))
        intent = rule.get("intent", "")
        rec = rule.get("rec", "")
        kind = rule.get("kind", "regex")
        rext = rule.get("ext")
        if rext and ext not in rext:
            continue
        hit = False

        if kind == "regex":
            pattern = rule.get("pattern")
            req = rule.get("req_regex")
            req_all = rule.get("req_all") or []
            absent = rule.get("absent_patterns") or []
            ok = True
            if pattern:
                ok = bool(re.search(pattern, content, re.IGNORECASE | re.MULTILINE))
            if ok and req:
                ok = bool(re.search(req, content, re.IGNORECASE | re.MULTILINE))
            if ok and req_all:
                ok = all(re.search(r, content, re.IGNORECASE | re.MULTILINE) for r in req_all)
            if ok and absent:
                ok = not any(re.search(a, content, re.IGNORECASE | re.MULTILINE) for a in absent)
            hit = ok
            if not hit:
                continue
            findings.append({
                "rule": rid, "layer": rule.get("layer"), "severity": sev,
                "intent": intent, "recoverable": recoverable, "rec": rec, "file": rel,
            })
        elif kind == "missing_any":
            # terms 是同一事物的多种叫法（OR 关系）：全部叫法都没检出，才算真缺失。
            # 例：terms=["财务报[表告]","审计报告","资信证明"]，出现"审计报告"即视为已提供。
            # 若写成"任一未检出就报"，会大面积误报——误报会直接杀死这个工具。
            terms = rule.get("terms") or []
            if not terms:
                continue
            missed = [t for t in terms if not re.search(t, content, re.IGNORECASE | re.MULTILINE)]
            if len(missed) != len(terms):
                continue
            findings.append({
                "rule": rid, "layer": rule.get("layer"), "severity": sev,
                "intent": intent + "（未检出：" + "、".join(terms) + " 任一表述）",
                "recoverable": recoverable, "rec": rec, "file": rel,
            })
        elif kind == "date":
            dates = cache["dates"]
            min_count = int(rule.get("min_count", 2))
            if len(dates) < min_count:
                continue
            # 检查是否有矛盾的时间安排（开始日期晚于结束日期）
            # 简化版：这里只是示例，真实需要更复杂的时间解析
            findings.append({
                "rule": rid, "layer": rule.get("layer"), "severity": sev,
                "intent": intent + f"（发现 {len(dates)} 个日期，需人工核对工期安排是否矛盾）",
                "recoverable": recoverable, "rec": rec, "file": rel,
            })
        elif kind == "deadline":
            # 真正解析开工/竣工日期并比较，仅在确实倒挂时报告，避免误报
            pattern = rule.get("pattern")
            if not pattern:
                continue
            m = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if not m:
                continue
            try:
                start = tuple(int(m.group(i)) for i in (1, 2, 3))
                end = tuple(int(m.group(i)) for i in (4, 5, 6))
            except Exception:
                continue
            if start <= end:
                continue  # 工期正常，不报——宁可漏报也不可误报
            findings.append({
                "rule": rid, "layer": rule.get("layer"), "severity": sev,
                "intent": intent + "（开工 %d-%02d-%02d 晚于竣工 %d-%02d-%02d）" % (start + end),
                "recoverable": recoverable, "rec": rec, "file": rel,
            })
        elif kind == "amount":
            amounts = cache["amounts"]
            min_count = int(rule.get("min_count", 1))
            if len(amounts) < min_count:
                continue
            findings.append({
                "rule": rid, "layer": rule.get("layer"), "severity": sev,
                "intent": intent + f"（发现 {len(amounts)} 处金额表述，需核对是否超限）",
                "recoverable": recoverable, "rec": rec, "file": rel,
            })
        elif kind == "pagegap":
            gap = cache["page_gap"]
            if gap:
                findings.append({
                    "rule": rid, "layer": rule.get("layer"), "severity": sev,
                    "intent": intent + f"（页码不连续：第 {gap[0]} 页跳到第 {gap[1]} 页）",
                    "recoverable": recoverable, "rec": rec, "file": rel,
                })

    return findings


def scan_root(root):
    rules_doc = _load_rules()
    rules = rules_doc.get("rules", [])
    findings = []
    if os.path.isfile(root):
        targets = [root]
        root_abs = os.path.abspath(os.path.dirname(root))
    elif os.path.isdir(root):
        targets = []
        for dp, _, fs in os.walk(root):
            for fn in fs:
                targets.append(os.path.join(dp, fn))
        root_abs = os.path.abspath(root)
    else:
        _die("路径不存在：" + root, 2)
    for path in targets:
        if not _is_text(path):
            continue
        if _skip_file(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        cache = {}
        findings.extend(_scan_file(path, rules, content, root, root_abs, cache))
    return findings, rules_doc


def _priority(findings):
    return sorted(findings, key=lambda x: -SEV_RANK.get(x["severity"], 0))


def build_report(root, findings, rules_doc):
    findings = _priority(findings)
    top = findings[0]["severity"] if findings else "低"
    exposure = 0
    avoid = 0
    fixable = 0
    unfixable = 0
    for f in findings:
        exposure += SEV_WEIGHT.get(f["severity"], 3)
        avoid += AVOID_LOSS.get(f["severity"], 10000)
        if f["recoverable"]:
            fixable += 1
        else:
            unfixable += 1
    exposure = min(exposure, 100)
    verdict = top if findings else "通过"
    lines = []
    lines.append("# 标书废标自查报告（check-tender-rejection v%s）\n" % ENGINE_VERSION)
    lines.append("扫描目标：`%s`\n" % root)
    lines.append("判定：**%s**　废标风险指数：**%d/100**　可修正：%d / 不可修正：%d　发现项：%d　预计避免损失：¥%d\n" % (
        verdict, exposure, fixable, unfixable, len(findings), avoid))
    lines.append("\n## 发现清单\n")
    if not findings:
        lines.append("未发现废标风险。\n")
    else:
        lines.append("| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |\n")
        lines.append("|---|---|---|---|---|---|---|\n")
        for f in findings:
            lines.append("| %s | %s | %s | %s | %s | %s | %s |\n" % (
                f["severity"], f["rule"], f["layer"], f["file"], f["intent"],
                "可修正" if f["recoverable"] else "不可修正", f["rec"]))
    lines.append("\n<!-- REJECTION_RESULT %s -->\n" % json.dumps({
        "verdict": verdict, "exposure_index": exposure,
        "fixable": fixable, "unfixable": unfixable,
        "findings": len(findings), "avoid_loss": avoid,
        "scan_time": datetime.now().isoformat(),
    }, ensure_ascii=False))
    return "".join(lines), verdict, exposure, fixable, unfixable, len(findings), avoid


def cmd_scan(argv):
    if not argv:
        _die("缺少扫描路径（文件或目录）", 1)
    root = argv[0]
    out = argv[1] if len(argv) > 1 else "tender_rejection_report.md"
    findings, rules_doc = scan_root(root)
    report, verdict, exposure, fixable, unfixable, n, avoid = build_report(root, findings, rules_doc)
    try:
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(report)
    except Exception as e:
        _die("报告写入失败：" + str(e), 2)
    sys.stdout.write(report)
    if not findings:
        return 0
    if verdict == "极端":
        return 4
    return 1


def cmd_rules(argv):
    rd = _load_rules()
    for r in rd.get("rules", []):
        sys.stdout.write("%s\t%s\t%s\trecoverable=%s\n" % (
            r.get("id"), r.get("layer"), r.get("severity"), r.get("recoverable")))
    return 0


def cmd_ledger(argv):
    if not argv:
        _die("缺少扫描路径", 1)
    root = argv[0]
    findings, rules_doc = scan_root(root)
    _, verdict, exposure, fixable, unfixable, n, avoid = build_report(root, findings, rules_doc)
    sys.stdout.write(json.dumps({
        "verdict": verdict, "exposure_index": exposure,
        "fixable": fixable, "unfixable": unfixable,
        "findings": n, "avoid_loss": avoid,
        "scan_time": datetime.now().isoformat(),
    }, ensure_ascii=False) + "\n")
    return 0 if not findings else (4 if verdict == "极端" else 1)


def cmd_version(argv):
    sys.stdout.write("%s %s\n" % (PKG_NAME, ENGINE_VERSION))
    return 0


COMMANDS = {
    "scan": cmd_scan, "rules": cmd_rules, "ledger": cmd_ledger, "version": cmd_version,
}


def main(argv):
    if not argv:
        _die("未知命令：空。可用 scan/rules/ledger/version", 3)
    cmd = argv[0]
    if cmd not in COMMANDS:
        _die("未知命令：%s。可用 scan/rules/ledger/version" % cmd, 3)
    return COMMANDS[cmd](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
