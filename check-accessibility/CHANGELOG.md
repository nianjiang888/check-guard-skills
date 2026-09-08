# check-accessibility 版本记录

## v2.0.1（2026-09-06）

- 小升级：版本号 2.0.0 → 2.0.1，便于重新发布更新；引擎逻辑未改动，冒烟测试与合规扫描均保持通过。

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列成员，定位「可访问性基线护栏」。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4，报告末尾附 `A11Y_RESULT {...}` 机器可读判定块。
- 6 条规则：
- A11Y-IMG-NO-ALT（<img> 缺 alt，高，限 html/htm/jsx/tsx/vue/svelte/md）
- A11Y-BTN-NO-LABEL（<button> 无文字无 aria-label，中，限组件类）
- A11Y-NO-LANG（<html> 缺 lang，中，限 html/htm）
- A11Y-NO-TITLE（无 <title>，低，限 html/htm）
- A11Y-HEADING-SKIP（标题层级跳跃，低，限 md/html/htm）
- A11Y-CLEAN（已接 a11y/无障碍，safe 鼓励信号）
- 资源三件套：rules.json / check-accessibility-models.json / check-accessibility-domains.json。
- 参考三篇：accessibility-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_accessibility.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做需要语义理解/运行时/渲染才能判定的检查（详见 references/defense-stance.md），与深度版/专业审计工具分工明确。
