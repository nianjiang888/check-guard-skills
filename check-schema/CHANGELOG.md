# check-schema 版本记录

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列成员，定位「数据 schema 校验护栏」（guard-schema 的快检版）。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4，报告末尾附 `SCHEMA_RESULT {...}` 机器可读判定块。
- 6 条规则（均 kind: regex）：SCHEMA-NO-REQUIRED（有 properties 无 required，中）、SCHEMA-NO-TYPE（有 properties 无 type，中）、SCHEMA-EMAIL-NO-FORMAT（email 类字段无 format，低）、SCHEMA-ENUM-MISSING（有限值字段无 enum，低）、SCHEMA-NO-DESCRIPTION（有 properties 无 description，低）、SCHEMA-CLEAN（已接 jsonschema/pydantic 等，safe 鼓励信号）。
- 资源三件套：rules.json / check-schema-models.json / check-schema-domains.json。
- 参考三篇：schema-check-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_schema.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做全量类型推导，无法发现「字段类型逻辑矛盾」「跨字段依赖约束」；这是与 guard-schema 深度版的明确分工。
