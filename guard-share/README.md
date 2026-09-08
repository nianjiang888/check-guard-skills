# guard-share 使用说明（v2.0.0）

外发文件泄露检查护栏（DLP）。在把文件发给外部（客户/合作方/公开渠道）前静态扫描内容边界，算外发泄露指数，出可溯源性报告，看清泄露面再决定发不发。

## 快速开始

```
# 扫描某目录，报告写到该目录下 share_report.md（高/极端退出码 4）
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
| `scan <目录>` | 扫描并出 share_report.md | 0 / 1 / 2 / 4 |
| `scan <目录> --json` | 同上，额外打印结构化命中 | 0 / 1 / 2 / 4 |
| `scan <目录> --out <文件>` | 指定报告输出路径 | 0 / 1 / 2 / 4 |
| `rules` | 列出 12 条外发泄露护栏规则 | 0 |
| `ledger <目录>` | 聚合报告生成价值账本 | 0 / 1 |
| `version` | 打印引擎版本 | 0 |

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 通过（低危或无命中） |
| 1 | 参数错（缺目录 / 路径不存在） |
| 2 | IO·运行错（资源解析失败 / 报告写入失败） |
| 3 | 未知命令 |
| 4 | 已拦截（高/极端风险，建议不要直接外发） |

## 六层规则（12 条）

| 层 | 规则 | 严重度 | 可溯源性 |
|----|------|--------|----------|
| pii PII 外泄 | SHARE-PII-ID 18 位身份证号字面（强 PII） | 高 | 视文件标记 |
| pii PII 外泄 | SHARE-PII-PHONE 11 位手机号字面（强 PII） | 高 | 视文件标记 |
| pii PII 外泄 | SHARE-PII-EMAIL 邮箱字面（PII） | 中 | 视文件标记 |
| secret 密钥外泄 | SHARE-SECRET-APIKEY 密钥/令牌明文赋值 | 极端 | 视文件标记 |
| secret 密钥外泄 | SHARE-SECRET-PRIVKEY 私钥块（PEM） | 极端 | 视文件标记 |
| secret 密钥外泄 | SHARE-SECRET-CRED 账号+密码配对明文 | 高 | 视文件标记 |
| sensitive 商业敏感 | SHARE-SENSITIVE-PRICE 报价/合同/成本金额 | 高 | 视文件标记 |
| sensitive 商业敏感 | SHARE-SENSITIVE-ROADMAP 未发布路线图/战略 | 中 | 视文件标记 |
| internal 内部文档 | SHARE-INTERNAL-DOC 内部架构/员工/薪酬信息 | 中 | 视文件标记 |
| classify 分类缺失 | SHARE-CLASSIFY-MISSING 含敏感内容但无密级标签 | 中 | 不可溯源 |
| watermark 溯源/蜜标 | SHARE-WATERMARK-MISSING 含敏感内容但无溯源标记 | 中 | 不可溯源 |
| safe 安全变体 | SHARE-SAFE 已标密级+溯源标记 | 低 | 仅鼓励信号 |

注：pii/secret/sensitive/internal 层的「可溯源性」由同文件是否带溯源标记动态判定（带标记=可溯源，无标记=不可溯源）；classify/watermark 复合规则只在标记缺失时触发，本身即不可溯源。

## 量化模型

- **外发泄露指数**：命中严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低（取最高，非平均）。
- **可溯源性维度**：每条内容泄露命中按同文件是否带密级/水印/canary/分类标签，实算「可溯源 / 不可溯源」。
- **安全控制价值量化**：极端 8h / 高 4h / 中 1h / 低 0h 的避免溯源补救与泄露处置工时。

## 报告样例（节选）

```
## 一、判定
- 风险等级：高
- 外发泄露指数：40 / 100
- 可溯源性：0 处可溯源 / 1 处不可溯源
- 处置建议：拦下，人工确认后再决定；外发内容必须先标密级、加溯源

## 三、命中清单
| 严重度 | 类型 | 可溯源 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 高 | PII 外泄 | 不可溯源 | 11 位手机号字面（强 PII）(SHARE-PII-PHONE) | 名单.md:5 | 客户联系电话 13800001111 | 建议：外发前脱敏（如 138****8000）... |
```

## 诚实边界

- 仅静态检测，不实际拦发送、不修改文件；决策权在人（看清后果再决定，不硬禁止）。
- 对文件最终是否真的发出、发给谁、通过什么渠道无感知。
- 不解析二进制实为图片/加密压缩包的内容（需先看原文）。
- 不承诺 100%：变量改名、间接引用会漏；个别普通字段会被误报。规则仅作提示。
- 溯源标记检测是「有/无」判断，不校验标记真伪。
- 详见 `references/defense-stance.md`。

## 文件结构

```
guard-share/
├── SKILL.md
├── scripts/guard.py
├── resources/{rules,share-models,share-domains}.json
├── references/{dlp-classification,leak-detection,defense-stance}.md
├── FAQ.md  README.md  SELF_EVAL.md  CHANGELOG.md
└── examples/{sample-scan-extreme,high,mid,clean}.md
```
