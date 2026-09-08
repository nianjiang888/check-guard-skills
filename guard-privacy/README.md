# guard-privacy 使用说明（v2.0.0）

PII 字段脱敏护栏。在代码发布前静态扫描 PII（身份证号、手机号、银行卡、姓名、地址、邮箱）字段的处置方式，算 PII 暴露指数，出可脱敏性报告，看清脱敏缺口再上线。

## 快速开始

```
# 扫描某目录，报告写到该目录下 privacy_report.md（高/极端退出码 4）
python scripts/guard.py scan <目录>

# 只看结构化命中（JSON）
python scripts/guard.py scan <目录> --json

# 列出全部 12 条规则
python scripts/guard.py rules

# 聚合目录下所有报告，生成价值账本 guard-ledger.md
python scripts/guard.py ledger <目录>

# 打印引擎版本
python scripts/guard.py version
```

## 子命令

| 子命令 | 作用 | 退出码 |
|--------|------|--------|
| `scan <目录>` | 扫描并出 privacy_report.md | 0 / 1 / 2 / 4 |
| `scan <目录> --json` | 同上，额外打印结构化命中 | 0 / 1 / 2 / 4 |
| `scan <目录> --out <文件>` | 指定报告输出路径 | 0 / 1 / 2 / 4 |
| `rules` | 列出 12 条 PII 脱敏护栏规则 | 0 |
| `ledger <目录>` | 聚合报告生成价值账本 | 0 / 1 |
| `version` | 打印引擎版本 | 0 |

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 通过（低危或无命中） |
| 1 | 参数错（缺目录 / 路径不存在） |
| 2 | IO·运行错（资源解析失败 / 报告写入失败） |
| 3 | 未知命令 |
| 4 | 已拦截（高/极端风险，建议不要直接上线） |

## 六层规则（12 条）

| 层 | 规则 | 严重度 | 可脱敏性 |
|----|------|--------|----------|
| pii_field PII 字段识别 | PII-HARDCODE 敏感字段明文入源码 | 极端 | 可脱敏 |
| pii_field PII 字段识别 | PII-ID-PATTERN 18 位身份证号字面 | 高 | 可脱敏 |
| pii_field PII 字段识别 | PII-PHONE-PATTERN 11 位手机号字面 | 高 | 可脱敏 |
| pii_field PII 字段识别 | PII-EMAIL-PATTERN 邮箱字面 | 中 | 可脱敏 |
| pii_field PII 字段识别 | PII-ADDRESS 住址字段明文 | 中 | 可脱敏 |
| pii_field PII 字段识别 | PII-MASK-MISSING 有 PII 字段却无脱敏函数（复合规则） | 中 | 可脱敏 |
| log 日志泄露 | PII-LOG-RAW 日志打印原始 PII | 极端 | 可脱敏 |
| log 日志泄露 | PII-PRINT-RAW 输出/打印原始 PII | 极端 | 可脱敏 |
| store 明文存储 | PII-STORE-PLAIN 明文存储 PII 字段 | 高 | 可脱敏 |
| export 返回/展示 | PII-EXPOSE-RESPONSE 接口返回直带完整 PII | 高 | 可脱敏 |
| external 外传第三方 | PII-EXTERNAL PII 外传给第三方（无脱敏） | 极端 | 可脱敏 |
| safe 安全变体 | PII-SAFE-DESENSITIZE 脱敏/加密/令牌化 | 低 | 可脱敏（仅鼓励） |

## 量化模型

- **PII 暴露指数**：命中严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低（取最高，非平均）。
- **可脱敏性维度**：每条标 可脱敏（可经脱敏/加密/令牌化治理），提示"这些点都该加护栏"。
- **安全控制价值量化**：极端 8h / 高 4h / 中 1h / 低 0h 的避免脱敏治理与合规排查工时。

## 报告样例（节选）

```
## 一、判定
- 风险等级：极端
- PII 暴露指数：100 / 100
- 可脱敏性：5 处可脱敏 / 0 处不可脱敏
- 处置建议：禁止上线（无例外，先加脱敏/令牌化/加密再发布）

## 三、命中清单
| 严重度 | 类型 | 可脱敏 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 极端 | 日志泄露 | 可脱敏 | 日志打印原始 PII(PII-LOG-RAW) | agent.py:3 | logger.info("用户身份证:" + id_card) | 建议：日志只记脱敏... |
```

## 诚实边界

- 仅静态检测，不实际拦数据；决策权在人。
- 对运行时真实数据流向无感知（PII 是否真落库/外传、是否已脱敏它不知道）。
- 不承诺 100%：变量改名、间接引用、解密再打印都会漏；个别普通字段会误报。
- 不评估数据敏感度等级，只量化静态可见风险。
- 详见 `references/defense-stance.md`。

## 文件结构

```
guard-privacy/
├── SKILL.md
├── scripts/guard.py
├── resources/{rules,privacy-models,privacy-domains}.json
├── references/{pii-detection,privacy-law,defense-stance}.md
├── FAQ.md  README.md  SELF_EVAL.md  CHANGELOG.md
└── examples/{sample-scan-extreme,high,mid,clean}.md
```
