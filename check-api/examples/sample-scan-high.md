# API 契约校验报告（check-api v2.0.1）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**52/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：5

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | API-GET-WITH-BODY | verb | api_high.json | GET 操作带了 requestBody，GET 语义不应有请求体，通常是动词用错 | 可修正 | GET 改为 POST，或去掉 requestBody |
| 中 | API-NO-RESPONSE-SCHEMA | response | api_high.json | 接口定义了 get/post 等操作却没写 responses，调用方不知道返回什么 | 可修正 | 为每个操作补上 responses 定义 |

<!-- API_RESULT {"verdict": "高", "exposure_index": 52, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 5} -->
