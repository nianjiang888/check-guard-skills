# CI 配置校验报告（check-ci v2.0.0）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**100/100**　可修正：4 / 不可修正：0　发现项：4　预计避免返工工时：10

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | CI-SECRET-PLAIN | secret | ci.yml | CI 配置里明文写了密码/令牌/密钥字面值，泄露即失陷 | 可修正 | 改用密钥管理器/加密变量引用，轮换已泄露凭据 |
| 高 | CI-NO-TRIGGER | trigger | ci.yml | 工作流没有任何触发条件（on / push / pull_request / schedule），实际上永远不会运行 | 可修正 | 补上触发条件（on: push / pull_request / schedule） |
| 中 | CI-NO-TIMEOUT | timeout | ci.yml | CI 任务未设超时，卡死的步骤会一直占用 runner、拖垮整个流水线 | 可修正 | 为任务加上超时（如 timeout-minutes） |
| 中 | CI-PERMISSIONS-WIDE | permission | ci.yml | CI 授予过宽权限（write-all 或 contents: write），被攻陷的步骤可篡改仓库与发布 | 可修正 | 按最小权限收缩 scopes，仅授予必要权限 |

<!-- CI_RESULT {"verdict": "高", "exposure_index": 100, "fixable": 4, "unfixable": 0, "findings": 4, "avoid_rework_hours": 10} -->
