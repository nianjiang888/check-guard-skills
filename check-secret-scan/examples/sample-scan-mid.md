# 密钥明文快检报告（check-secret-scan v2.0.0）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**12/100**　可修正：1 / 不可修正：0　发现项：1　预计避免返工工时：1

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | SECRET-ENV-FILE | env-file | .env | 检测到被提交进仓库的 .env 文件，里面通常含真实凭证 | 可修正 | 把 .env 加入 .gitignore，改用 .env.example 提交占位，真实值走 CI 变量 |

<!-- SECRET_RESULT {"verdict": "中", "exposure_index": 12, "fixable": 1, "unfixable": 0, "findings": 1, "avoid_rework_hours": 1} -->
