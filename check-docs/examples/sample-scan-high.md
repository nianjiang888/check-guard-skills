# 文档一致性校验报告（check-docs v2.0.1）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**52/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：5

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | DOCS-BROKEN-LINK | link | readme.md | 文档引用的相对文件/资源不存在，读者点开即 404，文档与仓库实际结构不一致（缺失：missing-diagram.png） | 可修正 | 修正链接路径或补上被引用的文件 |
| 中 | DOCS-PLACEHOLDER | placeholder | readme.md | 文档仍含未填占位符（{{}}、TBD、待补充），对外发布会露出半成品 | 可修正 | 补全占位内容或移除该段落 |

<!-- DOCS_RESULT {"verdict": "高", "exposure_index": 52, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 5} -->
