# 配置校验报告（check-config v2.0.0）
扫描目标：`示例目录\case_mid\config.ini`
判定：**中**　验证暴露指数：**24/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：2

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | CFG-INVALID-LOGLEVEL | value | config.ini | 日志级别取值不在允许集合内 | 可修正 | 把日志级别设为 debug/info/warn/error/critical 之一 |
| 中 | CFG-ENV-MISMATCH | env | config.ini | 生产环境仍开启 debug | 可修正 | 生产环境关闭 debug |

<!-- CHECK_RESULT {"verdict": "中", "exposure_index": 24, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 2} -->
