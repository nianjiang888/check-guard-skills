# guard-publish 使用说明（v2.0.0）

发布前合规检查护栏。在内容或工具对外发布前静态扫合规红线与发布清单，算发布合规指数，出可整改性报告，看清风险再发布。

## 快速开始

```
# 扫描某目录，报告写到该目录下 publish_report.md（高/极端退出码 4）
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
| `scan <目录>` | 扫描并出 publish_report.md | 0 / 1 / 2 / 4 |
| `scan <目录> --json` | 同上，额外打印结构化命中 | 0 / 1 / 2 / 4 |
| `scan <目录> --out <文件>` | 指定报告输出路径 | 0 / 1 / 2 / 4 |
| `rules` | 列出 12 条发布合规检查规则 | 0 |
| `ledger <目录>` | 聚合报告生成价值账本 | 0 / 1 |
| `version` | 打印引擎版本 | 0 |

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 通过（低危或无命中） |
| 1 | 参数错（缺目录 / 路径不存在） |
| 2 | IO·运行错（资源解析失败 / 报告写入失败） |
| 3 | 未知命令 |
| 4 | 已拦截（高/极端风险，建议不要直接发布） |

## 六层规则（12 条）

| 层 | 规则 | 严重度 | 可整改性 |
|----|------|--------|----------|
| meta 发布清单 | PUB-NO-META 发布元信息缺失（版本/更新日志/授权） | 中 | 可整改 |
| content 内容合规 | PUB-SUPERLATIVE 广告法极限词 | 高 | 可整改 |
| content 内容合规 | PUB-MEDICAL-CLAIM 医疗疗效承诺 | 极端 | 可整改 |
| content 内容合规 | PUB-INVEST-CLAIM 投资收益承诺 | 极端 | 可整改 |
| legal 法律声明 | PUB-NO-DISCLAIMER 涉敏感领域但无免责声明 | 高 | 可整改 |
| legal 法律声明 | PUB-NO-SOURCE 引用数据但未标注来源 | 中 | 可整改 |
| privacy 个人信息 | PUB-PII-RAW 发布内容含未脱敏个人信息 | 极端 | 不可整改 |
| privacy 个人信息 | PUB-NO-PRIVACY-POLICY 收集个人信息但无隐私政策 | 高 | 可整改 |
| credential 凭据与内网 | PUB-SECRET-HARDCODE 密钥/凭据硬编码 | 极端 | 不可整改 |
| credential 凭据与内网 | PUB-INTERNAL-ADDR 内网地址/运维入口暴露 | 高 | 不可整改 |
| credential 凭据与内网 | PUB-DEBUG-LEFTOVER 调试开关/测试数据残留 | 中 | 可整改 |
| safe 安全变体 | PUB-SAFE 免责声明+隐私政策+版本授权 | 低 | 仅鼓励信号 |

注：meta / legal / privacy(缺政策) 三条与 PUB-NO-META 为复合规则，用「req_regex（确有该类内容）+ absent_patterns（无配套声明）」做文件级判定；content 与 credential 层为逐命中模式，带上下文白名单降噪。

## 量化模型

- **发布合规指数**：命中严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低（取最高，非平均）。
- **可整改性维度**：发布前补得上/删得掉 → 可整改；一旦发布即不可逆 → 不可整改（未脱敏 PII、明文密钥、内网地址暴露）。
- **安全控制价值量化**：极端 8h / 高 4h / 中 1h / 低 0h 的避免发布后整改与召回工时。

## 报告样例（节选）

```
## 一、判定
- 风险等级：极端
- 发布合规指数：100 / 100
- 可整改性：1 处可整改 / 2 处不可整改
- 处置建议：禁止发布（无例外，先清掉密钥与个人信息、删除违规承诺再发）

## 三、命中清单
| 严重度 | 类型 | 可整改 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 极端 | 个人信息 | 不可整改 | 发布内容含未脱敏个人信息(PUB-PII-RAW) | 客户名单.md:2 | 客户 张三 身份证 110101199003071234 | 建议：发布前一律脱敏... |
```

## 诚实边界

- 仅静态检测，不实际拦发布、不修改内容；决策权在人（看清后果再决定，不硬禁止）。
- 对内容是否真的发布、发到哪个平台、覆盖多少受众无感知。
- 不替代法务合规审查与监管部门认定；地域与行业口径存在差异，规则只覆盖通用红线。
- 不可整改是「一旦发布就不可逆」的预警，不等于「已经发生泄露」。
- 不解析二进制实为图片/加密压缩包的内容（需先看原文）。
- 详见 `references/defense-stance.md`。

## 文件结构

```
guard-publish/
├── SKILL.md
├── scripts/guard.py
├── resources/{rules,publish-models,publish-domains}.json
├── references/{release-checklist,compliance-rules,defense-stance}.md
├── FAQ.md  README.md  SELF_EVAL.md  CHANGELOG.md
└── examples/{sample-scan-extreme,high,mid,clean}.md
```
