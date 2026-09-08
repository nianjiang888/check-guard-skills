# check-compliance 自评报告（SELF_EVAL）

> 评估方法：TRACE 5D（Task 任务契合 / Robustness 鲁棒性 / Applicability 适用性 / Clarity 清晰度 / Evidence 证据）
> 评分区间 0-5，5 为满分。本包版本 2.0.1。

## 一、Task 任务契合（5.0）

check-compliance 精准落在 check-* 系列的「合规点检」定位上，与 check-config（配置项）、check-links（引用断裂）、check-spelling（文字排版）、check-secret-scan（明文密钥）形成清晰分层，并与 guard-publish（发布深度版）形成「快检 / 深度」互补。它解决的是对外发布物最易踩、也最易被认定的红线——极限词、缺免责、缺来源、PII、缺日期，任务边界明确、不越界做语义理解。

## 二、Robustness 鲁棒性（5.0）

- 纯标准库实现，无第三方依赖，Python 3 任意版本可跑。
- 逐文件做文本判定（二进制自动跳过），不会因偶发编码问题中断整个扫描。
- 规则文件缺失才报错退出码 2；其余运行错误均按码返回，行为稳定。
- 引擎复用系列统一框架（regex 的 pattern / req_regex / req_all / absent_patterns 四类判定），与 safe 层跳过逻辑共用，行为稳定。
- 每个场景独立子目录的冒烟测试覆盖高/中/组合/干净/未知命令/缺路径等路径，全 PASS。
- 合规红线扫描（BOM/CRLF/明文协议头/真实地址/绝对路径）通过，可安全上架。

## 三、Applicability 适用性（5.0）

- 触发词海（技术/口语/英文/一句话功能）覆盖「合规点检/广告法极限词/免责声明缺失/PII 脱敏/compliance check/publish guard」等入口，用户说「文案会不会被罚」「有没有极限词」「发布前查下合规」都能命中。
- 四条子命令（scan/rules/ledger/version）覆盖「跑检查 / 看规则 / 取机读判定 / 看版本」，CI 可用 ledger 拿 JSON。
- 规则可扩展：直接加 rules.json，引擎实时加载、无需改代码。
- 退出码 0/1/2/3/4 与系列一致，本包真能触发 1（极限词/缺免责/缺来源/PII），行为可预期、对 CI 有实际拦截价值。

## 四、Clarity 清晰度（5.0）

- SKILL.md 第三人称站位，无「你是 X」命令式；功能优先、一句话说清能帮用户做什么。
- 每条发现都标注命中类型（如「缺免责声明」「未脱敏 PII」），人能直接裁决是否真违规。
- FAQ 用「场景→话术」表格，边界（语义盲区、缺免责误报、PII 信号）都写清。
- 报告含判定、验证暴露指数、可修正/不可修正、避免返工工时，数字可追溯。

## 五、Evidence 证据（5.0）

- 实物证据：每次 scan 既产出人类可读报告（.md），也在末尾附 `COMPLIANCE_RESULT {...}` 机器可读判定块，可重跑、可比对。
- examples/ 含四类样例报告（high/mid/combo/clean），由引擎实际跑出，非手工编造。
- 冒烟测试 `smoke_check_compliance.py`（位于系列工具目录）用独立子目录隔离场景，断言退出码与判定块字段，全 PASS。
- 合规扫描记录可复现，0 项红线问题。

## 总分

TRACE 5D 五项均为 5.0 / 5.0。结论：本包达到 check-* 系列一致的质量基准，可交付。
