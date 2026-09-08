# check-links 使用导航

> 死链与坏引用检测护栏（check-* 系列 #2，v2.0.0）。在文档/代码/配置上线前静态扫缺失的 import/include 引用、缺失的相对文件、语法非法链接、失效页内锚点、占位域名与空链接，算验证暴露指数并出可修正性报告。

## 文件导航

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 定位、能力边界、用法 |
| `scripts/check.py` | 校验引擎（scan/rules/ledger/version 四子命令） |
| `resources/rules.json` | 9 条检查规则 + 1 条安全变体（10 层） |
| `resources/check-links-models.json` | 方法论（可解析性/链接卫生/锚点唯一性/静态优先）+ 量化模型 |
| `resources/check-links-domains.json` | 报告字段、退出码、诚实边界、白名单说明 |
| `references/link-validation.md` | 死链检测方法论依据 |
| `references/common-pitfalls.md` | 常见坑位清单与误报控制 |
| `references/defense-stance.md` | 防御立场与诚实边界 |
| `FAQ.md` | 场景→话术映射表 |
| `SELF_EVAL.md` | 自评（TRACE 五维） |
| `CHANGELOG.md` | 版本记录 |
| `examples/` | 四档示例报告（极端/高/中/干净） |

## 快速使用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
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
- **可修正性**：每条标可修正/不可修正（本包默认均可修正，极端的 import 缺失也只是「补文件」即可）。
- **预计避免返工工时**：极端8/高4/中1/低0，为经验折算估算。
