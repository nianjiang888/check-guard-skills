# guard-dependency 依赖漏洞与投毒护栏检测报告

- 扫描时间：2026-09-02 09:13
- 目标：示例目录\extreme
- 引擎版本：2.0.0

## 一、判定

- **风险等级：极端**
- **依赖风险指数：100 / 100**
- **可治理性：3 处可治理 / 0 处不可治理**
- **处置建议：禁止合入（无例外，先升级/替换/加锁/换 https 源再引入）**

## 二、命中汇总（3 处）

- 按严重度：极端 2 / 高 1 / 中 0 / 低 0
- 按类型：混淆/投毒 2、来源可信 1

## 三、命中清单

| 严重度 | 类型 | 可治理 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 极端 | 混淆/投毒 | 可治理 | 内部/私有命名包走公开源（依赖混淆）(DEP-CONFUSION) | deps.txt:1 | internal-utils==1.0.0 | 建议：内部包走私有 registry 并设 namespace 隔离，禁止同名公开包可被拉取 |
| 极端 | 混淆/投毒 | 可治理 | 安装钩子执行任意代码(DEP-INSTALL-SCRIPT) | package.json:3 | "postinstall": "node -e process.exit(1)" | 建议：禁用自动 install scripts（npm ci --ignore-scripts），人工审计后再开 |
| 高 | 来源可信 | 可治理 | 配置文件指向自定义 registry(DEP-UNTRUSTED-REGISTRY) | pip.conf:2 | index-url = mirror.example/simple | 建议：受信源统一由组织级配置下发，项目级自定义源须评审 |

## 四、安全控制价值量化

- 本次若放行，估算可避免损失：约 8 小时依赖治理与漏洞修复

> 说明：本工具立场是「看清后果再决定」，不是硬禁止——硬禁止会逼人把依赖写死进 vendored 黑箱，那是更坏结局。判定依据为命中的严重度优先级链，非平均。诚实边界：仅做静态检测，不实际拦依赖解析；对运行时真实依赖树无感知；依赖后果取决于该包是否真被安装且被加载，本工具只量化静态可见风险。

```json
{"time": "2026-09-02 09:13", "target": "示例目录\\extreme", "verdict": "极端", "risk_index": 100, "governable": 3, "ungovernable": 0, "findings": 3, "avoided_govern_hours": 8}
```