# 配置校验报告（check-config v2.0.0）
扫描目标：`示例目录\case_high\config.ini`
判定：**高**　验证暴露指数：**100/100**　可修正：3 / 不可修正：0　发现项：3　预计避免返工工时：12

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | CFG-INSECURE-PROTOCOL | protocol | config.ini | 配置里用了明文 http 协议，传输可被窃听 | 可修正 | 内部/外部调用改用 https |
| 高 | CFG-HARDCODED-PATH | path | config.ini | 配置里硬编码了绝对路径，换环境即失效 | 可修正 | 改用相对路径或环境变量拼接 |
| 高 | CFG-PORT-OOR | type | config.ini | 端口号超出合法范围（>65535） | 可修正 | 把端口号改到 1–65535 之间 |

<!-- CHECK_RESULT {"verdict": "高", "exposure_index": 100, "fixable": 3, "unfixable": 0, "findings": 3, "avoid_rework_hours": 12} -->
