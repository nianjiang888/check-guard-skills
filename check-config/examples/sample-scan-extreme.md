# 配置校验报告（check-config v2.0.0）
扫描目标：`示例目录\case_extreme\config.ini`
判定：**极端**　验证暴露指数：**100/100**　可修正：0 / 不可修正：1　发现项：1　预计避免返工工时：8

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 极端 | CFG-SECRET-PLAINTEXT | secret | config.ini | 配置里明文写了密钥/令牌，泄露即需轮换 | 不可修正 | 把明文密钥移到环境变量或密钥管理服务，并轮换已暴露的密钥 |

<!-- CHECK_RESULT {"verdict": "极端", "exposure_index": 100, "fixable": 0, "unfixable": 1, "findings": 1, "avoid_rework_hours": 8} -->
