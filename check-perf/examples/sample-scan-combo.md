# 性能阈值校验报告（check-perf v2.0.0）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**76/100**　可修正：4 / 不可修正：0　发现项：4　预计避免返工工时：7

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | PERF-NO-TIMEOUT | timeout | combo.py | 网络/IO 调用（requests/httpx/fetch/socket/urllib）没有设置 timeout，一旦对端卡死会永久挂起 | 可修正 | 给网络调用加上 timeout 参数 |
| 中 | PERF-WHILE-TRUE | loop | combo.py | 出现 while True 无限循环，若无超时/退出条件会占满 CPU | 可修正 | 为 while True 加退出条件或超时保护 |
| 中 | PERF-NPLUS1 | query | combo.py | 在循环里逐条查库（for ... in ... 内调用 .query/.filter/.all/.get），典型 N+1 查询 | 可修正 | 改为批量查询或 join，避免循环内单条查库 |
| 中 | PERF-SYNC-IN-ASYNC | blocking | combo.py | async 函数里调用同步阻塞（time.sleep/subprocess/os.system），会卡住整个事件循环 | 可修正 | 改用异步等价物（await asyncio.sleep / aiohttp） |

<!-- PERF_RESULT {"verdict": "高", "exposure_index": 76, "fixable": 4, "unfixable": 0, "findings": 4, "avoid_rework_hours": 7} -->
