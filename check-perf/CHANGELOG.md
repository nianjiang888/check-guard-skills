# check-perf 版本记录

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列新成员，定位「性能阈值与资源预算护栏」（guard-* 的快检版）。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4（无 timeout 等高级问题触发 1 建议修复）。
- 6 条规则：PERF-NO-TIMEOUT（网络/IO 调用无 timeout，高）、PERF-WHILE-TRUE（while True 无限循环，中）、PERF-NPLUS1（循环内逐条查库，中）、PERF-SYNC-IN-ASYNC（async 内同步阻塞，中）、PERF-NO-PAGINATION（列表接口无分页，低）、PERF-CLEAN（已接性能分析/压测工具，safe）。
- 引擎支持 regex 全部判定形态（pattern / req_regex / req_all / absent_patterns），与模板共用框架。
- 资源三件套：rules.json / check-perf-models.json / check-perf-domains.json。
- 参考三篇：perf-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_perf.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做运行时压测，无法给出真实吞吐/延迟；只判定「是否触碰已知雷区」。这是与 guard-* 深度版的明确分工。
