---
name: guard-privacy
display_name: PII 脱敏护栏
version: 2.0.0
description: PII 字段脱敏护栏（技术触发词：PII/个人信息/脱敏/去标识化/令牌化/假名化/k-匿名/差分隐私/PIPL/GDPR/身份证号/手机号；口语触发词：代码里有没有把身份证手机号明文打日志/接口返回有没有带完整手机号/PII 有没有脱敏/个人信息合规吗；英文触发词：PII / personal data / desensitization / tokenization / data masking / PIPL / GDPR；一句话功能：在代码发布前静态扫描 PII 字段的处置方式，算 PII 暴露指数并出可脱敏性报告，看清脱敏缺口再上线）
license: MIT
---

# guard-privacy · PII 字段脱敏护栏

## 这个包是谁（定位锚点）

guard-privacy 是 guard 安全护栏系列的第九条，专门管**文本里的 PII（个人敏感信息）字段**——身份证号、手机号、银行卡、姓名、地址、邮箱。它检测这些字段是怎么被处置的：有没有写进日志、存库明文、随接口返回、外传给第三方、硬编码进源码、或者全文压根没脱敏。它不替你脱敏，只把脱敏缺口摊开，让你看清再决定。

适用场景：AI Agent 自动生成的代码、第三方技能/MCP 包、CI 里要合入的业务代码——任何"处理个人信息"的地方。

## 它能做什么 / 不能做什么

能做的：
- 扫描目录，识别 6 类 PII 处置风险：PII 字段识别（硬编码/身份证/手机号/邮箱/地址字面）、日志泄露、明文存储、返回/展示暴露、外传第三方、以及"有 PII 却无脱敏函数"的缺口。
- 算**PII 暴露指数（0-100）**，按严重度优先级链给判定：极端 / 高 / 中 / 低。
- 标出每条命中的**可脱敏性**（这些暴露是否可经脱敏治理）。
- 量化**安全控制价值**（避免的脱敏治理与合规排查工时），并聚合出 `guard-ledger.md` 价值账本。
- 落**实物报告**（privacy_report.md + 机器可读 JSON 尾块），不是日志。

不能做的（诚实边界）：
- 不实际拦数据，决策权在你。
- 对运行时真实数据流向无感知（PII 是否真落库/外传、是否已脱敏它不知道）。
- 不承诺 100%：变量改名、间接引用、解密再打印都会漏；个别普通字段会误报。
- 不评估数据敏感度等级，只量化静态可见风险。

## 怎么用

```
python scripts/guard.py scan <目录>            # 扫描并出 privacy_report.md，高/极端返回码 4
python scripts/guard.py scan <目录> --json     # 同上加 --json 输出结构化命中
python scripts/guard.py rules                  # 列出 12 条 PII 脱敏护栏规则
python scripts/guard.py ledger <目录>          # 聚合该目录下所有 report 生成价值账本
python scripts/guard.py version                # 打印引擎版本
```

退出码：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / **4 已拦截（高/极端风险）**。

## 判定与量化（原创点）

- **PII 暴露指数**：命中严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低（取最高，不平均）。
- **可脱敏性维度**：每条标 可脱敏（可经脱敏/加密/令牌化治理），提示"这些点都该加护栏"。
- **安全控制价值量化**：极端 8h / 高 4h / 中 1h / 低 0h 的避免脱敏治理与合规排查工时。

## 理论根基（可溯源）

k-匿名（Sweeney 2002）、差分隐私（Dwork 2006）、PIPL/GDPR 个人信息保护义务、NER 用于 PII 发现。详细见 `references/pii-detection.md`、`references/privacy-law.md`、`references/defense-stance.md`。

## 文件导航

- `scripts/guard.py` — 主引擎（scan/rules/ledger/version 四子命令）
- `resources/rules.json` — 12 条规则（6 层）
- `resources/privacy-models.json` — 理论根基与量化模型
- `resources/privacy-domains.json` — 字段定义 / 诚实边界 / 退出码
- `references/` — 三篇长文方法论
- `FAQ.md` — 场景→话术映射与误用/升级回退
- `README.md` — 完整使用说明
- `SELF_EVAL.md` — 五维自评估（TRACE 5D）
- `CHANGELOG.md` — 变更记录
- `examples/` — 四档示例报告
