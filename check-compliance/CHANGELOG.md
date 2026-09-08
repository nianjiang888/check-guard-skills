# check-compliance 版本记录

## v2.0.1（2026-09-06）

- 小升级：版本号 2.0.0 → 2.0.1，便于重新发布更新；引擎逻辑未改动，冒烟测试与合规扫描均保持通过。

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列新成员，定位「合规点检护栏」（guard-publish 的快检版）。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4（本包最高「高」，实际返回 1；4 保留与系列一致）。
- 6 条规则（均 regex）：COMPLIANCE-SUPERLATIVE（极限词，高）、COMPLIANCE-NO-DISCLAIMER（缺免责声明，中，req_regex+absent_patterns）、COMPLIANCE-NO-SOURCE（缺数据来源，中，req_regex+absent_patterns）、COMPLIANCE-PII（未脱敏 PII，中，pattern）、COMPLIANCE-NO-DATE（缺发布日期，低，absent_patterns）、COMPLIANCE-CLEAN（已接合规流程，safe，鼓励信号不计入）。
- 引擎复用系列统一 regex 框架（pattern / req_regex / req_all / absent_patterns），与 safe 层跳过逻辑共用；无 knownprefix/filename 规则。
- 资源三件套：rules.json / check-compliance-models.json / check-compliance-domains.json（替代模板的 secret-patterns.json）。
- 参考三篇：compliance-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 报告标题「合规点检报告（check-compliance v2.0.0）」，末尾 `COMPLIANCE_RESULT {...}` 机器可读判定块。
- 冒烟测试 smoke_check_compliance.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做全量语义理解，无法发现「话术包装后的隐性违规」；这是与 guard-publish 深度版的明确分工。
