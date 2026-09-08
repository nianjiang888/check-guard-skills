# guard-secret · 更新记录

## v2.0.0（2026-09-01）

- **定位**：guard 系列第二棒，密钥 / 凭据泄露扫描。提交 / 发布之前的静态体检。
- **真引擎** `scripts/guard.py`：三层检测管线（正则精度 → 香农熵召回 → 上下文/白名单降误报）；扫描 AWS/GCP/Azure/SSH/DB/API/Token/Stripe 等 14 类密钥格式；四级判定优先级链；密钥暴露面指数（0-100）。
- **三处资源**：rules.json（14 条正则 + 熵阈值 + 白名单，可增改）/ secret-models.json（香农熵模型·三层管线·暴露面指数·轮换原则）/ secret-domains.json（字段·边界·退出码）。
- **两篇方法论长文**：shannon-entropy（1948 信息论 + 字符集熵上限 + 阈值依据）、secret-detection-pipeline（三层互补 + CWE-798 + 删行没用必须轮换 + 诚实边界 90–95%）。
- **实物证据**：每次扫描落 `secret_report.md`（含类型/置信度/是否疑似已泄露/轮换建议，机器可读 JSON 尾块），`ledger` 聚合生成 `guard-ledger.md` 价值账本。
- **退出码**：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / 4 已拦截（高/极端）。
- **写作原则**：全中文内容、英文 slug 与 CLI、第三人称站位、无人格锚；不承诺 100% 拦住（诚实边界）；隐私——扫描本地进行不外发。
- **合规**：包内无 http(s) 直链 / 真实 IP / 绝对路径；打包去 BOM、CRLF→LF、SKILL.md 在根。
