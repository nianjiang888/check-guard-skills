# CI 配置校验报告（check-ci v2.0.0）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**24/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：2

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | CI-NO-TIMEOUT | timeout | ci.yml | CI 任务未设超时，卡死的步骤会一直占用 runner、拖垮整个流水线 | 可修正 | 为任务加上超时（如 timeout-minutes） |
| 中 | CI-PERMISSIONS-WIDE | permission | ci.yml | CI 授予过宽权限（write-all 或 contents: write），被攻陷的步骤可篡改仓库与发布 | 可修正 | 按最小权限收缩 scopes，仅授予必要权限 |

<!-- CI_RESULT {"verdict": "中", "exposure_index": 24, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 2} -->
