# guard-secret 文件导航

> 密钥 / 凭据泄露扫描。提交 / 发布之前扫一遍，别把钥匙插在门上。

## 30 秒上手

```bash
python scripts/guard.py scan <目录>      # 三层扫描 + 报告（高/极端退出码 4）
python scripts/guard.py rules            # 看正则规则库与熵阈值
python scripts/guard.py ledger <目录>    # 聚合价值账本
```

## 文件结构

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 定位、触发词海、理论地图、子命令速查、边界 |
| `scripts/guard.py` | 真引擎：三层检测 → 判定 → 出报告 → 价值账本 |
| `resources/rules.json` | 正则规则库 + 熵阈值 + 白名单（可增改，不写死在代码） |
| `resources/secret-models.json` | 香农熵模型、三层管线、密钥暴露面指数、轮换原则 |
| `resources/secret-domains.json` | 字段 / 边界 / 退出码定义 |
| `references/shannon-entropy.md` | 香农熵与密钥检测理论 |
| `references/secret-detection-pipeline.md` | 三层检测管线与诚实边界（CWE-798） |
| `FAQ.md` | 场景 → 话术映射 + 边界声明 |
| `SELF_EVAL.md` | TRACE 五维自评 |
| `CHANGELOG.md` | 版本记录 |
| `examples/sample-scan.md` | 端到端走查示例 |

## 判定与退出码

| 等级 | 处置 | 退出码 |
|---|---|---|
| 低 | 可提交 | 0 |
| 中 | 可提交，留意高熵无上下文串 | 0 |
| 高 | 拦下，需人工确认；疑似泄露须轮换 | 4 |
| 极端 | 禁止提交（无例外，立即轮换） | 4 |

参数错 → 1，IO/运行错 → 2，未知子命令 → 3，已拦截 → 4。

## 边界

- 做：静态密钥扫描、可存档报告、疑似泄露标注与轮换建议、拦截价值量化。
- 不做：运行时密钥管理、动态内存/流量捕获、保证 100% 拦住所有泄露。
- 隐私：扫描全程本地，不向外发送被扫目录内容。
