# 性能阈值校验报告（check-perf v2.0.0）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**40/100**　可修正：1 / 不可修正：0　发现项：1　预计避免返工工时：4

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | PERF-NO-TIMEOUT | timeout | app.py | 网络/IO 调用（requests/httpx/fetch/socket/urllib）没有设置 timeout，一旦对端卡死会永久挂起 | 可修正 | 给网络调用加上 timeout 参数 |

<!-- PERF_RESULT {"verdict": "高", "exposure_index": 40, "fixable": 1, "unfixable": 0, "findings": 1, "avoid_rework_hours": 4} -->
