# 密钥明文快检报告（check-secret-scan v2.0.0）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**80/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：8

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | SECRET-HARDCODED-CRED | hardcoded | config.py | password/secret/token/api_key 等被硬编码为字面值，发布后易被读取 | 可修正 | 改为从环境变量 / 密钥管理器读取，不要在代码中写死 |
| 高 | SECRET-URL-CREDENTIAL | url-cred | config.py | URL 内嵌 user:pass（如 协议头://user:pass@host 这类写法），凭证会明文出现在地址里 | 可修正 | 把凭证移出 URL，改用 Authorization 头或环境变量 |

<!-- SECRET_RESULT {"verdict": "高", "exposure_index": 80, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 8} -->
