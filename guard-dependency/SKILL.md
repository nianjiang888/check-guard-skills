---
name: guard-dependency
display_name: 依赖护栏
version: 2.0.0
description: 依赖漏洞与投毒护栏（技术触发词：依赖扫描/依赖投毒/依赖混淆/SLSA/SBOM/CVSS/typosquatting/锁文件/完整性哈希/私有源/安装钩子/供应链；口语触发词：这个依赖安全吗/依赖有没有被投毒/锁文件有没有/依赖源是不是 https/安装脚本会不会乱跑/内部包名会不会被混淆；英文触发词：dependency scanning / supply chain / dependency confusion / typosquatting / lockfile / integrity hash；一句话功能：在合入依赖、发布前静态扫描依赖清单与安装配置，算依赖风险指数并出可治理性报告，看清治理缺口再合入）
license: MIT
---

# guard-dependency · 依赖漏洞与投毒护栏

## 这个包是谁（定位锚点）

guard-dependency 是 guard 安全护栏系列的第十条，专门管**第三方依赖的漏洞与投毒**。开源依赖一旦被投毒（依赖混淆 / typosquatting / 安装钩子执行恶意代码 / 锁文件缺失 / 走明文 http 源被中间人篡改），整条供应链都会沦陷。它不替你删包，只在合入依赖、发布前静态扫一遍清单与安装配置，算一笔「依赖风险指数」，落实物报告让你看清治理缺口再决定。

适用场景：AI Agent 自动装包、CI 合入前的依赖体检、第三方技能/MCP 包自带的依赖、任何「引入外部代码」的地方。

## 它能做什么 / 不能做什么

能做的：
- 扫描目录，识别 6 类依赖风险：依赖清单（浮动版本/git 源）、版本风险（已知投毒版本/typosquatting）、混淆/投毒（依赖混淆/安装钩子/源劫持）、完整性（明文 http 源/无哈希）、来源可信（自定义 registry/锁分支）、以及"有地址却无完整性哈希"的缺口。
- 算**依赖风险指数（0-100）**，按严重度优先级链给判定：极端 / 高 / 中 / 低。
- 标出每条命中的**可治理性**（这些风险是否可经升级/替换/加锁/换源治理）。
- 量化**安全控制价值**（避免的依赖治理与漏洞修复工时），并聚合出 `guard-ledger.md` 价值账本。
- 落**实物报告**（dependency_report.md + 机器可读 JSON 尾块），不是日志。

不能做的（诚实边界）：
- 不实际拦依赖安装，决策权在你。
- 不解析真实依赖树，对运行时实际装了哪些版本无感知。
- 不承诺 100%：变量改名、间接引用、vendored 黑箱、私有源白名单都会漏；个别公开 scoped 包名会误报。
- 不评估漏洞利用难度，只量化静态可见风险。

## 怎么用

```
python scripts/guard.py scan <目录>            # 扫描并出 dependency_report.md，高/极端返回码 4
python scripts/guard.py scan <目录> --json     # 同上加 --json 输出结构化命中
python scripts/guard.py rules                  # 列出 12 条依赖护栏规则
python scripts/guard.py ledger <目录>          # 聚合该目录下所有 report 生成价值账本
python scripts/guard.py version                # 打印引擎版本
```

退出码：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / **4 已拦截（高/极端风险）**。

## 判定与量化（原创点）

- **依赖风险指数**：命中严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低（取最高，不平均）。
- **可治理性维度**：每条标 可治理（可经升级/替换/加锁/换源/关脚本治理），提示"这些点都该补护栏"。
- **安全控制价值量化**：极端 8h / 高 4h / 中 1h / 低 0h 的避免依赖治理与漏洞修复工时。

## 理论根基（可溯源）

SLSA（供应链溯源 L1-L2）、SBOM（NTIA 最小元素 / EO 14028）、CVSS（漏洞评分）、依赖混淆（Birsan 2021）、typosquatting、幽灵依赖。详细见 `references/slsa-sbom.md`、`references/dependency-confusion.md`、`references/defense-stance.md`。

## 文件导航

- `scripts/guard.py` — 主引擎（scan/rules/ledger/version 四子命令）
- `resources/rules.json` — 12 条规则（6 层）
- `resources/dependency-models.json` — 理论根基与量化模型
- `resources/dependency-domains.json` — 字段定义 / 诚实边界 / 退出码
- `references/` — 三篇长文方法论
- `FAQ.md` — 场景→话术映射与误用/升级回退
- `README.md` — 完整使用说明
- `SELF_EVAL.md` — 五维自评估（TRACE 5D）
- `CHANGELOG.md` — 变更记录
- `examples/` — 四档示例报告
