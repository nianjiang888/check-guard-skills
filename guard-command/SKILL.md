---
name: guard-command
display_name: 命令执行护栏
version: 2.0.0
description: 高危命令与危险参数拦截（技术触发词：高危命令检测/危险参数/命令注入/最小权限/能力安全/blast radius/rm -rf/dd 写盘/fork bomb/chmod 777/curl 管道直跑/git --force/--no-verify；口语触发词：这条命令跑下去会不会删库/rm -rf 会不会误删/curl 管道直跑脚本安不安全/脚本里有没有危险 root 操作/git push --force 能不能拦；英文触发词：dangerous command / risky argument / rm -rf / fork bomb / privilege escalation / pipe to shell / git force push；一句话功能：在脚本上线前静态扫描危险命令与危险参数，算命令危险暴露指数并出可回滚性报告，看清后果再决定）
license: MIT
---

# guard-command · 高危命令 / 危险参数拦截

## 这个技能在防什么

rm -rf /、dd 写盘、mkfs、fork bomb、chmod 777、sudo su、curl|sh、git push --force——这些命令一旦真跑，轻则清库重装，重则整盘报销。guard-command 是一个**自主运行的检测引擎**，在脚本/命令上线前静态扫一遍危险命令与危险参数，把风险点、严重度、以及「拦下后能避免多少恢复工时」算清楚，交给人决定。

## 它能做 / 不能做

- **能**：扫描目录，检测六类危险命令（文件系统破坏 / 磁盘设备 / 权限提权 / 进程自杀 / 网络执行 / 版本控制），输出判定、暴露指数、命中清单与价值量化报告；聚合多份报告生成团队价值账本。
- **不能**：不实际拦截任何命令、不感知运行时真实执行情况、不判定命令「是否会真被运行」。它只量化**静态可见**风险，决策权始终在人。

## 怎么用

```
python scripts/guard.py scan <目录>          # 扫描并出 command_report.md
python scripts/guard.py rules                # 列出 12 条规则库
python scripts/guard.py ledger <目录>         # 聚合报告生成 guard-ledger.md
python scripts/guard.py version              # 打印引擎版本
```

退出码：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / **4 已拦截（高/极端风险）**。

## 原创量化点

1. **命令危险暴露指数（0-100）**：极端 100 / 高 40 / 中 12 / 低 3，按最坏一项定级（极端>高>中>低），不被平均稀释。
2. **判定优先级链**：最坏一项定级，而非算术平均。
3. **安全控制价值量化**：把「没发生的误操作」折算成可感知工时（极端 8h / 高 4h / 中 1h / 低 0h）。
4. **可回滚性维度**：每条命中标「可回滚/不可回滚」，呼应 rm -rf / dd 这类一旦执行难挽回。

## 设计立场

看清后果再决定，不硬禁止——硬禁止会逼人绕过护栏（--no-verify/裸 root），那是更坏结局。误报会杀死产品，故对危险命令本体做了边界收敛（rm -rf 而非任意 rm、777 而非 755）。

## 文件导航

- `scripts/guard.py` — 主引擎（零依赖，标准库）
- `resources/rules.json` — 12 条高危命令规则（六层 + 安全变体）
- `resources/command-models.json` — 理论模型与量化方法
- `resources/command-domains.json` — 字段 / 边界 / 退出码定义
- `references/` — 最小权限、能力安全/爆炸半径、防御立场三篇带引用
- `FAQ.md` `README.md` `SELF_EVAL.md` `CHANGELOG.md` — 文档
- `examples/` — 极端 / 高 / 中 / 干净 四份样例报告
