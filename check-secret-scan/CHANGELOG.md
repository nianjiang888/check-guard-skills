# check-secret-scan 版本记录

## v2.0.1（2026-09-06）

- 小升级：补发评测报告。此前 v2.0.0 随 check-* 系列上架时，冒烟测试只放在 `_tools/smoke_check_secret_scan.py`，包内缺 `scripts/smoke_test.py`，导致发布件无可运行评测报告。
- 将冒烟测试集成进包内 `scripts/smoke_test.py`（自包含：相对路径 + `sys.executable`，不依赖外部 `_tools`），并让其在跑完后自动写出 `EVALUATION_REPORT.md`（评测报告），覆盖四档场景 + 子命令可用性 + 合规结论 + TRACE 5D 摘要。
- 复跑结果：8 PASS / 0 FAIL（extreme/high/mid/clean 四档判定、退出码、可修正/不可修正/发现项全自洽；rules/version/未知命令 rc=3/缺路径 rc=1 均 PASS）。
- 合规红线扫描：RED-LINE PASS 0 问题。
- 版本号 2.0.0 → 2.0.1（仅交付物补齐，引擎逻辑未改）。

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列第四个成员，定位「密钥明文快检护栏」（guard-secret 的快检版）。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4（明文私钥/已知前缀密钥触发 4 建议阻断）。
- 6 条规则：SECRET-PRIVATE-KEY（PEM 私钥块，极端）、SECRET-KNOWN-PREFIX（已知前缀明文密钥，极端，加载 secret-patterns.json）、SECRET-HARDCODED-CRED（password/secret/token/key=值，高）、SECRET-URL-CREDENTIAL（地址内嵌 user:pass，高）、SECRET-ENV-FILE（被提交的 .env，中，按文件名命中）、SECRET-CLEAN（已接密钥扫描工具，safe）。
- 引擎新增两类计算检查：knownprefix（加载前缀库逐条正则命中、标注厂商名）、filename（按文件名命中 .env），与既有 regex 共用框架。
- 资源四件套：rules.json / secret-patterns.json / models.json / domains.json。
- 参考三篇：secret-scan-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_secret_scan.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做全量熵分析，无法发现「无前缀的高熵随机密钥」；这是与 guard-secret 深度版的明确分工。
