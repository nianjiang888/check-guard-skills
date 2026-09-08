#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-tender-rejection 冒烟测试：每档样例在独立子目录中隔离实跑，
断言退出码 + 判定块字段，全 PASS 才算交付。
用法：python scripts/smoke_test.py
"""
import os
import sys
import json
import re
import shutil
import tempfile
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
CHECK_PY = os.path.join(HERE, "check.py")

# 期望：样例 -> (退出码, verdict, exposure 判定函数)
EXPECT = {
    "tender-demo-clean": (0, "通过", lambda e: e == 0),
    "tender-demo-mid":   (1, "中",   lambda e: 0 < e < 100),
    "tender-demo-high":  (4, "极端", lambda e: e == 100),
    "tender-demo-combo": (1, "高",   lambda e: e == 100),
}


def run_case(name):
    """在独立临时目录里隔离跑一个样例，避免相互污染。"""
    src = os.path.join(PKG, "examples", name + ".md")
    tmp = tempfile.mkdtemp(prefix="tender_smoke_")
    try:
        dst = os.path.join(tmp, name + ".md")
        shutil.copyfile(src, dst)
        out = os.path.join(tmp, "report.md")
        proc = subprocess.run(
            [sys.executable, CHECK_PY, "scan", dst, out],
            capture_output=True, text=True, encoding="utf-8", errors="ignore",
        )
        code = proc.returncode
        if not os.path.exists(out):
            return False, "报告未生成"
        body = open(out, encoding="utf-8").read()
        m = re.search(r"<!-- REJECTION_RESULT (\{.*?\}) -->", body, re.S)
        if not m:
            return False, "判定块缺失"
        try:
            data = json.loads(m.group(1))
        except Exception as e:
            return False, "判定块非法 JSON：%s" % e

        exp_code, exp_verdict, exp_exp = EXPECT[name]
        errs = []
        if code != exp_code:
            errs.append("退出码 %s ≠ 期望 %s" % (code, exp_code))
        if data.get("verdict") != exp_verdict:
            errs.append("判定 %s ≠ 期望 %s" % (data.get("verdict"), exp_verdict))
        if not exp_exp(data.get("exposure_index", -1)):
            errs.append("暴露指数 %s 不满足期望" % data.get("exposure_index"))
        for k in ("fixable", "unfixable", "findings", "avoid_loss", "scan_time"):
            if k not in data:
                errs.append("判定块缺字段 %s" % k)
        if data.get("fixable", 0) + data.get("unfixable", 0) != data.get("findings"):
            errs.append("可修正+不可修正 ≠ 发现项")
        return (len(errs) == 0), ("；".join(errs) if errs else "PASS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    print("check-tender-rejection 冒烟测试\n" + "-" * 52)
    all_pass = True
    for name in EXPECT:
        ok, msg = run_case(name)
        flag = "PASS" if ok else "FAIL"
        all_pass = all_pass and ok
        print("[%s] %-22s %s" % (flag, name, msg if not ok else ""))
    print("-" * 52)
    print("总结果：%s" % ("ALL PASS" if all_pass else "存在 FAIL"))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
