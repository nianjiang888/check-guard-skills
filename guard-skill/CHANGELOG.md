# guard-skill · 更新记录

## v2.0.0（2026-09-01）

- **定位**：guard 系列旗舰，第三方技能 / MCP / 代码包供应链安全审查。
- **真引擎** `scripts/guard.py`：五子命令 review / scan / rules / ledger / version；扫描五类红线（提示注入后门、凭据窃取、数据外传、权限越界、代码混淆），溯源（author/version/updated），权限范围评估（网络/文件写入/shell 信号），四级判定优先级链，供应链信任指数（0-100）。
- **三处资源**：rules.json（14 条红线，可增改）/ skill-supply-chain-models.json（信任分·判定链·价值量化模型）/ skill-domains.json（字段·边界·退出码）。
- **三篇方法论长文**：slsa-sbom（SLSA+SBOM）、least-privilege（Saltzer&Schroeder 1975）、malicious-skill-patterns（依赖混淆/CWE/OWASP LLM01）。
- **实物证据**：每次审查落 `verdict_report.md`（含机器可读 JSON 尾块），`ledger` 聚合生成 `guard-ledger.md` 价值账本。
- **退出码**：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / 4 已拦截（高/极端）。
- **写作原则**：全中文内容、英文 slug 与 CLI、第三人称站位、无人格锚；不承诺 100% 拦住（诚实边界）；隐私——审查本地进行不外发。
- **合规**：包内无 http(s)/IP/绝对路径；打包去 BOM、CRLF→LF、SKILL.md 在根。
