# 数据 schema 校验报告（check-schema v2.0.0）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**21/100**　可修正：4 / 不可修正：0　发现项：4　预计避免返工工时：1

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | SCHEMA-NO-REQUIRED | required | schema.json | JSON Schema 声明了 properties 却没写 required 数组，调用方无法判断哪些字段必填 | 可修正 | 补上 required 数组列出必填字段 |
| 低 | SCHEMA-EMAIL-NO-FORMAT | format | schema.json | 出现 email/mail/邮箱 这类字段却没标 format: email，校验会放行进错格式 | 可修正 | 给邮箱字段加 format: email |
| 低 | SCHEMA-ENUM-MISSING | enum | schema.json | 出现 status/state/role/type/level 这类有限值字段却没标 enum，取值无约束 | 可修正 | 给有限值字段加 enum 枚举 |
| 低 | SCHEMA-NO-DESCRIPTION | doc | schema.json | schema 声明了 properties 却没有任何 description，消费者看不懂字段含义 | 可修正 | 为字段补 description |

<!-- SCHEMA_RESULT {"verdict": "中", "exposure_index": 21, "fixable": 4, "unfixable": 0, "findings": 4, "avoid_rework_hours": 1} -->
