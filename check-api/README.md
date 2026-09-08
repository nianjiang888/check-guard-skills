# check-api 导航索引

check-api 是 check-* 系列的新成员，定位「API 契约一致性护栏」。本文档是包内导航，帮你快速找到对应内容。

## 文件导航

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 包说明与触发词海、用法 |
| `scripts/check.py` | 检测引擎（纯标准库，确定性、可重跑） |
| `resources/rules.json` | 规则定义（6 条，含严重度与可修正性） |
| `resources/check-api-models.json` | 方法论与量化模型 |
| `resources/check-api-domains.json` | 报告字段、退出码、诚实边界 |
| `references/api-contract-methodology.md` | 检测方法论与取舍 |
| `references/common-pitfalls.md` | 常见误报与边界 |
| `references/defense-stance.md` | 防御立场与诚实声明 |
| `FAQ.md` | 场景→话术映射 |
| `SELF_EVAL.md` | 自评（TRACE 5D） |
| `CHANGELOG.md` | 版本记录 |
| `examples/` | 四类扫描样例报告 |

## 子命令

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

## 退出码

| 码 | 含义 |
|---|---|
| 0 | 通过（无发现项） |
| 1 | 发现中/高级契约问题（建议修复后发布） |
| 2 | 运行错误（路径不存在 / 规则读取失败 / 报告写入失败） |
| 3 | 未知命令 |
| 4 | 预留：极端级问题（本包未启用极端级规则，保留与系列一致的退出码位） |

## 量化模型（与系列统一）

- 维度：可修正性
- 验证暴露指数：各发现严重度权重累加（极端100/高40/中12/低3），上限 100
- 预计避免返工工时：各发现严重度对应工时累加（极端8/高4/中1/低0）
- 报告末尾 `API_RESULT {...}` 为机器可读判定块，供 CI 消费
