# 文档一致性校验报告（check-docs v2.0.1）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**67/100**　可修正：4 / 不可修正：0　发现项：4　预计避免返工工时：6

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | DOCS-BROKEN-LINK | link | doc.md | 文档引用的相对文件/资源不存在，读者点开即 404，文档与仓库实际结构不一致（缺失：nope.md） | 可修正 | 修正链接路径或补上被引用的文件 |
| 中 | DOCS-STALE-TODO | staleness | doc.md | 文档声称已实现/已支持/已完成，却仍含 TODO/FIXME/待办 等未完成标记，文档与代码状态不一致 | 可修正 | 去掉与代码不符的完成声明，或补上对应实现 |
| 中 | DOCS-PLACEHOLDER | placeholder | doc.md | 文档仍含未填占位符（{{}}、TBD、待补充），对外发布会露出半成品 | 可修正 | 补全占位内容或移除该段落 |
| 低 | DOCS-HEADING-SKIP | structure | doc.md | Markdown 标题层级跳跃超过一级（如从 # 直接到 ###），大纲结构断裂、可读性差（层级 1 跳到 3） | 可修正 | 补齐中间层级或调整标题级别 |

<!-- DOCS_RESULT {"verdict": "高", "exposure_index": 67, "fixable": 4, "unfixable": 0, "findings": 4, "avoid_rework_hours": 6} -->
