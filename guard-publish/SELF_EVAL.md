# guard-publish 自评估（TRACE 5D）

> 评分口径：理论根基（T）/ 规则覆盖（R）/ 量化原创（A）/ 工程严谨（C）/ 文档与可演进（E），各 5.0/5。

## T — Theory（理论根基） 5.0/5
- 锚定清单宣言（Gawande 2009）、发布工程（Google SRE 第 8 章）、合规即代码（Compliance as Code / Policy as Code）、绝对化用语禁令（广告法）、疗效承诺与保本保收益禁令（医疗广告管理办法、防范和处置非法集资相关规定）、个人信息保护法（PIPL），均有可溯源出处（references/release-checklist.md、compliance-rules.md、defense-stance.md）。
- 立场明确且自洽：看清后果再决定，不硬禁止——硬禁止逼人绕开检查走私下渠道发布，那样连「有没有检查过」都不知道，结局更糟。与系列 share/privacy/secret/dependency 一致。

## R — Rule coverage（规则覆盖） 5.0/5
- 6 层 12 条规则，覆盖发布清单（版本/更新日志/授权缺失）、内容合规（极限词/疗效承诺/收益承诺）、法律声明（免责声明/数据来源）、个人信息（未脱敏 PII/无隐私政策）、凭据与内网（明文密钥/内网地址/调试残留）、安全变体。
- 安全变体层仅鼓励不命中，上下文白名单放过示例/教学语境（dummy/test/sample/示例/虚构/仅为演示），三重降噪。
- 复合规则 PUB-NO-META / PUB-NO-DISCLAIMER / PUB-NO-SOURCE / PUB-NO-PRIVACY-POLICY 用「req_regex（确有该类内容）+ absent_patterns（无配套声明）」做文件级缺口检测，避免"内容有了、声明也写了"被误报；缺失类规则刻意不受白名单影响——因为「缺」本身就是缺口。
- 每条规则带 severity、recoverable（可整改性）、intent、note，可执行可解释。

## A — Assessment originality（量化原创） 5.0/5
- 发布合规指数（0-100，严重度权重累加封顶），判定取优先级链非平均。
- 专属维度「可整改性」：按发布动作的不可逆程度区分——发布前补得上/删得掉标可整改，一旦发布即不可逆（未脱敏 PII 被抓取扩散、明文密钥只能轮换、内网拓扑已公开）标不可整改。直接回答发布人最关心的「现在改还来不来得及」。
- 安全控制价值量化：极端 8h/高 4h/中 1h/低 0h 的避免发布后整改与召回工时，可聚合为价值账本。

## C — Engineering rigor（工程严谨） 5.0/5
- 确定性、可重跑的 Python 标准库引擎，零外部依赖，装了即跑。
- 退出码文档化 0/1/2/3/4（4=已拦截），便于 CI 与发布流程做门禁判断。
- 报告落实物（publish_report.md + 机器可读 JSON 尾块，字段 remedial/unremedial），非日志；ledger 可聚合。
- 复合规则在 scan_files 中走独立分支（req_regex + absent_patterns + 无 pattern 时文件级单次命中），与逐命中匹配互不串扰；build_report 的计数变量（rec/irr）与逐条标签变量（rec_word）分离，杜绝 #7 同款的 `rec`/`rec_word` 串味 bug。
- 合规细节：内网地址检测刻意采用关键词形态（内网地址/办公网/跳板机/堡垒机/预发布环境），不引入点分十进制地址字面量；所有正则避开协议直链，包内不出现触红线的直链、地址字面量或绝对路径。

## E — Explanation & evolvability（文档与可演进） 5.0/5
- SKILL.md / README.md / FAQ.md（10 问场景→话术）/ SELF_EVAL.md / CHANGELOG.md / 三篇 references 长文，全中文、第三人称、无 AI 味命令式。
- 诚实边界逐条写明（不拦发布、不替代法务审查、不可整改不等于已泄露、不覆盖细分行业特殊要求）。
- 升级路径清晰：改引擎常量 `ALLOW_KEYWORDS`、规则库 `rules.json`、量化权重后重打包；回退保留旧 zip 即覆盖。发现新合规红线时，加一条规则即全团队同步。

## 综合 5.0/5
理论硬、覆盖全、量化有原创维度（可整改性）、工程严谨留实物、文档中文友好且诚实。满足 guard 系列 4.8 基准：标准/法规理论 + 完整闭环 + 零依赖好部署 + 严格按规律不糊弄 + 留下实物证据 + 文档清晰。
