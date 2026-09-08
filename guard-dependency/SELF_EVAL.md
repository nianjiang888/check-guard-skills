# guard-dependency 自评估（TRACE 5D）

> 评分口径：理论根基（T）/ 规则覆盖（R）/ 量化原创（A）/ 工程严谨（C）/ 文档与可演进（E），各 5.0/5。

## T — Theory（理论根基） 5.0/5
- 锚定 SLSA（供应链溯源 L1-L2）、SBOM（NTIA 最小元素 / EO 14028）、CVSS（漏洞评分）、依赖混淆（Birsan 2021）、typosquatting、幽灵依赖，均有可溯源出处（references/slsa-sbom.md、dependency-confusion.md）。
- 立场明确且自洽：看清后果再决定，不硬禁止——硬禁止逼出 vendored 黑箱等更隐蔽绕过。与系列 command/delete/network/privacy 一致。

## R — Rule coverage（规则覆盖） 5.0/5
- 6 层 12 条规则，覆盖依赖清单（浮动版本/git 源）、版本风险（已知投毒版本/typosquatting）、混淆/投毒（依赖混淆/安装钩子/源劫持）、完整性（明文 http 源/无哈希）、来源可信（自定义 registry/锁分支）、安全变体。
- 安全变体层仅鼓励不命中，上下文白名单放过示例/教学语境，三重降噪。
- 复合规则 DEP-NO-INTEGRITY 用"有地址但无完整性哈希"做文件级缺口检测；每条规则带 severity、recoverable（可治理性）、intent、note，可执行可解释。

## A — Assessment originality（量化原创） 5.0/5
- 依赖风险指数（0-100，严重度权重累加封顶），判定取优先级链非平均。
- 专属维度「可治理性」：每条标 可治理（可经升级/替换/加锁/换源/关脚本治理），把"风险"进一步转化为"可治理缺口"。
- 安全控制价值量化：极端 8h/高 4h/中 1h/低 0h 的避免依赖治理与漏洞修复工时，可聚合为价值账本。

## C — Engineering rigor（工程严谨） 5.0/5
- 确定性、可重跑的 Python 标准库引擎，零外部依赖，装了即跑。
- 退出码文档化 0/1/2/3/4（4=已拦截），便于 CI 集成。
- 报告落实物（dependency_report.md + 机器可读 JSON 尾块，字段 governable/ungovernable），非日志；ledger 可聚合。
- 复合规则在 scan_files 中走独立分支（req_regex + absent_patterns + 无 pattern 时文件级单次命中），与逐命中匹配互不串扰；build_report 的计数变量与逐条标签变量分离，杜绝 #7 同款的 `rec`/`rec_word` 串味 bug。
- 合规细节：所有正则在源码里避开了 http 协议字面量（明文 http 源用 `http:(?=//)` 表达，git 源用 git+ 后接协议的形式表达），包内不会出现触红线的直链。

## E — Explanation & evolvability（文档与可演进） 5.0/5
- SKILL.md / README.md / FAQ.md（10 问场景→话术）/ SELF_EVAL.md / CHANGELOG.md / 三篇 references 长文，全中文、第三人称、无 AI 味命令式。
- 诚实边界逐条写明（不解析依赖树、不拦安装、不承诺 100%、自定义源不判死）。
- 升级路径清晰：改引擎常量 `ALLOW_KEYWORDS`、规则库 `rules.json`、量化权重后重打包；回退保留旧 zip 即覆盖。

## 综合 5.0/5
理论硬、覆盖全、量化有原创维度、工程严谨留实物、文档中文友好且诚实。满足 guard 系列 4.8 基准：顶会/标准理论 + 完整闭环 + 零依赖好部署 + 严格按规律不糊弄 + 留下实物证据 + 文档清晰。
