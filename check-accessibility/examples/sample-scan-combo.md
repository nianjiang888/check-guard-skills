# 可访问性校验报告（check-accessibility v2.0.1）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**67/100**　可修正：4 / 不可修正：0　发现项：4　预计避免返工工时：6

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | A11Y-IMG-NO-ALT | img | page.html | <img> 缺少 alt 属性，屏幕阅读器无法传达图片内容，视障用户丢失信息 | 可修正 | 为每个 img 补上有意义的 alt 文本 |
| 中 | A11Y-BTN-NO-LABEL | button | page.html | <button> 既无文字也无 aria-label，交互目标对辅助技术不可识别 | 可修正 | 为按钮补上可见文字或 aria-label |
| 中 | A11Y-NO-LANG | html | page.html | <html> 缺少 lang 属性，浏览器/屏幕阅读器无法正确选择语言与发音 | 可修正 | 为 <html> 补上 lang 属性（如 lang="zh-CN"） |
| 低 | A11Y-HEADING-SKIP | structure | page.html | 标题层级跳跃超过一级（如从 h1 直接到 h3），大纲结构断裂、导航困难（层级 1 跳到 3） | 可修正 | 补齐中间层级或调整标题级别 |

<!-- A11Y_RESULT {"verdict": "高", "exposure_index": 67, "fixable": 4, "unfixable": 0, "findings": 4, "avoid_rework_hours": 6} -->
