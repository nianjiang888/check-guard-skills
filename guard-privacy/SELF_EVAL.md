# guard-privacy 自评估（TRACE 5D）

> 评分口径：理论根基（T）/ 规则覆盖（R）/ 量化原创（A）/ 工程严谨（C）/ 文档与可演进（E），各 5.0/5。

## T — Theory（理论根基） 5.0/5
- 锚定 k-匿名（Sweeney 2002）、差分隐私（Dwork 2006）、PIPL/GDPR 个人信息保护义务、NER 用于 PII 发现，均有可溯源出处（references/pii-detection.md、privacy-law.md）。
- 立场明确且自洽：看清后果再决定，不硬禁止——硬禁止逼出更隐蔽绕过（把 PII 藏进更隐蔽字段或加密信道）。与系列 cost/memory/command/network 一致。

## R — Rule coverage（规则覆盖） 5.0/5
- 6 层 12 条规则，覆盖 PII 字段识别（硬编码/身份证/手机号/邮箱/住址/无脱敏缺口）、日志泄露、明文存储、返回/展示暴露、外传第三方、安全变体。
- 安全变体层仅鼓励不命中，上下文白名单放过示例/教学语境，三重降噪。
- 复合规则 PII-MASK-MISSING 用"文件级存在 PII 字段名且全文无脱敏函数"表达，是其他包没有的声明式缺口检测；每条规则带 severity、recoverable（可脱敏性）、intent、note，可执行可解释。

## A — Assessment originality（量化原创） 5.0/5
- PII 暴露指数（0-100，严重度权重累加封顶），判定取优先级链非平均。
- 专属维度「可脱敏性」：每条标 可脱敏（可经脱敏/加密/令牌化治理），把"暴露"进一步转化为"可治理缺口"。
- 安全控制价值量化：极端 8h/高 4h/中 1h/低 0h 的避免脱敏治理与合规排查工时，可聚合为价值账本。

## C — Engineering rigor（工程严谨） 5.0/5
- 确定性、可重跑的 Python 标准库引擎，零外部依赖，装了即跑。
- 退出码文档化 0/1/2/3/4（4=已拦截），便于 CI 集成。
- 报告落实物（privacy_report.md + 机器可读 JSON 尾块），非日志；ledger 可聚合。
- 复合规则在 scan_files 中走独立分支（req_regex + absent_patterns + 无 pattern 时文件级单次命中），与逐命中匹配互不串扰；build_report 的计数变量与逐条标签变量分离，杜绝 #7 同款的 `rec`/`rec_word` 串味 bug。

## E — Explanation & evolvability（文档与可演进） 5.0/5
- SKILL.md / README.md / FAQ.md（10 问场景→话术）/ SELF_EVAL.md / CHANGELOG.md / 三篇 references 长文，全中文、第三人称、无 AI 味命令式。
- 诚实边界逐条写明（不拦数据、不感知运行时、不承诺 100%、不评估敏感度等级）。
- 升级路径清晰：改引擎常量 `ALLOW_KEYWORDS`、规则库 `rules.json`、量化权重后重打包；回退保留旧 zip 即覆盖。

## 综合 5.0/5
理论硬、覆盖全、量化有原创维度、工程严谨留实物、文档中文友好且诚实。满足 guard 系列 4.8 基准：顶会/标准理论 + 完整闭环 + 零依赖好部署 + 严格按规律不糊弄 + 留下实物证据 + 文档清晰。
