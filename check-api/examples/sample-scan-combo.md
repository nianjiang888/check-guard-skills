# API 契约校验报告（check-api v2.0.1）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**79/100**　可修正：5 / 不可修正：0　发现项：5　预计避免返工工时：7

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | API-GET-WITH-BODY | verb | api_high.json | GET 操作带了 requestBody，GET 语义不应有请求体，通常是动词用错 | 可修正 | GET 改为 POST，或去掉 requestBody |
| 中 | API-NO-RESPONSE-SCHEMA | response | api_high.json | 接口定义了 get/post 等操作却没写 responses，调用方不知道返回什么 | 可修正 | 为每个操作补上 responses 定义 |
| 中 | API-NO-ERROR-RESPONSE | error | api_mid.yaml | 定义了 responses 却只有 200，没有 4xx/5xx 错误响应，客户端无法处理异常 | 可修正 | 补充 4xx/5xx 错误响应定义 |
| 中 | API-NO-AUTH | auth | api_mid.yaml | API 定义了 paths 却全程没有鉴权声明（security/authorization/apiKey 等），接口裸奔 | 可修正 | 为接口补充鉴权方案声明 |
| 低 | API-NO-DESCRIPTION | doc | api_mid.yaml | API 定义了 paths 却没有任何 description，消费者看不懂接口用途 | 可修正 | 为接口与参数补 description |

<!-- API_RESULT {"verdict": "高", "exposure_index": 79, "fixable": 5, "unfixable": 0, "findings": 5, "avoid_rework_hours": 7} -->
