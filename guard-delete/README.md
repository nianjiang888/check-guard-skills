# guard-delete 破坏性操作拦截引擎

guard 安全护栏系列的第 4 个独立成员。在 rm -rf /、DROP TABLE、git push --force、chmod 000 这类破坏性操作真正执行前，先扫一遍、算一遍爆炸半径、看清可逆性，让你在敲回车之前就知道会波及多少东西。

设计立场：**看清后果再决定，不硬禁止**。硬禁止会逼出 --no-verify、sudo、裸 shell 绕过，那更糟。本包是多层防御里的「工具层」，不替代人的决策，也不替代备份、版本控制、最小权限、审批流。

## 文件导航

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 技能说明、触发词、用法、判定与量化、理论底座 |
| `scripts/guard.py` | 主引擎（标准库零依赖，可重跑） |
| `resources/rules.json` | 七层破坏性操作检测规则库 |
| `resources/delete-models.json` | 理论模型（瑞士奶酪/爆炸半径/海因里希） |
| `resources/delete-domains.json` | 领域与判定配置、退出码、诚实边界 |
| `references/swiss-cheese-blast-radius.md` | 瑞士奶酪模型与爆炸半径论证 |
| `references/heinrich-law.md` | 海因里希法则与价值量化逻辑 |
| `references/defense-stance.md` | 为何不硬禁止的设计立场 |
| `FAQ.md` | 9 个常见问答 |
| `SELF_EVAL.md` | 自评（TRACE 五维 5.0） |
| `CHANGELOG.md` | 版本记录 |
| `examples/` | 各场景样例报告 |

## 快速开始

```bash
# 扫描一个目录，看有没有破坏性操作
python scripts/guard.py scan ./my-script-dir

# 对某个具体命令做干跑预览（只数不删）
python scripts/guard.py blast "rm -rf ./dist"

# 列出全部规则库
python scripts/guard.py rules

# 聚合多份报告生成安全控制价值账本
python scripts/guard.py ledger .
```

## 子命令

- `scan <目录>`：扫描并出 `blast_report.md`；判定高/极端时退出码 4。
- `blast <路径或命令>`：干跑预览爆炸半径，只统计不删除。
- `rules`：列出全部破坏性规则（七层）。
- `ledger [目录]`：聚合 `blast_report.md` 生成 `guard-ledger.md`。
- `version`：打印引擎版本。

## 退出码

| 码 | 含义 |
|---|---|
| 0 | 通过：未发现破坏性操作 |
| 1 | 参数错：缺路径/目录不存在/账本无记录 |
| 2 | IO 错：规则文件缺失或解析失败、报告写入失败 |
| 3 | 未知命令 |
| 4 | 已拦截：判定为高或极端，建议不要执行 |

## 判定与量化

- 判定优先级链：极端 > 高 > 中 > 低（按最坏一项，非平均）。
- 爆炸半径指数（0-100）：严重度权重累加封顶（极端 100 / 高 40 / 中 12 / 低 3）。
- 安全控制价值量化：拦下后估算避免的事故响应工时（极端 8h / 高 4h / 中 1h / 低 0h）。

## 诚实边界

不实际执行/拦截/批准任何命令；不感知运行时即时命令；不保证 100% 拦住；不替代备份与版本控制。报告仅写本地，不含凭据或网络地址。
