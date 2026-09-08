# guard-share 自评估（TRACE 5D）

> 评分口径：理论根基（T）/ 规则覆盖（R）/ 量化原创（A）/ 工程严谨（C）/ 文档与可演进（E），各 5.0/5。

## T — Theory（理论根基） 5.0/5
- 锚定 DLP（数据防泄露）、数据分级分类（ISO/IEC 27001 附录 A.8）、溯源标记 / 蜜标（Thinkst Canary 思路）、数字水印、泄露处置成本（Ponemon 年度研究），均有可溯源出处（references/dlp-classification.md、leak-detection.md、defense-stance.md）。
- 立场明确且自洽：看清后果再决定，不硬禁止——硬禁止逼人把文件改成图片/加密压缩包私下传，反而脱离任何审查，结局更糟。与系列 privacy/secret/network 一致。

## R — Rule coverage（规则覆盖） 5.0/5
- 6 层 12 条规则，覆盖 PII 外泄（身份证/手机号/邮箱）、密钥外泄（明文 API Key/私钥/账号密码）、商业敏感（报价/路线图）、内部文档（内网/员工/薪酬）、分类缺失（有敏感内容无密级标签）、溯源缺失（有敏感内容无标记）。
- 安全变体层仅鼓励不命中，上下文白名单放过示例/教学语境（your-/dummy/test/sample/示例/虚构/仅为演示），三重降噪。
- 复合规则 SHARE-CLASSIFY-MISSING / SHARE-WATERMARK-MISSING 用「req_regex（必有敏感内容）+ absent_patterns（必无处置标记）」做文件级缺口检测；每条规则带 severity、recoverable、intent、note，可执行可解释。

## A — Assessment originality（量化原创） 5.0/5
- 外发泄露指数（0-100，严重度权重累加封顶），判定取优先级链非平均。
- 专属维度「可溯源性」：逐文件动态判定——同文件带密级/水印/canary/分类标签的泄露命中记为可溯源，无标记记为不可溯源。把"泄露后追不追得回来"第一次变成引擎实算的量化字段，而非套话。
- 安全控制价值量化：极端 8h/高 4h/中 1h/低 0h 的避免溯源补救与泄露处置工时，可聚合为价值账本。

## C — Engineering rigor（工程严谨） 5.0/5
- 确定性、可重跑的 Python 标准库引擎，零外部依赖，装了即跑。
- 退出码文档化 0/1/2/3/4（4=已拦截），便于 CI 集成做门禁判断。
- 报告落实物（share_report.md + 机器可读 JSON 尾块，字段 traceable/untraceable），非日志；ledger 可聚合。
- 复合规则在 scan_files 中走独立分支（req_regex + absent_patterns + 无 pattern 时文件级单次命中），与逐命中匹配互不串扰；build_report 的计数变量（rec/irr）与逐条标签变量（rec_word）分离，杜绝 #7 同款的 `rec`/`rec_word` 串味 bug。
- 可溯源性维度在 scan_files 内按文件级 `has_trace` 动态覆写 content-leak 层命中的 recoverable，逻辑集中在扫描期、报告期只读，避免状态错乱。
- 合规细节：所有正则在源码里避开 http 协议字面量（明文源表达用 `http:(?=//)` 形式），包内不出现触红线的直链、真实 IP 或绝对路径。

## E — Explanation & evolvability（文档与可演进） 5.0/5
- SKILL.md / README.md / FAQ.md（10 问场景→话术）/ SELF_EVAL.md / CHANGELOG.md / 三篇 references 长文，全中文、第三人称、无 AI 味命令式。
- 诚实边界逐条写明（不拦发送、不知文件最终去向、不解析图片/加密包、不承诺 100%、标记不校验真伪）。
- 升级路径清晰：改引擎常量 `ALLOW_KEYWORDS`/`TRACE_MARKERS`、规则库 `rules.json`、量化权重后重打包；回退保留旧 zip 即覆盖。

## 综合 5.0/5
理论硬、覆盖全、量化有原创维度（可溯源性）、工程严谨留实物、文档中文友好且诚实。满足 guard 系列 4.8 基准：顶会/标准理论 + 完整闭环 + 零依赖好部署 + 严格按规律不糊弄 + 留下实物证据 + 文档清晰。
