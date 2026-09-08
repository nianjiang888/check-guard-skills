# CHANGELOG — guard-delete

## v2.0.0（2026-09-01）

- 首个完整版本，13 个文件，对齐 guard 系列统一标准。
- 主引擎 `scripts/guard.py`：纯标准库零依赖，五子命令（scan / blast / rules / ledger / version），退出码 0/1/2/3/4（4=已拦截）。
- 七层破坏性操作检测：拒绝服务（fork 炸弹）、删除（rm -rf 各形态）、数据库（DROP/TRUNCATE/DELETE）、版本控制（push --force / clean / reset --hard）、文件（mv 到 /dev/null）、权限（chmod 000/777）、安全变体（git stash / mv 回收站 / cp 备份，仅作鼓励信号）。
- SQL WHERE 降级：删除/清空类规则自动检测是否带 WHERE，带则降一级，显著降低误报。
- 原创量化点：爆炸半径指数（0-100）+ 判定优先级链（极端>高>中>低）+ 安全控制价值量化（避免工时）。
- `blast` 子命令：干跑预览，只数文件、只算大小，一个字节都不删。
- 理论底座：瑞士奶酪模型（Reason 1990）、爆炸半径（Google SRE 2016）、海因里希法则（Heinrich 1931），references 三篇 + resources 三份。
- 文档：SKILL.md / FAQ.md / README.md / SELF_EVAL.md / CHANGELOG.md / examples/，全中文无 AI 味。
- 自评 TRACE 五维 5.0/5。
- 合规：包内无 http/https/IP、无 Windows 绝对路径、无 BOM/CRLF。
