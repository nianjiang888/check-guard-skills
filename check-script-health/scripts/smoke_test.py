#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-script-health 冒烟自检：四档样例隔离实跑，断言判定与各维度自洽。
运行：python scripts/smoke_test.py
"""
import os
import sys
import re
import json
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
ENGINE = os.path.join(HERE, "check.py")
EX = os.path.join(ROOT, "examples")

PY = sys.executable
PASS = 0
FAIL = 0


def run_scan(fname):
    f = os.path.join(EX, fname)
    p = subprocess.run([PY, ENGINE, "scan", f, os.devnull],
                       capture_output=True, text=True, encoding="utf-8")
    block = ""
    m = re.search(r"SCRIPT_HEALTH_RESULT (\{.*\})", p.stdout)
    if m:
        block = json.loads(m.group(1))
    return p.returncode, block, p.stdout, p.stderr


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s" % name)
    else:
        FAIL += 1
        print("  [FAIL] %s  %s" % (name, detail))


print("== check-script-health 冒烟自检 ==")

# 1) clean：0 命中，优秀，退出码 0
rc, b, out, err = run_scan("script-demo-clean.md")
check("clean 退出码=0", rc == 0, "rc=%d" % rc)
check("clean 判定=优秀", b.get("verdict") == "优秀", str(b))
check("clean 健康指数>=85", b.get("health_index", 0) >= 85, str(b))
check("clean 发现项=0", b.get("findings") == 0, str(b))
check("clean 无红线", b.get("redline") is False, str(b))
# 七维度齐全
dims = b.get("dimensions", {})
check("clean 七维度齐全", set(dims.keys()) == {"hook", "retention", "density", "cta", "compliance", "emotion", "spoken"}, str(dims))
check("clean 各维度=100", all(v == 100 for v in dims.values()), str(dims))

# 2) mid：有命中，良好，退出码 1
rc, b, out, err = run_scan("script-demo-mid.md")
check("mid 退出码=1", rc == 1, "rc=%d" % rc)
check("mid 判定=良好", b.get("verdict") == "良好", str(b))
check("mid 健康指数 65-84", 65 <= b.get("health_index", 0) <= 84, str(b))
check("mid 发现项>=4", b.get("findings", 0) >= 4, str(b))
check("mid 无红线", b.get("redline") is False, str(b))
check("mid 可修正=发现项(全可修正)", b.get("fixable") == b.get("findings"), str(b))

# 3) high：多项结构缺陷，退出码 1，非红线
rc, b, out, err = run_scan("script-demo-high.md")
check("high 退出码=1", rc == 1, "rc=%d" % rc)
check("high 无红线", b.get("redline") is False, str(b))
check("high 发现项>=8", b.get("findings", 0) >= 8, str(b))
check("high 健康指数<85", b.get("health_index", 100) < 85, str(b))
check("high 口语表达维度扣分", b.get("dimensions", {}).get("spoken", 100) < 100, str(b.get("dimensions")))

# 4) combo：命中合规红线，退出码 4
rc, b, out, err = run_scan("script-demo-combo.md")
check("combo 退出码=4", rc == 4, "rc=%d" % rc)
check("combo 红线=True", b.get("redline") is True, str(b))
check("combo 判定=红线", b.get("verdict") == "红线", str(b))
check("combo 健康指数<=40", b.get("health_index", 100) <= 40, str(b))
check("combo 合规维度扣分", b.get("dimensions", {}).get("compliance", 100) < 100, str(b.get("dimensions")))

# 5) 规则加载自洽：rules 命令可列
p = subprocess.run([PY, ENGINE, "rules"], capture_output=True, text=True, encoding="utf-8")
n = len([l for l in p.stdout.splitlines() if l.strip()])
check("rules 命令列出>=15条", n >= 15, "n=%d" % n)

print("\n结果：%d PASS / %d FAIL" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
