# guard-command 更新日志

## v2.0.0（2026-09-02）

- 首个可用版本（guard 系列第 7 棒）。
- 真引擎 `scripts/guard.py`：scan / rules / ledger / version 四子命令，零依赖标准库，中文报错，退出码 0/1/2/3/4（4=已拦截）。
- 六层检测、12 条规则：
  - 文件系统破坏：CMD-RM-RF（极端）
  - 磁盘/设备：CMD-DD-DISK（极端）、CMD-MKFS（极端）、CMD-DEV-REDIRECT（极端）
  - 进程自杀：CMD-FORKBOMB（极端）
  - 权限/提权：CMD-CHMOD-777（高）、CMD-CHMOD-000（高）、CMD-SUDO-SU（高）
  - 网络执行：CMD-PIPE-SH（高）
  - 版本控制：CMD-VCS-FORCE（高）、CMD-NO-VERIFY（中）
  - 安全变体：CMD-SAFE-DRYRUN（低）
- 原创量化点：命令危险暴露指数（0-100）+ 判定优先级链 + 安全控制价值量化（避免恢复工时）+ 可回滚性维度。
- 边界收敛降误报：rm -rf 而非任意 rm、777 而非 755、网络下载直输 shell 才报。
- 资源三份：rules.json（12 规则）、command-models.json（最小权限/能力安全/爆炸半径 + 量化）、command-domains.json（字段/边界/退出码）。
- 参考文档三篇：least-privilege / capability-security / defense-stance（均带权威引用）。
- 文档五件套：SKILL.md / FAQ.md（10 问）/ README.md / SELF_EVAL.md（TRACE 5D 全 5.0）/ CHANGELOG.md。
- 样例报告四份：极端 / 高 / 中 / 干净。
- 合规：包内无 http(s):// 直链 / 真实 IP / 绝对路径（盘符根或用户主目录写法）；打包去 BOM、CRLF→LF、SKILL.md 在根。
- 交付物：`guard-command-2.0.0.zip`（16 文件）。
