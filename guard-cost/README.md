# guard-cost API 花费熔断引擎

guard 安全护栏系列的第 5 个独立成员。在 while True 调大模型、无限重试、没预算上限、没熔断这些"删钱"操作上线前，先算一笔花费暴露指数、看清账单后果再决定。

设计立场：**看清账单后果再决定，不硬禁止**。硬禁止会逼出绕过，那更糟。本包是多层防御里的「工具层」，不替代人的决策，也不替代预算系统、限流中间件、账单告警。

## 文件导航

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 技能说明、触发词、用法、判定与量化、理论底座 |
| `scripts/guard.py` | 主引擎（标准库零依赖，可重跑） |
| `resources/rules.json` | 七层成本风险检测规则库 |
| `resources/cost-models.json` | 理论模型（熔断/令牌桶/控制论）+ 参考单价表 |
| `resources/cost-domains.json` | 领域与判定配置、退出码、诚实边界 |
| `references/circuit-breaker.md` | 熔断器模式与令牌桶论证 |
| `references/cost-control-theory.md` | 控制论视角与价值量化逻辑 |
| `references/defense-stance.md` | 为何不硬禁止的设计立场 |
| `FAQ.md` | 9 个常见问答 |
| `SELF_EVAL.md` | 自评（TRACE 五维 5.0） |
| `CHANGELOG.md` | 版本记录 |
| `examples/` | 各场景样例报告 |

## 快速开始

```bash
# 扫描一个含大模型调用的目录，看成本雷区
python scripts/guard.py scan ./my-llm-code

# 对具体调用做花费投影（模型:次数xtoken）
python scripts/guard.py cap "gpt-4o:10000x2000"

# 列出全部规则库
python scripts/guard.py rules

# 聚合多份报告生成成本防护价值账本
python scripts/guard.py ledger .
```

## 子命令

- `scan <目录>`：扫描并出 `cost_report.md`；判定高/极端时退出码 4。
- `cap <路径 | model:次数xtoken>`：花费投影（路径模式=扫描花费暴露指数，简写模式=按参考单价算花费）。
- `rules`：列出全部成本风险规则（七层）。
- `ledger [目录]`：聚合 `cost_report.md` / `cost_cap_report.md` 生成 `guard-ledger.md`。
- `version`：打印引擎版本。

## 退出码

| 码 | 含义 |
|---|---|
| 0 | 通过：未发现明显成本雷区 |
| 1 | 参数错：缺路径/目录不存在/账本无记录 |
| 2 | IO 错：规则文件缺失或解析失败、报告写入失败 |
| 3 | 未知命令 |
| 4 | 已拦截：判定为高或极端，建议不要直接上线 |

## 判定与量化

- 判定优先级链：极端 > 高 > 中 > 低（按最坏一项，非平均）。
- 花费暴露指数（0-100）：严重度权重累加封顶（极端 100 / 高 40 / 中 12 / 低 3）。
- 安全控制价值量化：拦下后估算避免的止损工时（极端 8h / 高 4h / 中 1h / 低 0h）。

## 诚实边界

不实际拦截请求；不感知运行时动态调用频次；不保证 100% 拦住；单价仅为参考估算，真实花费以账单为准。报告仅写本地，不含凭据或网络地址。
