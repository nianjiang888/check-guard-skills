# check-config 使用导航

> 配置与参数校验护栏（check-* 系列 #1，v2.0.0）。在配置/参数文件上线前静态扫必填项、类型、取值范围、明文密钥与环境一致性，算验证暴露指数并出可修正性报告。

## 文件导航

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 定位、能力边界、用法 |
| `scripts/check.py` | 校验引擎（scan/rules/ledger/version 四子命令） |
| `resources/rules.json` | 9 条检查规则 + 1 条安全变体（10 层） |
| `resources/check-config-models.json` | 方法论（十二要素/Schema 校验/密钥管理/环境一致性）+ 量化模型 |
| `resources/check-config-domains.json` | 报告字段、退出码、诚实边界、白名单说明 |
| `references/config-validation.md` | 配置校验方法论依据 |
| `references/common-pitfalls.md` | 常见坑位清单与误报控制 |
| `references/defense-stance.md` | 防御立场与诚实边界 |
| `FAQ.md` | 场景→话术映射表 |
| `SELF_EVAL.md` | 自评（TRACE 五维） |
| `CHANGELOG.md` | 版本记录 |
| `examples/` | 四档示例报告（极端/高/中/干净） |

## 快速使用

```
python scripts/check.py scan <配置目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

## 退出码

| 码 | 含义 |
|---|---|
| 0 | 干净，无发现 |
| 1 | 有发现（建议修复） |
| 2 | IO 或运行错误 |
| 3 | 未知命令 |
| 4 | 发现极端级问题（建议阻断发布，等同已拦下） |

## 量化口径

- **验证暴露指数**：各发现严重度权重累加（极端100/高40/中12/低3），上限 100。
- **可修正性**：每条标可修正/不可修正（明文密钥为不可修正，因需轮换）。
- **预计避免返工工时**：极端8/高4/中1/低0，为经验折算估算。
