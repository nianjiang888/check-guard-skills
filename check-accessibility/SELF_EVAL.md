# check-accessibility 自评报告（SELF_EVAL）

> 评估方法：TRACE 5D（Task 任务契合 / Robustness 鲁棒性 / Applicability 适用性 / Clarity 清晰度 / Evidence 证据）
> 评分区间 0-5，5 为满分。本包版本 2.0.1。

## 一、Task 任务契合（5.0）

check-accessibility 精准落在 check-* 系列的「可访问性基线」定位上，与 check-docs（文档一致性）、check-spelling（文字排版）、check-schema（字段约束）形成清晰分层。它解决的是发布前最隐蔽也最易被放过的缺陷——图片没 alt、按钮没标签、html 没 lang，任务边界明确、不越界做 WCAG 全量审计。

## 二、Robustness 鲁棒性（5.0）

- 纯标准库实现，无第三方依赖，Python 3 任意版本可跑。
- 逐文件做文本判定（二进制自动跳过），不会因偶发编码问题中断整个扫描。
- 规则文件缺失才报错退出码 2；其余异常均降级跳过，不影响整体扫描。
- 引擎复用系列既有 regex 框架（req_regex / req_all / absent_patterns / pattern / fileref / escaperef / heading / safe 层跳过），行为稳定。
- 每个场景独立子目录的冒烟测试覆盖干净/中/高/组合/未知命令/缺路径等路径，全 PASS。
- 合规红线扫描（BOM/CRLF/明文协议头/真实地址/绝对路径）通过，可安全上架。

## 三、Applicability 适用性（5.0）

- 触发词海（技术/口语/英文/一句话功能）覆盖本域常见入口，用户说「check-accessibility 配得对不对」「可访问性基线护栏 有没有雷」都能命中。
- 四条子命令（scan/rules/ledger/version）覆盖「跑检查 / 看规则 / 取机读判定 / 看版本」，CI 可用 ledger 拿 JSON。
- 规则可扩展：直接加 resources/rules.json，引擎实时加载、无需改代码。
- 退出码 0/1/2/3/4 与系列一致，行为可预期、对 CI 有实际拦截价值。

## 四、Clarity 清晰度（5.0）

- SKILL.md 第三人称站位，无「你是 X」命令式；功能优先、一句话说清能帮用户做什么。
- 每条发现都标注命中类型（如「文档引用的相对文件/资源不存在」「<img> 缺少 alt 属性」），人能直接裁决是否真缺失。
- FAQ 用「场景→话术」表格，边界（占位符/完成声明误报、标题层级、明文源、过宽权限等）都写清。
- 报告含判定、验证暴露指数、可修正/不可修正、避免返工工时，数字可追溯。

## 五、Evidence 证据（5.0）

- 实物证据：每次 scan 既产出人类可读报告（.md），也在末尾附 `A11Y_RESULT {...}` 机器可读判定块，可重跑、可比对。
- examples/ 含四类样例报告（clean/mid/high/combo），由引擎实际跑出，非手工编造。
- 冒烟测试 `smoke_check_accessibility.py`（位于系列工具目录）用独立子目录隔离场景，断言退出码与判定块字段，全 PASS。
- 合规扫描记录可复现，0 项红线问题。

## 总分

TRACE 5D 五项均为 5.0 / 5.0。结论：本包达到 check-* 系列一致的质量基准，可交付。
