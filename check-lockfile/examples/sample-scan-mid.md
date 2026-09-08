# 依赖锁定校验报告（check-lockfile v2.0.0）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**24/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：2

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | LOCK-FLOATING | floating | package-lock.json | 锁文件仍含浮动版本（^ ~ >= * x），说明并未真正锁定，依赖可能随源漂移 | 可修正 | 用精确版本替换浮动范围，真正锁定依赖 |
| 中 | LOCK-NO-INTEGRITY | integrity | package-lock.json | 锁文件含依赖条目却无完整性哈希（integrity/sha/--hash），无法校验被篡改 | 可修正 | 为依赖条目补上完整性哈希 |

<!-- LOCK_RESULT {"verdict": "中", "exposure_index": 24, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 2} -->
