# guard-skill 文件导航

> 第三方技能 / MCP / 代码包供应链安全审查。装包之前的入职背调。

## 30 秒上手

```bash
python scripts/guard.py review <包目录>      # 完整背调 + 报告
python scripts/guard.py scan <包目录>        # 仅列红线命中
python scripts/guard.py rules                # 看红线规则库
python scripts/guard.py ledger <目录>        # 聚合价值账本
```

## 文件结构

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 定位、触发词海、理论地图、子命令速查、边界 |
| `scripts/guard.py` | 真引擎：扫描 / 溯源 / 权限评估 / 判定 / 出报告 / 价值账本 |
| `resources/rules.json` | 红线规则库（可增改，不写死在代码） |
| `resources/skill-supply-chain-models.json` | 信任分、判定链、价值量化模型 |
| `resources/skill-domains.json` | 字段 / 边界 / 退出码定义 |
| `references/slsa-sbom.md` | 供应链完整性：SLSA 与 SBOM |
| `references/least-privilege.md` | 最小权限原则及其在 Agent 时代的必要性 |
| `references/malicious-skill-patterns.md` | 恶意包与恶意技能的真实模式 |
| `FAQ.md` | 场景 → 话术映射 + 边界声明 |
| `SELF_EVAL.md` | TRACE 五维自评 |
| `CHANGELOG.md` | 版本记录 |
| `examples/sample-review.md` | 端到端走查示例 |

## 判定与退出码

| 等级 | 处置 | 退出码 |
|---|---|---|
| 低 | 可安装 | 0 |
| 中 | 可装，留意中危项与溯源缺失 | 0 |
| 高 | 拦下，需人工批准 | 4 |
| 极端 | 禁止安装（无例外） | 4 |

参数错 → 1，IO/运行错 → 2，未知子命令 → 3，已拦截 → 4。

## 边界

- 做：静态代码与元数据审查、可存档报告、拦截价值量化。
- 不做：运行时沙箱、动态行为分析、保证 100% 拦住所有后门。
- 隐私：审查全程本地，不向外发送被审包内容。
