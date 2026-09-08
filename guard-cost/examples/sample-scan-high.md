# guard-cost 成本风险检测报告

- 扫描时间：2026-09-02 07:14
- 目标：示例目录/hi
- 引擎版本：2.0.0

## 一、判定

- **风险等级：高**
- **花费暴露指数：100 / 100**
- **可规避性：6 处可规避 / 0 处不可规避**
- **处置建议：拦下，人工确认后再决定；付费调用必须先加护栏**

## 二、命中汇总（6 处）

- 按严重度：极端 0 / 高 2 / 中 4 / 低 0
- 按类型：密钥泄露 1、无界循环 1、预算缺失 1、限速缺失 1、熔断缺失 1、高单价模型 1

## 三、命中清单

| 严重度 | 类型 | 可规避 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 高 | 密钥泄露 | 可规避 | 硬编码 API 密钥(COST-KEY-HARDCODE) | caller.py:1 | api_key = "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456" | 改用环境变量 / 密钥管理服务 |
| 高 | 无界循环 | 可规避 | for 循环内批量调付费 API(COST-FOR-API) | caller.py:2 | for item in items: | 循环需有确定上界，或加预算熔断 |
| 中 | 预算缺失 | 可规避 | 付费调用无预算上限(COST-NO-BUDGET) | caller.py:1 | api_key = "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456" | 补 max_tokens / 预算常量 / 熔断 |
| 中 | 限速缺失 | 可规避 | 付费调用无限速(COST-NO-RATELIMIT) | caller.py:1 | api_key = "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456" | 补 rate limiter / 退避等待 |
| 中 | 熔断缺失 | 可规避 | 付费调用无熔断(COST-NO-CIRCUIT) | caller.py:1 | api_key = "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456" | 补 circuit breaker / fallback 降级 |
| 中 | 高单价模型 | 可规避 | 使用高单价模型(COST-EXPENSIVE-MODEL) | caller.py:3 | result = client.chat.completions.create(model="gpt-4o-mini", messages=item) | 评估是否可降级到 mini/轻量版 |

## 四、安全控制价值量化

- 本次若放行，估算可避免损失：约 4 小时账单对账与止损响应

> 说明：本工具立场是「看清后果再决定」，不是硬禁止——硬禁止会逼用户绕过护栏，那是更坏结局。判定依据为命中的严重度优先级链，非平均。诚实边界：仅做静态检测，不实际拦请求；对运行时动态调用频次无感知，单价以 cost-models.json 参考价为准，实际以账单为准。

```json
{"time": "2026-09-02 07:14", "target": "示例目录/hi", "verdict": "高", "exposure_index": 100, "recoverable": "可规避", "irrecoverable": 0, "findings": 6, "avoided_spend_hours": 4}
```