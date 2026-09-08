# 文档一致性校验报告（check-docs v2.0.1）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**24/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：2

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | DOCS-STALE-TODO | staleness | api.md | 文档声称已实现/已支持/已完成，却仍含 TODO/FIXME/待办 等未完成标记，文档与代码状态不一致 | 可修正 | 去掉与代码不符的完成声明，或补上对应实现 |
| 中 | DOCS-PLACEHOLDER | placeholder | api.md | 文档仍含未填占位符（{{}}、TBD、待补充），对外发布会露出半成品 | 可修正 | 补全占位内容或移除该段落 |

<!-- DOCS_RESULT {"verdict": "中", "exposure_index": 24, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 2} -->
