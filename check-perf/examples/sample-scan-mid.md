# 性能阈值校验报告（check-perf v2.0.0）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**36/100**　可修正：3 / 不可修正：0　发现项：3　预计避免返工工时：3

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | PERF-WHILE-TRUE | loop | loop.py | 出现 while True 无限循环，若无超时/退出条件会占满 CPU | 可修正 | 为 while True 加退出条件或超时保护 |
| 中 | PERF-NPLUS1 | query | loop.py | 在循环里逐条查库（for ... in ... 内调用 .query/.filter/.all/.get），典型 N+1 查询 | 可修正 | 改为批量查询或 join，避免循环内单条查库 |
| 中 | PERF-SYNC-IN-ASYNC | blocking | loop.py | async 函数里调用同步阻塞（time.sleep/subprocess/os.system），会卡住整个事件循环 | 可修正 | 改用异步等价物（await asyncio.sleep / aiohttp） |

<!-- PERF_RESULT {"verdict": "中", "exposure_index": 36, "fixable": 3, "unfixable": 0, "findings": 3, "avoid_rework_hours": 3} -->
