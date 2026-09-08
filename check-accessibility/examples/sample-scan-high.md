# 可访问性校验报告（check-accessibility v2.0.1）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**52/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：5

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | A11Y-IMG-NO-ALT | img | page.html | <img> 缺少 alt 属性，屏幕阅读器无法传达图片内容，视障用户丢失信息 | 可修正 | 为每个 img 补上有意义的 alt 文本 |
| 中 | A11Y-NO-LANG | html | page.html | <html> 缺少 lang 属性，浏览器/屏幕阅读器无法正确选择语言与发音 | 可修正 | 为 <html> 补上 lang 属性（如 lang="zh-CN"） |

<!-- A11Y_RESULT {"verdict": "高", "exposure_index": 52, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 5} -->
