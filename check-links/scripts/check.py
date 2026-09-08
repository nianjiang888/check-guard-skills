#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-links —— 死链 / 坏引用检测护栏（check-* 系列 #2，v2.0.0）
在文档/代码/配置上线前静态扫描：缺失的 import/include 引用、缺失的相对文件引用、
语法非法的链接、页内锚点失效、占位/示意域名、空链接、逃出仓库根的引用、
链接目标首尾空白、重复锚点。算验证暴露指数并出可修正性报告。
仅静态检测，不修改文件、不拦截部署。退出码 0/1/2/3/4。
"""
import os
import sys
import json
import re

ENGINE_VERSION = "2.0.0"
PKG_NAME = "check-links"

SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}
AVOID_HOURS = {"极端": 8, "高": 4, "中": 1, "低": 0}
SEV_RANK = {"极端": 4, "高": 3, "中": 2, "低": 1}

# 白名单：仅跳过明显是测试/示例专用的文件，避免误伤真实文档（真实文档常含 example 等词）。
ALLOW_KEYWORDS = [
    "fixture", "测试专用示例", "占位样例", "test_fixture", "dummy-fixture",
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


# ---------- 链接引用抽取 ----------
def _extract_import_refs(content):
    refs = []
    pats = [
        r'import\s+["\']([^"\']+)["\']',
        r'from\s+["\']([^"\']+)["\']\s+import',
        r'require\(\s*["\']([^"\']+)["\']\s*\)',
        r'!include\s+(\S+)',
    ]
    for p in pats:
        for m in re.finditer(p, content):
            refs.append(m.group(1).strip())
    return refs


def _looks_like_domain(t):
    return bool(re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/.*)?$', t)) and not t.startswith(('.', '/'))


def _extract_file_refs(content):
    refs = []
    # markdown 链接/图片：](target)
    for m in re.finditer(r'\]\(([^)\s]+)(?:\s+[^)]*)?\)', content):
        t = m.group(1).strip()
        if t.startswith('#') or '://' in t or t.startswith('mailto:') or _looks_like_domain(t):
            continue
        refs.append(t)
    # src= / href=
    for m in re.finditer(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', content, re.I):
        t = m.group(1).strip()
        if t.startswith('#') or '://' in t or t.startswith('mailto:') or _looks_like_domain(t):
            continue
        refs.append(t)
    # yaml 式 include/path/url（不含代码 import/require）
    for m in re.finditer(r'(?im)^\s*(?:include|path|url)\s*[:=]\s*["\']?([^"\'\s#]+)', content):
        t = m.group(1).strip()
        if '://' in t or t.startswith('#') or t.startswith('mailto:') or _looks_like_domain(t):
            continue
        refs.append(t)
    return refs


def _slugify(heading):
    s = heading.strip().lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = s.strip().replace(' ', '-')
    return s


def _extract_anchors(content):
    defined = set()
    counts = {}
    for m in re.finditer(r'^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$', content, re.M):
        h = m.group(1).strip()
        slug = _slugify(h)
        defined.add(slug)
        counts[slug] = counts.get(slug, 0) + 1
    for m in re.finditer(r'<a\s+[^>]*(?:name|id)\s*=\s*["\']([^"\']+)["\']', content, re.I):
        defined.add(m.group(1).strip().lower())
    return defined, counts


def _extract_referenced_anchors(content):
    refs = set()
    for m in re.finditer(r'\]\(#([^)\s]+)\)', content):
        refs.add(m.group(1).strip().lower())
    for m in re.finditer(r'href\s*=\s*["\']#([^"\']+)["\']', content, re.I):
        refs.add(m.group(1).strip().lower())
    return refs


def _resolve(target, filedir, root_abs):
    # 返回 ('escape'|'missing'|'ok', resolved_abs)
    if target.startswith('/'):
        cand = os.path.normpath(os.path.join(root_abs, target))
    else:
        cand = os.path.normpath(os.path.join(filedir, target))
    cand_abs = os.path.abspath(cand)
    if cand_abs != root_abs and not cand_abs.startswith(root_abs + os.sep):
        return ('escape', cand_abs)
    if os.path.exists(cand_abs):
        return ('ok', cand_abs)
    # 退一步：相对仓库根再试
    cand2 = os.path.normpath(os.path.join(root_abs, target.lstrip('./')))
    cand2_abs = os.path.abspath(cand2)
    if cand2_abs != root_abs and not cand2_abs.startswith(root_abs + os.sep):
        return ('escape', cand2_abs)
    if os.path.exists(cand2_abs):
        return ('ok', cand2_abs)
    return ('missing', cand_abs)


def _scan_file(path, rules, content, root, root_abs, cache):
    findings = []
    rel = os.path.relpath(path, root) if os.path.isdir(root) else os.path.basename(path)
    filedir = os.path.dirname(os.path.abspath(path))

    # 计算型检查前置
    if "import_refs" not in cache:
        cache["import_refs"] = _extract_import_refs(content)
        cache["file_refs"] = _extract_file_refs(content)
        cache["anchors_defined"], cache["anchor_counts"] = _extract_anchors(content)
        cache["anchors_referenced"] = _extract_referenced_anchors(content)

    for rule in rules:
        if rule.get("layer") == "safe":
            continue
        rid = rule.get("id")
        sev = rule.get("severity", "中")
        recoverable = bool(rule.get("recoverable", True))
        intent = rule.get("intent", "")
        rec = rule.get("rec", "")
        kind = rule.get("kind", "regex")
        hit = False

        if kind == "regex":
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
        elif kind == "importref":
            for t in cache["import_refs"]:
                st, _ = _resolve(t, filedir, root_abs)
                if st == "missing":
                    findings.append({
                        "rule": rid, "layer": rule.get("layer"), "severity": sev,
                        "intent": intent + "（缺失：" + t + "）", "recoverable": recoverable,
                        "rec": rec, "file": rel,
                    })
        elif kind == "fileref":
            for t in cache["file_refs"]:
                st, _ = _resolve(t, filedir, root_abs)
                if st == "missing":
                    findings.append({
                        "rule": rid, "layer": rule.get("layer"), "severity": sev,
                        "intent": intent + "（缺失：" + t + "）", "recoverable": recoverable,
                        "rec": rec, "file": rel,
                    })
        elif kind == "escaperef":
            for t in cache["file_refs"] + cache["import_refs"]:
                st, _ = _resolve(t, filedir, root_abs)
                if st == "escape":
                    findings.append({
                        "rule": rid, "layer": rule.get("layer"), "severity": sev,
                        "intent": intent + "（越界：" + t + "）", "recoverable": recoverable,
                        "rec": rec, "file": rel,
                    })
        elif kind == "anchor":
            for a in cache["anchors_referenced"]:
                if a not in cache["anchors_defined"]:
                    findings.append({
                        "rule": rid, "layer": rule.get("layer"), "severity": sev,
                        "intent": intent + "（缺失锚点：#" + a + "）", "recoverable": recoverable,
                        "rec": rec, "file": rel,
                    })
        elif kind == "dupanchor":
            for slug, c in cache["anchor_counts"].items():
                if c > 1:
                    findings.append({
                        "rule": rid, "layer": rule.get("layer"), "severity": sev,
                        "intent": intent + "（重复标题锚点：" + slug + " 出现 " + str(c) + " 次）",
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
        avoid += AVOID_HOURS.get(f["severity"], 0)
        if f["recoverable"]:
            fixable += 1
        else:
            unfixable += 1
    exposure = min(exposure, 100)
    verdict = top if findings else "通过"
    lines = []
    lines.append("# 链接校验报告（check-links v%s）\n" % ENGINE_VERSION)
    lines.append("扫描目标：`%s`\n" % root)
    lines.append("判定：**%s**　验证暴露指数：**%d/100**　可修正：%d / 不可修正：%d　发现项：%d　预计避免返工工时：%d\n" % (
        verdict, exposure, fixable, unfixable, len(findings), avoid))
    lines.append("\n## 发现清单\n")
    if not findings:
        lines.append("未发现链接问题。\n")
    else:
        lines.append("| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |\n")
        lines.append("|---|---|---|---|---|---|---|\n")
        for f in findings:
            lines.append("| %s | %s | %s | %s | %s | %s | %s |\n" % (
                f["severity"], f["rule"], f["layer"], f["file"], f["intent"],
                "可修正" if f["recoverable"] else "不可修正", f["rec"]))
    lines.append("\n<!-- LINK_RESULT %s -->\n" % json.dumps({
        "verdict": verdict, "exposure_index": exposure,
        "fixable": fixable, "unfixable": unfixable,
        "findings": len(findings), "avoid_rework_hours": avoid,
    }, ensure_ascii=False))
    return "".join(lines), verdict, exposure, fixable, unfixable, len(findings), avoid


def cmd_scan(argv):
    if not argv:
        _die("缺少扫描路径（文件或目录）", 1)
    root = argv[0]
    out = argv[1] if len(argv) > 1 else "links_report.md"
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
