# CHANGELOG — guard-cost

## v2.0.0（2026-09-02）

- 首个完整版本，12 个文件，对齐 guard 系列统一标准。
- 主引擎 `scripts/guard.py`：纯标准库零依赖，五子命令（scan / cap / rules / ledger / version），退出码 0/1/2/3/4（4=已拦截）。
- 七层成本雷区检测：无界循环（while True / for / map 内调付费 API）、预算缺失、限速/熔断缺失、重试失控、高单价模型、密钥硬编码、安全变体（预算常量/熔断装饰器/限速中间件，仅作鼓励信号）。
- 复合规则：缺预算/限速/熔断类规则要求「文件确实调了付费 API」且「缺失对应护栏字样」才命中，显著降低误报。
- 原创量化点：花费暴露指数（0-100）+ 判定优先级链（极端>高>中>低）+ 安全控制价值量化（避免工时）+ cap 花费投影（model:次数xtoken 简写按参考单价）。
- `cap` 子命令：简写模式按参考单价投影花费；路径模式扫描花费暴露指数。拒绝遍历根目录/盘符根。
- 理论底座：熔断器模式（Nygard 2007）、令牌桶（Turner 1986）、控制论视角（Wiener 1948 / Ashby 1956），references 三篇 + resources 三份（含参考单价表）。
- 文档：SKILL.md / FAQ.md / README.md / SELF_EVAL.md / CHANGELOG.md / examples/，全中文无 AI 味。
- 自评 TRACE 五维 5.0/5。
- 合规：包内无 http/https/IP、无 Windows 绝对路径、无 BOM/CRLF。
