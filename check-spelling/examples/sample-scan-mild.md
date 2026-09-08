# 拼写与排版校验报告（check-spelling v2.0.0）
扫描目标：`示例目录`
判定：**低**　验证暴露指数：**6/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：0

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 低 | SPELL-PUNCT-HALF | punct | doc.md | 中文后紧跟半角标点（, . ! ? ; :），中文排版应使用全角标点 | 可修正 | 把半角标点换成对应的全角标点 |
| 低 | SPELL-HEADING-SKIP | heading | doc.md | Markdown 标题层级跳跃（如无二级直接到三级），影响文档结构与目录生成（层级 1 跳到 3） | 可修正 | 补齐被跳过的层级，或调整标题层级顺序 |

<!-- SPELL_RESULT {"verdict": "低", "exposure_index": 6, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 0} -->
