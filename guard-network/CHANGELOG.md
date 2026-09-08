# guard-network 变更记录

## v2.0.0（2026-09-02）
- 初版构建，guard 系列第八条（外联 / 数据外泄通道检测）。
- 真引擎 `scripts/guard.py`：scan / rules / ledger / version 四子命令，确定性、可重跑、零依赖。
- 12 条规则跨 6 层：egress（出站 POST / 编码外发 / 原始 socket）、dns（DNS 隧道 / 动态域名）、c2（DGA 子域 / 信标）、tunnel（反弹 shell / 内网穿透）、raw（原始套接字 / 造包）、safe（出口白名单+TLS 校验+审计，仅鼓励不命中）。
- 原创量化点：外联暴露指数（0-100）、判定优先级链、可阻断性维度、安全控制价值量化（避免工时），ledger 可聚合为价值账本。
- 退出码 0/1/2/3/4（4=已拦截）。
- 三篇 references 长文：network-egress-theory（MITRE T1041/T1048、CIS 出口过滤）、c2-detection（信标/DGA/DNS 隧道/反弹 shell/原始套接字）、defense-stance（统一立场与诚实边界）。
- 合规：包内无 http(s):// 直链 / 真实 IP / 盘符根或用户主目录写法；打包去 BOM、CRLF→LF、SKILL.md 在根。

## 设计站位说明
- 看清后果再决定，不硬禁止——硬禁止逼出更隐蔽绕过（加密隧道/域名分段/白名单外跳板）。
- 仅静态检测、不实际拦流量、不感知运行时真实外联、不承诺 100%。
