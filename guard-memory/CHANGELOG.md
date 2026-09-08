# guard-memory 更新日志

## v2.0.0（2026-09-02）

- 首个可用版本（guard 系列第 6 棒）。
- 真引擎 `scripts/guard.py`：scan / rules / ledger / version 四子命令，零依赖标准库，中文报错，退出码 0/1/2/3/4（4=已拦截）。
- 七层检测、12 条规则：
  - 写入边界：MEM-WRITE-UNTRUSTED（高）
  - 投毒信号：MEM-POISON-PHRASE（极端）、MEM-POISON-IMPERATIVE（高）
  - RAG 溢出：MEM-RAG-NOCAP（中）、MEM-RAG-UNTRUSTED（高）
  - 跨会话：MEM-CROSS-SESSION（高）、MEM-SESSION-NOID（中）
  - 溯源缺失：MEM-NO-PROVENANCE（中）
  - 泄露：MEM-LEAK-SYSPROMPT（极端）、MEM-LEAK-SECRET（极端）
  - 安全变体：MEM-SAFE-PROVENANCE（低）、MEM-SAFE-QUARANTINE（低）
- 原创量化点：记忆污染暴露指数（0-100）+ 判定优先级链 + 安全控制价值量化（避免清洗工时）+ 可清洗性维度。
- 资源三份：rules.json（12 规则）、memory-models.json（OWASP/RAG/信任边界理论 + 量化）、memory-domains.json（字段/边界/退出码）。
- 参考文档三篇：owasp-llm07-memory-poisoning / rag-poisoning / defense-stance（均带权威引用）。
- 文档五件套：SKILL.md / FAQ.md（10 问）/ README.md / SELF_EVAL.md（TRACE 5D 全 5.0）/ CHANGELOG.md。
- 样例报告四份：极端 / 高 / 中 / 干净。
- 合规：包内无 http(s):// 直链 / 真实 IP / 绝对路径（盘符根或用户主目录写法）；打包去 BOM、CRLF→LF、SKILL.md 在根。
- 交付物：`guard-memory-2.0.0.zip`（16 文件）。
