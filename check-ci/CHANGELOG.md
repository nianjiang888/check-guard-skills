# check-ci 版本记录

## v2.0.0（2026-09-02）

- 初版交付，check-* 系列成员，定位「CI 配置护栏」。
- 引擎 scripts/check.py：纯标准库，确定性、可重跑，退出码 0/1/2/3/4，报告末尾附 `CI_RESULT {...}` 机器可读判定块。
- 5 条规则：
- CI-NO-TIMEOUT（任务未设超时，中，限 yml/yaml）
- CI-SECRET-PLAIN（明文写了密码/令牌/密钥，高，限 yml/yaml）
- CI-PERMISSIONS-WIDE（授予过宽权限 write-all/contents: write，中，限 yml/yaml）
- CI-NO-TRIGGER（工作流无触发条件，高，限 yml/yaml）
- CI-CLEAN（已接 pipeline lint/CI 校验，safe 鼓励信号）
- 资源三件套：rules.json / check-ci-models.json / check-ci-domains.json。
- 参考三篇：ci-methodology / common-pitfalls / defense-stance。
- 交付物：SKILL.md、FAQ.md、README.md、SELF_EVAL.md（TRACE 5D 全 5.0）、CHANGELOG.md、examples×4。
- 冒烟测试 smoke_check_ci.py：全 PASS；合规红线扫描 0 问题。
- 诚实边界：不做需要语义理解/运行时/渲染才能判定的检查（详见 references/defense-stance.md），与深度版/专业审计工具分工明确。
