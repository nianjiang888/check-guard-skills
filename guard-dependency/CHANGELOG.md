# guard-dependency 变更记录

## v2.0.0（2026-09-02）
- 初版构建，guard 系列第十条（依赖漏洞与投毒护栏）。
- 真引擎 `scripts/guard.py`：scan / rules / ledger / version 四子命令，确定性、可重跑、零依赖。
- 12 条规则跨 6 层：manifest（浮动版本 / git 源）、version（已知投毒版本 / typosquatting）、confusion（依赖混淆 / 安装钩子执行代码 / 源劫持）、integrity（明文 http 源 / 无完整性哈希）、source（自定义 registry / 锁分支）、safe（固定版本+完整性校验，仅鼓励不命中）。
- 复合规则 DEP-NO-INTEGRITY：用 req_regex（有 resolved/tarball 地址）+ absent_patterns（integrity/sha 哈希清单）做文件级缺口检测。
- 原创量化点：依赖风险指数（0-100）、判定优先级链、可治理性维度、安全控制价值量化（避免工时），ledger 可聚合为价值账本。
- 退出码 0/1/2/3/4（4=已拦截）。
- 三篇 references 长文：slsa-sbom（SLSA 与 SBOM 溯源）、dependency-confusion（混淆/typosquatting/安装钩子/幽灵依赖）、defense-stance（统一立场与诚实边界）。
- 合规：包内无 http(s):// 直链（明文 http 源检测用 `http:(?=//)`、git 源用 `git\+https?://`，避开字面量）/ 真实 IP / 盘符根或用户主目录写法；打包去 BOM、CRLF→LF、SKILL.md 在根。

## 设计站位说明
- 看清后果再决定，不硬禁止——硬禁止逼出 vendored 黑箱等更隐蔽绕过。
- 仅静态检测、不解析真实依赖树、不实际拦安装、不承诺 100%、自定义源不判死（一律提示人工确认）。
