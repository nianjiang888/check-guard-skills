# guard-privacy 变更记录

## v2.0.0（2026-09-02）
- 初版构建，guard 系列第九条（PII 字段脱敏护栏）。
- 真引擎 `scripts/guard.py`：scan / rules / ledger / version 四子命令，确定性、可重跑、零依赖。
- 12 条规则跨 6 层：pii_field（硬编码 / 身份证号 / 手机号 / 邮箱 / 住址 / 无脱敏缺口）、log（日志打印 / 输出打印原始 PII）、store（明文存储）、export（接口返回直带完整 PII）、external（外传第三方无脱敏）、safe（脱敏/加密/令牌化，仅鼓励不命中）。
- 复合规则 PII-MASK-MISSING：用 req_regex（PII 字段名）+ absent_patterns（脱敏函数清单）做文件级缺口检测，无需逐行 pattern。
- 原创量化点：PII 暴露指数（0-100）、判定优先级链、可脱敏性维度、安全控制价值量化（避免工时），ledger 可聚合为价值账本。
- 退出码 0/1/2/3/4（4=已拦截）。
- 三篇 references 长文：pii-detection（NER 与 PII 识别、k-匿名/差分隐私）、privacy-law（PIPL/GDPR 义务）、defense-stance（统一立场与诚实边界）。
- 合规：包内无 http(s):// 直链 / 真实 IP / 盘符根或用户主目录写法；打包去 BOM、CRLF→LF、SKILL.md 在根。

## 设计站位说明
- 看清后果再决定，不硬禁止——硬禁止逼出更隐蔽绕过（把 PII 藏进更隐蔽字段或加密信道）。
- 仅静态检测、不实际拦数据、不感知运行时真实数据流向、不承诺 100%。
