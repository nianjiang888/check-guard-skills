# 链接校验报告（check-links v2.0.0）
扫描目标：`示例目录\case_mid`
判定：**中**　验证暴露指数：**24/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：2

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | LINK-ANCHOR-MISSING | anchor | guide.md | 页内锚点链接指向的标题/锚点不存在，点击跳转无效（缺失锚点：#nope） | 可修正 | 补上对应标题或修正锚点拼写 |
| 中 | LINK-PLACEHOLDER | placeholder | guide.md | 链接指向示例/占位域名（example/your-domain/placeholder/xxx/dummy），发布后读者打不开 | 可修正 | 替换为真实地址 |

<!-- LINK_RESULT {"verdict": "中", "exposure_index": 24, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 2} -->
