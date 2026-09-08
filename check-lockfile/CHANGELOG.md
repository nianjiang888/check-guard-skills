# check-lockfile 版本记录

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列成员，定位「依赖锁定完整性护栏」。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4，报告末尾附 `LOCK_RESULT {...}` 机器可读判定块。
- 5 条规则：
- LOCK-FLOATING（仍含浮动版本 ^~>=*x，中）
- LOCK-NO-INTEGRITY（依赖条目无完整性哈希，中）
- LOCK-HTTP-SOURCE（从明文 http 源拉取，高）
- LOCK-UNRESOLVED（含未解析标记 unresolved/extraneous/missing，中）
- LOCK-CLEAN（已启依赖锁定与完整性校验，safe 鼓励信号）
- 资源三件套：rules.json / check-lockfile-models.json / check-lockfile-domains.json。
- 参考三篇：lockfile-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_lockfile.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做需要语义理解/运行时/渲染才能判定的检查（详见 references/defense-stance.md），与深度版/专业审计工具分工明确。
