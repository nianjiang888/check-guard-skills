#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-script-health —— 短视频脚本体检评分（check-* 系列，v1.0.0）
在脚本开拍/发布前静态体检：开头钩子、完播留人、信息密度、互动引导、合规安全、情绪共鸣、口语表达
七维度打分，算「完播健康指数(0-100)」并出可修正性报告。
仅静态检测，不修改文件、不替代创作判断。退出码 0/1/2/3/4。
"""
import os
import sys
import json
import re
from datetime import datetime

ENGINE_VERSION = "1.0.0"
PKG_NAME = "check-script-health"

SEV_WEIGHT = {"极端": 100, "高": 40, "中": 12, "低": 3}
SEV_RANK = {"极端": 4, "高": 3, "中": 2, "低": 1}

# 仅跳过明显是测试/示例专用文件，避免误伤真实脚本
ALLOW_KEYWORDS = ["测试专用示例", "占位样例", "test_fixture", "dummy-fixture"]

HOOK_RE = re.compile(
    r"(你|您).{0,16}(知道|发现|注意|别|有没有|试过|敢|信|猜|想过|遇到)"
    r"|(居然|竟然|没想到|其实|原来|秘密|真相|警告|重点|揭秘|别再|为什么|如何|怎样|这样|千万别|一般人|大多数人|以为是|错了|错在哪)"
    r"|[？?]"
    r"|(第[一二三四五六]个|三招|五个|三步|一招|两种方法|两个套路)"
)

CTA_RE = re.compile(
    r"(点赞|关注|转发|收藏|评论|下期|主页|订阅|记得|别忘了|点个|三连|双击|左下角|评论区|说说你的|你敢|你试过|你遇到过)"
)

BOOKISH = ["综上所述", "然而", "因此", "基于", "鉴于", "值得注意的是", "换言之",
           "不难发现", "由此可见", "总而言之", "毋庸置疑", "众所周知", "诚然",
           "固然", "毋容置疑", "事实上", "换言之"]

FILLERS = ["啊", "呢", "吧", "嘛", "就是说", "那个", "然后", "对吧", "懂吧",
           "其实吧", "怎么说呢", "这个", "呃", "额", "的话", "就是说"]

RULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "rules.json")


def _die(msg, code):
    sys.stderr.write("【错误】" + msg + "\n")
    sys.exit(code)


def _load_rules():
    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        _die("规则文件读取失败：" + str(e), 2)
    # 规则加载期逐条校验正则，坏正则跳过不崩（#2 反哺的工程缺口）
    good = []
    for r in doc.get("rules", []):
        for key in ("pattern", "patterns"):
            pats = r.get(key)
            if not pats:
                continue
            pats = pats if isinstance(pats, list) else [pats]
            for p in pats:
                try:
                    re.compile(p)
                except Exception:
                    sys.stderr.write("【警告】规则 %s 正则非法已跳过：%s\n" % (r.get("id"), p))
                    r["_bad"] = True
        if not r.get("_bad"):
            good.append(r)
    doc["rules"] = good
    return doc


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


# ---------- 特殊体检函数 ----------

def _opening_has_hook(content):
    head = content[:90]
    return bool(HOOK_RE.search(head))


def _opening_has_addr(content):
    head = content[:120]
    return bool(re.search(r"(你|您)", head))


def _ending_has_cta(content):
    tail = content[-120:]
    return bool(CTA_RE.search(tail))


def _find_repeated_phrases(content):
    # 按标点拆句，找长度>=4且出现>=2次的重复短语（车轱辘话）
    parts = re.split(r"[，。！？、；：\n\r“”\"'（）()]", content)
    phrases = [p.strip() for p in parts if len(p.strip()) >= 4]
    seen = {}
    for p in phrases:
        seen[p] = seen.get(p, 0) + 1
    dups = [p for p, c in seen.items() if c >= 2]
    return dups


def _filler_ratio(content):
    total = len(content)
    if total == 0:
        return 0, 0
    cnt = 0
    for f in FILLERS:
        cnt += content.count(f)
    return cnt, cnt  # 返回出现次数与加权计数（此处等权）


def _detect_duration(content):
    m = re.search(r"时长[:：]?\s*(\d+)\s*(秒|s|分钟|min)", content)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if unit in ("分钟", "min"):
            return n * 60
        return n
    return None


def _is_bookish(content):
    return any(b in content for b in BOOKISH)


def _long_sentence(content, limit=45):
    pieces = re.split(r"[。！？!?；;：:\n\r]", content)
    for p in pieces:
        if len(p.strip()) > limit:
            return p.strip()
    return None


# --------------------------------

def _scan_file(path, rules, content, root):
    findings = []
    rel = os.path.relpath(path, root) if os.path.isdir(root) else os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()
    duration = _detect_duration(content)
    filler_cnt, _ = _filler_ratio(content)

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
        detail = ""

        if kind == "regex_present":
            pats = rule.get("patterns") or ([rule["pattern"]] if rule.get("pattern") else [])
            for p in pats:
                m = re.search(p, content, re.IGNORECASE)
                if m:
                    hit = True
                    detail = "（命中：「%s」）" % m.group(0)
                    break
        elif kind == "missing_any":
            terms = rule.get("terms") or []
            if not terms:
                continue
            missed = [t for t in terms if not re.search(t, content, re.IGNORECASE | re.MULTILINE)]
            if len(missed) != len(terms):
                continue
            hit = True
        elif kind == "opening":
            if not _opening_has_hook(content):
                hit = True
        elif kind == "opening_addr":
            if not _opening_has_addr(content):
                hit = True
        elif kind == "ending":
            if not _ending_has_cta(content):
                hit = True
        elif kind == "repetition":
            dups = _find_repeated_phrases(content)
            if dups:
                hit = True
                detail = "（重复表达：%s）" % "、".join(dups[:3])
        elif kind == "density":
            # 水词过多：出现次数>=8 且 占比过高（每 40 字一个以上水词）
            if filler_cnt >= 8 and filler_cnt > len(content) / 40.0:
                hit = True
                detail = "（水词出现 %d 次）" % filler_cnt
        elif kind == "length":
            rec_min, rec_max = 3.0, 4.5
            dur = duration or 60
            lo = int(dur * rec_min * 0.5)
            hi = int(dur * rec_max * 2.0)
            n = len(content)
            if n < lo or n > hi:
                hit = True
                detail = "（脚本 %d 字，%s秒视频建议 %d–%d 字）" % (
                    n, ("%d" % dur), int(dur * rec_min), int(dur * rec_max))
        elif kind == "spoken":
            if _is_bookish(content):
                hit = True
                detail = "（书面连词：%s）" % "、".join([b for b in BOOKISH if b in content][:2])
        elif kind == "long_sentence":
            ls = _long_sentence(content, 45)
            if ls:
                hit = True
                detail = "（长句 %d 字：%s…）" % (len(ls), ls[:18])

        if not hit:
            continue
        findings.append({
            "rule": rid, "layer": rule.get("layer"), "severity": sev,
            "intent": intent + detail, "recoverable": recoverable,
            "rec": rec, "file": rel,
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


def _dimension_scores(findings, rules_doc):
    weights = rules_doc.get("meta", {}).get("layer_weights", {})
    layers = list(weights.keys())
    pen = {l: 0 for l in layers}
    for f in findings:
        l = f.get("layer")
        if l in pen:
            pen[l] += SEV_WEIGHT.get(f["severity"], 3)
    scores = {}
    for l in layers:
        scores[l] = max(0, 100 - pen[l])
    return scores, weights


def build_report(root, findings, rules_doc):
    findings = _priority(findings)
    meta = rules_doc.get("meta", {})
    weights = meta.get("layer_weights", {})
    scores, _ = _dimension_scores(findings, rules_doc)
    redline = meta.get("redline_severity", "极端")

    # 健康指数 = 各维度加权均值
    if weights:
        health = round(sum(scores[l] * w for l, w in weights.items()))
    else:
        health = round(sum(scores.values()) / max(1, len(scores)))

    # 合规红线：任意极端命中强制低分
    has_redline = any(f["severity"] == redline for f in findings)
    if has_redline:
        health = min(health, 40)
        verdict = "红线"
    else:
        if health >= 85:
            verdict = "优秀"
        elif health >= 70:
            verdict = "良好"
        elif health >= 50:
            verdict = "一般"
        else:
            verdict = "偏弱"

    fixable = sum(1 for f in findings if f["recoverable"])
    unfixable = len(findings) - fixable

    lines = []
    lines.append("# 短视频脚本体检报告（check-script-health v%s）\n" % ENGINE_VERSION)
    lines.append("扫描目标：`%s`\n" % root)
    lines.append("判定：**%s**　完播健康指数：**%d/100**　可修正：%d / 不可修正：%d　发现项：%d%s\n" % (
        verdict, health, fixable, unfixable, len(findings),
        "　⚠️ 命中合规红线" if has_redline else ""))
    lines.append("\n## 七维度评分\n")
    layer_names = {
        "hook": "开头钩子", "retention": "完播留人", "density": "信息密度",
        "cta": "互动引导", "compliance": "合规安全", "emotion": "情绪共鸣", "spoken": "口语表达",
    }
    lines.append("| 维度 | 得分 | 权重 |\n|---|---|---|\n")
    for l, w in weights.items():
        lines.append("| %s | %d | %.0f%% |\n" % (layer_names.get(l, l), scores[l], w * 100))
    lines.append("\n## 发现清单\n")
    if not findings:
        lines.append("未发现明显问题，脚本体检通过。\n")
    else:
        lines.append("| 严重度 | 规则 | 维度 | 文件 | 说明 | 可修正 | 建议 |\n")
        lines.append("|---|---|---|---|---|---|---|\n")
        for f in findings:
            lines.append("| %s | %s | %s | %s | %s | %s | %s |\n" % (
                f["severity"], f["rule"], layer_names.get(f["layer"], f["layer"]),
                f["file"], f["intent"], "可修正" if f["recoverable"] else "不可修正", f["rec"]))
    lines.append("\n<!-- SCRIPT_HEALTH_RESULT %s -->\n" % json.dumps({
        "verdict": verdict, "health_index": health, "redline": has_redline,
        "dimensions": scores, "fixable": fixable, "unfixable": unfixable,
        "findings": len(findings), "scan_time": datetime.now().isoformat(),
    }, ensure_ascii=False))
    return "".join(lines), verdict, health, has_redline, fixable, unfixable, len(findings), scores


def cmd_scan(argv):
    if not argv:
        _die("缺少扫描路径（文件或目录）", 1)
    root = argv[0]
    out = argv[1] if len(argv) > 1 else "script_health_report.md"
    findings, rules_doc = scan_root(root)
    report, verdict, health, redline, fixable, unfixable, n, scores = build_report(root, findings, rules_doc)
    try:
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(report)
    except Exception as e:
        _die("报告写入失败：" + str(e), 2)
    sys.stdout.write(report)
    if not findings:
        return 0
    if redline:
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
    _, verdict, health, redline, fixable, unfixable, n, scores = build_report(root, findings, rules_doc)
    sys.stdout.write(json.dumps({
        "verdict": verdict, "health_index": health, "redline": redline,
        "dimensions": scores, "fixable": fixable, "unfixable": unfixable,
        "findings": n, "scan_time": datetime.now().isoformat(),
    }, ensure_ascii=False) + "\n")
    return 0 if not findings else (4 if redline else 1)


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
