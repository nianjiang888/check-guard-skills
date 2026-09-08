# guard-prompt · 更新记录

## v2.0.0（2026-09-01）

- **定位**：guard 系列第三棒，提示注入检测。AI 处理不可信内容之前的静态安检。
- **真引擎** `scripts/guard.py`：三维检测（指令劫持信号 hijack → 结构/分隔符注入 structure → 意图目标 intent）；覆盖直接注入与间接注入（RAG 投毒/网页藏针/多模态残留）；四级判定优先级链；注入风险分（0-100）。
- **三处资源**：rules.json（14 条三维规则 + 隐形字符 stealth_chars + 白名单，可增改）/ prompt-injection-models.json（OWASP LLM01、直接/间接、风险分、StruQ/SecAlign、诚实边界）/ prompt-domains.json（字段·边界·退出码）。
- **三篇方法论长文**：owasp-llm01（LLM01 榜首+直接/间接+架构根因+硬数据）、injection-defense（文本/模型/执行三层+诚实边界 90–95%）、indirect-injection（RAG 投毒/多模态/上下文污染深潜）。
- **实物证据**：每次扫描落 `injection_report.md`（含维度/严重度/意图/文件行号，机器可读 JSON 尾块），`ledger` 聚合生成 `guard-ledger.md` 价值账本。
- **退出码**：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / 4 已拦截（高/极端）。
- **写作原则**：全中文内容、英文 slug 与 CLI、第三人称站位、无人格锚；不承诺 100% 拦住（诚实边界，Transformer 架构级缺陷）；隐私——扫描本地进行不外发。
- **合规**：包内无 http(s) 直链 / 真实 IP / 绝对路径；打包去 BOM、CRLF→LF、SKILL.md 在根。
