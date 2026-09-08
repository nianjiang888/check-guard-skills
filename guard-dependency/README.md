# guard-dependency 使用说明（v2.0.0）

依赖漏洞与投毒护栏。在合入依赖、发布前静态扫描依赖清单与安装配置，算依赖风险指数，出可治理性报告，看清治理缺口再合入。

## 快速开始

```
# 扫描某目录，报告写到该目录下 dependency_report.md（高/极端退出码 4）
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
| `scan <目录>` | 扫描并出 dependency_report.md | 0 / 1 / 2 / 4 |
| `scan <目录> --json` | 同上，额外打印结构化命中 | 0 / 1 / 2 / 4 |
| `scan <目录> --out <文件>` | 指定报告输出路径 | 0 / 1 / 2 / 4 |
| `rules` | 列出 12 条依赖护栏规则 | 0 |
| `ledger <目录>` | 聚合报告生成价值账本 | 0 / 1 |
| `version` | 打印引擎版本 | 0 |

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 通过（低危或无命中） |
| 1 | 参数错（缺目录 / 路径不存在） |
| 2 | IO·运行错（资源解析失败 / 报告写入失败） |
| 3 | 未知命令 |
| 4 | 已拦截（高/极端风险，建议不要直接合入） |

## 六层规则（12 条）

| 层 | 规则 | 严重度 | 可治理性 |
|----|------|--------|----------|
| manifest 依赖清单 | DEP-PIN-LOOSE 版本范围过松（未固定） | 中 | 可治理 |
| manifest 依赖清单 | DEP-GIT-URL 依赖取自任意 git/VCS 源 | 高 | 可治理 |
| version 版本风险 | DEP-EOL-KNOWN 命中已知投毒/废弃版本 | 高 | 可治理 |
| version 版本风险 | DEP-TYPOSQUAT 疑似 typosquatting 包名 | 高 | 可治理 |
| confusion 混淆/投毒 | DEP-CONFUSION 内部/私有命名包走公开源 | 极端 | 可治理 |
| confusion 混淆/投毒 | DEP-INSTALL-SCRIPT 安装钩子执行任意代码 | 极端 | 可治理 |
| confusion 混淆/投毒 | DEP-PROTOCOL-HIJACK 安装指向自定义源（源劫持） | 高 | 可治理 |
| integrity 完整性 | DEP-HTTP-SOURCE 依赖源使用明文 http 协议 | 极端 | 可治理 |
| integrity 完整性 | DEP-NO-INTEGRITY 有地址但无完整性哈希 | 中 | 可治理 |
| source 来源可信 | DEP-UNTRUSTED-REGISTRY 配置文件指向自定义 registry | 高 | 可治理 |
| source 来源可信 | DEP-FORK-PIN 依赖锁定到分支/commit 而非发布版 | 中 | 可治理 |
| safe 安全变体 | DEP-SAFE 固定版本+完整性校验 | 低 | 可治理（仅鼓励） |

## 量化模型

- **依赖风险指数**：命中严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低（取最高，非平均）。
- **可治理性维度**：每条标 可治理（可经升级/替换/加锁/换源/关脚本治理），提示"这些点都该补护栏"。
- **安全控制价值量化**：极端 8h / 高 4h / 中 1h / 低 0h 的避免依赖治理与漏洞修复工时。

## 报告样例（节选）

```
## 一、判定
- 风险等级：极端
- 依赖风险指数：100 / 100
- 可治理性：6 处可治理 / 0 处不可治理
- 处置建议：禁止合入（无例外，先升级/替换/加锁/换 https 源再引入）

## 三、命中清单
| 严重度 | 类型 | 可治理 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 极端 | 完整性 | 可治理 | 依赖源使用明文 http 协议(DEP-HTTP-SOURCE) | requirements.in:3 | --index-url pypi.internal/simple | 建议：所有源强制 https + 证书校验... |
```

## 诚实边界

- 仅静态检测，不解析真实依赖树、不实际拦安装；决策权在人。
- 不承诺 100%：变量改名、间接引用、vendored 黑箱、私有源白名单都会漏；个别公开 scoped 包名会误报。
- 自定义源不判死，一律提示人工确认（受信私有源同写法）。
- 详见 `references/defense-stance.md`。

## 文件结构

```
guard-dependency/
├── SKILL.md
├── scripts/guard.py
├── resources/{rules,dependency-models,dependency-domains}.json
├── references/{slsa-sbom,dependency-confusion,defense-stance}.md
├── FAQ.md  README.md  SELF_EVAL.md  CHANGELOG.md
└── examples/{sample-scan-extreme,high,mid,clean}.md
```
