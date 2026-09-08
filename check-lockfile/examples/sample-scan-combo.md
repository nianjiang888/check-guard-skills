# 依赖锁定校验报告（check-lockfile v2.0.0）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**76/100**　可修正：4 / 不可修正：0　发现项：4　预计避免返工工时：7

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | LOCK-HTTP-SOURCE | source | package-lock.json | 锁文件从明文 http 源拉取依赖，传输可被中间人篡改注入恶意包 | 可修正 | 改用 https 源或自建可信镜像 |
| 中 | LOCK-FLOATING | floating | package-lock.json | 锁文件仍含浮动版本（^ ~ >= * x），说明并未真正锁定，依赖可能随源漂移 | 可修正 | 用精确版本替换浮动范围，真正锁定依赖 |
| 中 | LOCK-NO-INTEGRITY | integrity | package-lock.json | 锁文件含依赖条目却无完整性哈希（integrity/sha/--hash），无法校验被篡改 | 可修正 | 为依赖条目补上完整性哈希 |
| 中 | LOCK-UNRESOLVED | unresolved | package-lock.json | 锁文件含 unresolved/extraneous/missing 等未解析标记，依赖树不完整 | 可修正 | 重新解析并锁定依赖，移除悬空条目 |

<!-- LOCK_RESULT {"verdict": "高", "exposure_index": 76, "fixable": 4, "unfixable": 0, "findings": 4, "avoid_rework_hours": 7} -->
