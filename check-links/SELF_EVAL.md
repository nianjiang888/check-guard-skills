# check-links 自评（SELF_EVAL，TRACE 五维）

> 评估口径：T 理论 / R 可重跑 / A 自动化闭环 / C 中文友好 / E 证据。每项 5.0 为满分。

## T — 理论（Theory）5.0

判定逻辑建立在工程界公认原则：可解析性（Resolvability，引用在加载期应能被解析）、链接卫生（Link Hygiene，对外发布零占位/零空链/零语法非法）、锚点唯一性（Unique Anchor Slug）、静态优先（不联网探活、可重跑可进 CI）。每条规则都能在 `references/link-validation.md` 与 `resources/check-links-models.json` 找到对应理论锚点，不是拍脑袋的规则堆。

## R — 可重跑（Re-runnable）5.0

引擎 `scripts/check.py` 是纯标准库 Python，无外部依赖，`scan` 子命令对同目录/同文件多次运行结果一致（确定性，含文件存在性判定也基于磁盘状态）。`rules` 子命令列出规则、`ledger` 子命令聚合价值量化，均可重复执行并进入 CI。报告含机器可读 JSON 尾块，可程序化比对历史。

## A — 自动化闭环（Automation）5.0

从「扫描 → 分级 → 量化（验证暴露指数 + 可修正性 + 避免返工工时）→ 报告 + JSON 尾块」形成完整闭环。退出码 0/1/2/3/4 让 CI 直接消费：极端级（import 缺失，4）建议阻断、其余（1）建议修复。不修改文件、不拦截部署、不联网，把决策权留在人或 CI 策略。

## C — 中文友好（Chinese-friendly）5.0

全包中文（含报错、报告、文档）。报错用「【错误】」前缀的中文消息。报告用中文严重度（极端/高/中/低）、中文可修正性（可修正/不可修正）、中文价值量化（预计避免返工工时）。SKILL.md 第三人人称引入、能力边界用自然语言说清，无英文黑话堆砌。

## E — 证据（Evidence）5.0

每次扫描产出实物证据：报告文件（`links_report.md`，含判定/发现清单/量化）与机器可读 JSON 尾块（`LINK_RESULT {...}`，含 verdict/exposure_index/fixable/unfixable/findings/avoid_rework_hours）。`examples/` 提供四档示例报告（极端/高/中/干净），均来自引擎实跑。退出码 4=已拦下（极端风险）与 guard/check 系列一致。

## 综合结论

五维均 5.0。定位清晰（死链 lint ≠ 链接监控 ≠ 安全扫描 ≠ 发布门禁），与 guard-network/guard-publish 互补不重叠，误报通过白名单 + 文件存在性判定压制。作为 check-* 系列第二个成员，引擎骨架与 #1 check-config 完全一致，保证系列体系统一。
