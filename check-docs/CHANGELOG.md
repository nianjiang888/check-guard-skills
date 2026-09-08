# check-docs 版本记录

## v2.0.1（2026-09-06）

- 小升级：版本号 2.0.0 → 2.0.1，便于重新发布更新；引擎逻辑未改动，冒烟测试与合规扫描均保持通过。

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列成员，定位「文档与代码一致性护栏」。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4，报告末尾附 `DOCS_RESULT {...}` 机器可读判定块。
- 6 条规则：
- DOCS-STALE-TODO（声称完成却含 TODO/FIXME/待办，中）
- DOCS-PLACEHOLDER（未填占位符 {{}}/TBD/待补充，中）
- DOCS-BROKEN-LINK（相对引用的文件/资源不存在，高）
- DOCS-ESCAPE-REF（引用逃出仓库根，中）
- DOCS-HEADING-SKIP（Markdown 标题层级跳跃，低，限 .md/.markdown/.rst）
- DOCS-CLEAN（已接 doc-sync/文档同步，safe 鼓励信号）
- 资源三件套：rules.json / check-docs-models.json / check-docs-domains.json。
- 参考三篇：docs-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_docs.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做需要语义理解/运行时/渲染才能判定的检查（详见 references/defense-stance.md），与深度版/专业审计工具分工明确。
