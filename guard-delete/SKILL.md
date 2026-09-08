---
name: guard-delete
display_name: 删除操作护栏
version: 2.0.0
description: 在 rm -rf /、DROP TABLE、git push --force 这类破坏性操作真正执行前，先算一遍爆炸半径、看清可逆性再决定——guard-delete 破坏性操作拦截引擎。触发：技术词（rm -rf / DROP TABLE / git push --force / chmod 000 / truncate table / fork bomb）、口语（别乱删 / 这命令危险吗 / 删库跑路 / 强推会不会覆盖 / 删除前先确认 / 误删怎么办）、英文（destructive operation / blast radius / delete guard / prevent accidental deletion / safe delete）、场景（CI 脚本里有没有危险命令 / 代码评审防误删 / 运维操作前自检 / 清库前先评估）。
keywords:
  - 破坏性操作
  - rm -rf
  - DROP TABLE
  - git push --force
  - 删库
  - 误删防护
  - 爆炸半径
  - 干跑预览
  - 安全删除
  - 破坏性命令检测
  - blast radius
  - destructive operation
  - delete guard
  - safe delete
  - accidental deletion
  - chmod 000
  - truncate table
  - fork bomb
  - 瑞士奶酪模型
  - 海因里希法则
  - 代码评审
  - 运维安全
  - 版本控制风险
  - 权限置空
  - 安全控制价值量化
  - guard 系列
triggers:
  - "用户问某个删除/清理命令安不安全、会不会误删"
  - "用户准备执行 rm -rf、DROP TABLE、git push --force 等危险操作前想先确认"
  - "用户在写脚本/CI，担心里面藏了破坏性命令"
  - "用户做了代码评审，想顺手检查有没有误删风险"
  - "用户提到删库跑路、误删恢复、强推覆盖等事故"
  - "用户需要给安全操作留可审计的证据（blast_report / 价值账本）"
  - "用户问破坏性操作该怎么防御、有哪些安全替代"
  - "用户想把『没发生的灾难』折算成可感知的安全价值"
license: MIT
---

# guard-delete 破坏性操作拦截引擎

## 一、这是什么

guard-delete 是 guard 安全护栏系列的第 4 个独立成员，定位是「破坏性操作拦截」。它不替代人的决策，而是在 rm -rf /、DROP TABLE、git push --force、chmod 000 这类高危动作真正执行前，先扫一遍、算一遍爆炸半径、看清可逆性，让你在敲回车之前就知道会波及多少东西。

它和系列其他成员（guard-secret 凭据守护、guard-prompt 提示注入检测等）平行独立，各自守一个专业安全域，不挂古人 IP、不做流水线叙事。

## 二、能做什么 / 不能做什么

能做的：

- 检测七层破坏性操作模式：拒绝服务（fork 炸弹）、删除（rm -rf 各形态）、数据库（DROP/TRUNCATE/DELETE）、版本控制（push --force、clean、reset --hard）、文件（mv 到 /dev/null）、权限（chmod 000/777）。
- 对 SQL 是否带 WHERE 做全表/全量判定：带 WHERE 自动降一级，没带则标注「疑似全表操作」。
- `blast` 子命令对路径或命令做干跑预览，只数文件、只算大小，一个字节都不删。
- 把「拦下的先兆」折算成可感知数字（避免的事故响应工时），并聚合成价值账本。

不能做的（诚实边界）：

- 不实际执行、拦截或批准任何命令——决策权始终在人。
- 不感知运行时随手敲下的命令；只在被扫描的文本里看得到模式。
- 不保证 100% 拦住所有灾难，只是多层防御中的一层（需配备份、版本控制、最小权限、审批流）。
- 不替代 git stash、定期备份、rm 前的二次确认这些基本纪律。

## 三、怎么用

引擎在 `scripts/guard.py`，纯标准库、零依赖、可重跑。五个子命令：

```
python scripts/guard.py scan  <目录>            # 扫描并出 blast_report.md，高/极端退出码 4
python scripts/guard.py blast <路径或命令>      # 干跑预览爆炸半径，只数不删
python scripts/guard.py rules                  # 列出全部破坏性规则库
python scripts/guard.py ledger [目录]           # 聚合多份报告生成价值账本
python scripts/guard.py version                # 打印引擎版本
```

典型用法：动手删库/强推前，先 `scan` 一遍脚本目录，看报告里的风险等级与爆炸半径；对某个具体命令，用 `blast` 先看会波及多少文件；日常把若干 `blast_report.md` 用 `ledger` 聚合成团队安全价值账本。

## 四、判定与量化（原创点）

判定走**优先级链**而非平均：极端 > 高 > 中 > 低。只要命中一条极端规则（如 rm -rf /），整体就是极端；否则看最高一级。

两个量化指标：

- **爆炸半径指数（0-100）**：命中严重度权重（极端 100 / 高 40 / 中 12 / 低 3）累加封顶。
- **安全控制价值量化**：拦下后估算避免的事故响应工时（极端 8h / 高 4h / 中 1h / 低 0h），把「没发生的灾难」变成可感知数字。

退出码：0 通过 / 1 参数错 / 2 IO 错 / 3 未知命令 / 4 已拦截（高/极端）。第 4 态是 guard 系列的统一约定。

## 五、理论底座

- **瑞士奶酪模型**（Reason 1990）：没有单层防御能挡住一切，事故是多层孔洞对齐的结果。本包是工具层那片奶酪。
- **爆炸半径**（SRE 概念）：一次变更影响多少文件、多少数据、多少依赖方。
- **海因里希法则**（1:29:300）：大多数灾难之前都有可被看见的先兆——本包的价值在于把先兆显性化。
- **设计立场**：看清后果再决定，不硬禁止。硬禁止会逼出 `--no-verify`、sudo、裸 shell 绕过，那更糟。

详细论证见 `references/` 下三篇：`swiss-cheese-blast-radius.md`、`heinrich-law.md`、`defense-stance.md`。规则与理论数据见 `resources/`：`rules.json`、`delete-models.json`、`delete-domains.json`。

## 六、产物与退出码

- `blast_report.md`：单次扫描/预览产物，含判定、命中清单、爆炸半径、价值量化，JSON 尾附结构化结果。
- `guard-ledger.md`：多份报告聚合后的安全控制价值账本。

报告只写本地工作目录，不含任何凭据或网络地址。误报会杀死产品，故带 WHERE 的 SQL 自动降级、示例/教学/虚构语境经全局白名单放行、安全变体只作鼓励信号不当命中。
