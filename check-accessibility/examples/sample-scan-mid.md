# 可访问性校验报告（check-accessibility v2.0.1）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**24/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：2

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | A11Y-BTN-NO-LABEL | button | page.html | <button> 既无文字也无 aria-label，交互目标对辅助技术不可识别 | 可修正 | 为按钮补上可见文字或 aria-label |
| 中 | A11Y-NO-LANG | html | page.html | <html> 缺少 lang 属性，浏览器/屏幕阅读器无法正确选择语言与发音 | 可修正 | 为 <html> 补上 lang 属性（如 lang="zh-CN"） |

<!-- A11Y_RESULT {"verdict": "中", "exposure_index": 24, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 2} -->
