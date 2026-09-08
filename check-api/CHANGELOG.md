# check-api 版本记录

## v2.0.1（2026-09-06）

- 小升级：版本号 2.0.0 → 2.0.1，便于重新发布更新；引擎逻辑未改动，冒烟测试与合规扫描均保持通过。

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列新成员，定位「API 契约一致性护栏」。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4（高级契约问题触发 1 建议修复后发布；极端级保留与系列一致）。
- 6 条规则（均 regex）：API-NO-RESPONSE-SCHEMA（漏写 responses，中）、API-NO-ERROR-RESPONSE（缺 4xx/5xx 错误响应，中）、API-GET-WITH-BODY（GET 带 requestBody，高）、API-NO-AUTH（无鉴权声明，中）、API-NO-DESCRIPTION（无 description，低）、API-CLEAN（已接规范工具，safe 仅鼓励）。
- 资源三件套：rules.json / check-api-models.json / check-api-domains.json。
- 参考三篇：api-contract-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_api.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做语义级 schema 校验，无法发现「字段类型错/必填漏标」；这是与专业 OpenAPI linter 的明确分工。
