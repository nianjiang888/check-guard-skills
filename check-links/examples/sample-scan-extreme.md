# 链接校验报告（check-links v2.0.0）
扫描目标：`示例目录\case_extreme`
判定：**极端**　验证暴露指数：**100/100**　可修正：1 / 不可修正：0　发现项：1　预计避免返工工时：8

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 极端 | LINK-IMPORT-MISSING | import | mod.py | 代码/配置里 import/require/include 的目标文件不存在，构建会直接失败（缺失：./missing_helper.py） | 可修正 | 补上缺失的被引用文件，或修正引用路径 |

<!-- LINK_RESULT {"verdict": "极端", "exposure_index": 100, "fixable": 1, "unfixable": 0, "findings": 1, "avoid_rework_hours": 8} -->
