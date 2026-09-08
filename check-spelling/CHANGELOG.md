# check-spelling 版本记录

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列第三个成员，定位「文字质量与排版检测护栏」。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3（最高严重度「中」，不触发 4）。
- 7 条规则：SPELL-AUTH-TYPO（错别字，中）、SPELL-REPEAT-CN（中文叠字，中）、SPELL-REPEAT-EN（英文叠字，低）、SPELL-PUNCT-HALF（中文后跟半角标点，低，限散文）、SPELL-HEADING-SKIP（标题层级跳跃，低，限 Markdown）、SPELL-CJK-SPACE（中英文缺空格，低，限散文）、SPELL-CLEAN（已接校对工具，safe）。
- 错别字词典 resources/typos.json：约 30 组高频错→对。
- 量化模型与 check 系列统一：验证暴露指数 + 可修正性报告 + SPELL_RESULT 机读判定块。
- 资源三件套：rules.json / typos.json / models.json / domains.json。
- 参考三篇：spelling-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_spelling.py：8 项全 PASS；合规红线扫描 0 问题。
