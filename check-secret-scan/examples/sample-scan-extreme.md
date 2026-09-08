# 密钥明文快检报告（check-secret-scan v2.0.0）
扫描目标：`示例目录`
判定：**极端**　验证暴露指数：**100/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：16

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 极端 | SECRET-PRIVATE-KEY | private-key | key.pem | 代码/配置里出现 PEM 私钥块（-----BEGIN ... PRIVATE KEY-----），一旦提交即等同于私钥泄露 | 可修正 | 立即从仓库移除私钥，并到对应平台轮换/吊销该密钥 |
| 极端 | SECRET-KNOWN-PREFIX | known-prefix | key.pem | 命中已知前缀的明文密钥（AWS/GitHub/Slack/Google/OpenAI/GitLab/JWT 等），与私钥同属泄露级（命中 AWS Access Key ID） | 可修正 | 撤销并轮换该密钥，改用环境变量或密钥管理器注入 |

<!-- SECRET_RESULT {"verdict": "极端", "exposure_index": 100, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 16} -->
