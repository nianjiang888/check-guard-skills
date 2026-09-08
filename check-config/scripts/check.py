#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-config —— 配置与参数校验护栏（check-* 系列 #1，v2.0.0）
在配置/参数文件上线前静态扫描：必填鉴权项、类型/取值范围、明文密钥、
环境一致性、不安全协议、硬编码路径、废弃键，算验证暴露指数并出可修正性报告。
仅静态检测，不修改文件、不拦截部署。退出码 0/1/2/3/4。
"""
import os
import sys
import json
import re

ENGINE_VERSION = "2.0.0"
PKG_NAME = "check-config"

SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}
AVOID_HOURS = {"极端": 8, "高": 4, "中": 1, "低": 0}
SEV_RANK = {"极端": 4, "高": 3, "中": 2, "低": 1}

# 白名单：测试/示例/文档语境下不当命中
ALLOW_KEYWORDS = [
    "example", "sample", "demo", "test", "mock", "占位", "示例", "样例",
    "your_", "xxxx", "changeme", "placeholder", "todo", "fixme", "fake",
    "dummy", "secret_key_example", "test_password",
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


def _scan_file(path, rules, content, root):
    findings = []
    rel = os.path.relpath(path, root) if os.path.isdir(root) else os.path.basename(path)
    for rule in rules:
        if rule.get("layer") == "safe":
            continue
        rid = rule.get("id")
        sev = rule.get("severity", "中")
        recoverable = bool(rule.get("recoverable", True))
        intent = rule.get("intent", "")
        rec = rule.get("rec", "")
        hit = False
        pattern = rule.get("pattern")
        req = rule.get("req_regex")
        req_all = rule.get("req_all") or []
        absent = rule.get("absent_patterns") or []
        if pattern:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                hit = True
        elif req or req_all or absent:
            ok = True
            if req:
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
    return findings


def scan_root(root):
    rules_doc = _load_rules()
    rules = rules_doc.get("rules", [])
    findings = []
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
        if not _is_text(path):
            continue
        if _skip_file(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        findings.extend(_scan_file(path, rules, content, root))
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
        avoid += AVOID_HOURS.get(f["severity"], 0)
        if f["recoverable"]:
            fixable += 1
        else:
            unfixable += 1
    exposure = min(exposure, 100)
    verdict = top if findings else "通过"
    lines = []
    lines.append("# 配置校验报告（check-config v%s）\n" % ENGINE_VERSION)
    lines.append("扫描目标：`%s`\n" % root)
    lines.append("判定：**%s**　验证暴露指数：**%d/100**　可修正：%d / 不可修正：%d　发现项：%d　预计避免返工工时：%d\n" % (
        verdict, exposure, fixable, unfixable, len(findings), avoid))
    lines.append("\n## 发现清单\n")
    if not findings:
        lines.append("未发现配置问题。\n")
    else:
        lines.append("| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |\n")
        lines.append("|---|---|---|---|---|---|---|\n")
        for f in findings:
            lines.append("| %s | %s | %s | %s | %s | %s | %s |\n" % (
                f["severity"], f["rule"], f["layer"], f["file"], f["intent"],
                "可修正" if f["recoverable"] else "不可修正", f["rec"]))
    lines.append("\n<!-- CHECK_RESULT %s -->\n" % json.dumps({
        "verdict": verdict, "exposure_index": exposure,
        "fixable": fixable, "unfixable": unfixable,
        "findings": len(findings), "avoid_rework_hours": avoid,
    }, ensure_ascii=False))
    return "".join(lines), verdict, exposure, fixable, unfixable, len(findings), avoid


def cmd_scan(argv):
    if not argv:
        _die("缺少扫描路径（文件或目录）", 1)
    root = argv[0]
    out = argv[1] if len(argv) > 1 else "config_report.md"
    findings, rules_doc = scan_root(root)
    report, verdict, exposure, fixable, unfixable, n, avoid = build_report(root, findings, rules_doc)
    try:
        with open(out, "w", encoding="utf-8") as f:
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
        "findings": n, "avoid_rework_hours": avoid,
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
