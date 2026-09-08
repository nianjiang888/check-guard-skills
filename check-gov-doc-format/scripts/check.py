#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-gov-doc-format —— 公文格式终检（check-* 系列 #13，v1.0.0）
依据 GB/T 9704-2012《党政机关公文格式》与《党政机关公文处理工作条例》（中办发〔2012〕14号），
在公文印发前静态扫描格式要素错误：发文字号括号、成文日期数字、层次序数标点、
附件说明、版记抄送、主题词残留、文种合法性等。

仅静态检测，不修改文件、不拦截印发。退出码 0/1/2/3。
本域不存在一票否决级项，故不设「极端」判定，最高为「高」。
"""
import os
import sys
import json
import re
from datetime import datetime

ENGINE_VERSION = "1.0.0"
PKG_NAME = "check-gov-doc-format"

SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}
AVOID_HOURS = {"极端": 8, "高": 4, "中": 1, "低": 0}
SEV_RANK = {"极端": 4, "高": 3, "中": 2, "低": 1}

# 白名单：仅跳过明显是测试/示例专用的文件
ALLOW_KEYWORDS = ["测试专用示例", "占位样例", "test_fixture", "dummy-fixture"]

RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "rules.json")

# 单文件读取上限（字节）。超过则跳过并警告，防止把超大文件整个读进内存。
MAX_FILE_BYTES = 8 * 1024 * 1024

# 规则里允许出现正则的字段，加载时逐条编译校验
_REGEX_FIELDS = ("pattern", "req_regex", "when_regex")


def _validate_rules(rules):
    """加载期校验：正则非法的规则打印 id 并跳过，不让引擎在扫描中途崩掉。"""
    valid = []
    for rule in rules:
        rid = rule.get("id", "<无id>")
        bad = False
        for field in _REGEX_FIELDS:
            pat = rule.get(field)
            if not pat:
                continue
            try:
                re.compile(pat)
            except re.error as e:
                sys.stderr.write("【警告】规则 %s 的 %s 正则非法（%s），已跳过该规则\n" % (rid, field, e))
                bad = True
                break
        for field in ("req_all", "absent_patterns", "terms"):
            for pat in rule.get(field) or []:
                try:
                    re.compile(pat)
                except re.error as e:
                    sys.stderr.write("【警告】规则 %s 的 %s 正则非法（%s），已跳过该规则\n" % (rid, field, e))
                    bad = True
                    break
            if bad:
                break
        if not bad:
            valid.append(rule)
    return valid


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


def _scan_file(path, rules, content, root):
    """返回 (findings, manual_items)。manual 类不产生 findings，只进人工核对清单。"""
    findings = []
    manual_items = []
    rel = os.path.relpath(path, root) if os.path.isdir(root) else os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()

    for rule in rules:
        layer = rule.get("layer")
        if layer == "safe":
            continue
        rid = rule.get("id")
        sev = rule.get("severity", "中")
        basis = rule.get("basis", "—")
        intent = rule.get("intent", "")
        rec = rule.get("rec", "")
        kind = rule.get("kind", "regex")
        recoverable = bool(rule.get("recoverable", True))
        rext = rule.get("ext")
        if rext and ext not in rext:
            continue

        # 人工核对项：国标有规定但纯文本判不了（字体字号、页边距、印章位置等）。
        # 不进入 findings，不参与违规指数——避免把"需你确认"伪装成"已发现问题"。
        if kind == "manual":
            # 专项清单按文种/要素出现与否条件化，避免给通知类公文列一堆信函格式要求
            when = rule.get("when_regex")
            if when and not re.search(when, content, re.IGNORECASE | re.MULTILINE):
                continue
            manual_items.append({
                "rule": rid, "layer": layer, "basis": basis,
                "intent": intent, "standard": rule.get("standard", ""),
                "rec": rec, "severity": sev, "file": rel,
            })
            continue

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
            if not ok:
                continue
            findings.append({
                "rule": rid, "layer": layer, "severity": sev, "basis": basis,
                "intent": intent, "recoverable": recoverable, "rec": rec, "file": rel,
            })

        elif kind == "missing_any":
            terms = rule.get("terms") or []
            if not terms:
                continue
            missed = [t for t in terms if not re.search(t, content, re.IGNORECASE | re.MULTILINE)]
            if len(missed) != len(terms):
                continue
            findings.append({
                "rule": rid, "layer": layer, "severity": sev, "basis": basis,
                "intent": intent + "（未检出：" + "、".join(terms) + " 任一表述）",
                "recoverable": recoverable, "rec": rec, "file": rel,
            })

    return findings, manual_items


def scan_root(root):
    rules_doc = _load_rules()
    rules = _validate_rules(rules_doc.get("rules", []))
    findings = []
    manual_items = []
    if os.path.isfile(root):
        targets = [root]
    elif os.path.isdir(root):
        targets = []
        for dp, _, fs in os.walk(root):
            for fn in fs:
                targets.append(os.path.join(dp, fn))
    else:
        _die("路径不存在：" + root, 2)
    for path in targets:
        if not _is_text(path) or _skip_file(path):
            continue
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                sys.stderr.write("【警告】文件超过 %d MB 上限，已跳过：%s\n"
                                 % (MAX_FILE_BYTES // (1024 * 1024), path))
                continue
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        f1, m1 = _scan_file(path, rules, content, root)
        findings.extend(f1)
        manual_items.extend(m1)
    return findings, manual_items, rules_doc


def _priority(findings):
    return sorted(findings, key=lambda x: -SEV_RANK.get(x["severity"], 0))


def build_report(root, findings, manual_items, rules_doc):
    findings = _priority(findings)
    top = findings[0]["severity"] if findings else "低"
    exposure = 0
    avoid = 0
    fixable = 0
    unfixable = 0
    for f in findings:
        exposure += SEV_WEIGHT.get(f["severity"], 3)
        avoid += AVOID_HOURS.get(f["severity"], 0)
        if f["recoverable"]:
            fixable += 1
        else:
            unfixable += 1
    exposure = min(exposure, 100)
    verdict = top if findings else "通过"

    lines = []
    lines.append("# 公文格式终检报告（check-gov-doc-format v%s）\n" % ENGINE_VERSION)
    lines.append("依据：GB/T 9704-2012《党政机关公文格式》、《党政机关公文处理工作条例》（中办发〔2012〕14号）\n")
    lines.append("扫描目标：`%s`\n" % root)
    lines.append("判定：**%s**　格式违规指数：**%d/100**　可修正：%d / 不可修正：%d　发现项：%d　"
                 "预计避免返工工时（量级估算，按严重度基数累加，非精算）：%d　人工核对项：%d\n" % (
                     verdict, exposure, fixable, unfixable, len(findings), avoid, len(manual_items)))

    lines.append("\n## 一、自动检出问题\n")
    if not findings:
        lines.append("未检出格式错误。\n")
    else:
        lines.append("| 严重度 | 规则 | 国标条款 | 层 | 说明 | 可修正 | 整改建议 |\n")
        lines.append("|---|---|---|---|---|---|---|\n")
        for f in findings:
            lines.append("| %s | %s | %s | %s | %s | %s | %s |\n" % (
                f["severity"], f["rule"], f["basis"], f["layer"], f["intent"],
                "可修正" if f["recoverable"] else "不可修正", f["rec"]))

    lines.append("\n## 二、人工核对清单\n")
    lines.append("以下为国标明确规定、但纯文本无法自动判定的项（字体字号、页边距、印章位置等），"
                 "需对照原件逐一核对：\n")
    if not manual_items:
        lines.append("无。\n")
    else:
        lines.append("| 层 | 国标条款 | 核对项 | 标准值 |\n")
        lines.append("|---|---|---|---|\n")
        for m in manual_items:
            lines.append("| %s | %s | %s | %s |\n" % (
                m["layer"], m["basis"], m["intent"], m["standard"] or m["rec"]))

    lines.append("\n<!-- GOVDOC_RESULT %s -->\n" % json.dumps({
        "verdict": verdict, "exposure_index": exposure,
        "fixable": fixable, "unfixable": unfixable,
        "findings": len(findings), "manual_items": len(manual_items),
        "avoid_rework_hours": avoid, "scan_time": datetime.now().isoformat(),
    }, ensure_ascii=False))
    return "".join(lines), verdict, exposure, fixable, unfixable, len(findings), len(manual_items), avoid


def cmd_scan(argv):
    if not argv:
        _die("缺少扫描路径（文件或目录）", 1)
    root = argv[0]
    out = argv[1] if len(argv) > 1 else "govdoc_format_report.md"
    findings, manual_items, rules_doc = scan_root(root)
    report, verdict, exposure, fixable, unfixable, n, mn, avoid = build_report(
        root, findings, manual_items, rules_doc)
    try:
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(report)
    except Exception as e:
        _die("报告写入失败：" + str(e), 2)
    sys.stdout.write(report)
    return 0 if not findings else 1


def cmd_rules(argv):
    rd = _load_rules()
    auto = manual = 0
    for r in rd.get("rules", []):
        if r.get("layer") == "safe":
            continue
        if r.get("kind") == "manual":
            manual += 1
        else:
            auto += 1
        sys.stdout.write("%s\t%s\t%s\t%s\trecoverable=%s\n" % (
            r.get("id"), r.get("layer"), r.get("severity"), r.get("basis"), r.get("recoverable")))
    sys.stderr.write("自动判定规则 %d 条，人工核对项 %d 条\n" % (auto, manual))
    return 0


def cmd_ledger(argv):
    if not argv:
        _die("缺少扫描路径", 1)
    root = argv[0]
    findings, manual_items, rules_doc = scan_root(root)
    _, verdict, exposure, fixable, unfixable, n, mn, avoid = build_report(
        root, findings, manual_items, rules_doc)
    sys.stdout.write(json.dumps({
        "verdict": verdict, "exposure_index": exposure,
        "fixable": fixable, "unfixable": unfixable,
        "findings": n, "manual_items": mn,
        "avoid_rework_hours": avoid, "scan_time": datetime.now().isoformat(),
    }, ensure_ascii=False) + "\n")
    return 0 if not findings else 1


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
