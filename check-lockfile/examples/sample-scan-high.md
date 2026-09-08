# 依赖锁定校验报告（check-lockfile v2.0.0）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**40/100**　可修正：1 / 不可修正：0　发现项：1　预计避免返工工时：4

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | LOCK-HTTP-SOURCE | source | package-lock.json | 锁文件从明文 http 源拉取依赖，传输可被中间人篡改注入恶意包 | 可修正 | 改用 https 源或自建可信镜像 |

<!-- LOCK_RESULT {"verdict": "高", "exposure_index": 40, "fixable": 1, "unfixable": 0, "findings": 1, "avoid_rework_hours": 4} -->
