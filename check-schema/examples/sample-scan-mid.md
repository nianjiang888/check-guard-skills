# 数据 schema 校验报告（check-schema v2.0.0）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**27/100**　可修正：3 / 不可修正：0　发现项：3　预计避免返工工时：2

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | SCHEMA-NO-REQUIRED | required | schema.json | JSON Schema 声明了 properties 却没写 required 数组，调用方无法判断哪些字段必填 | 可修正 | 补上 required 数组列出必填字段 |
| 中 | SCHEMA-NO-TYPE | type | schema.json | schema 声明了 properties 却全程没有 type 字段，字段类型完全不约束 | 可修正 | 为每个字段补上 type |
| 低 | SCHEMA-NO-DESCRIPTION | doc | schema.json | schema 声明了 properties 却没有任何 description，消费者看不懂字段含义 | 可修正 | 为字段补 description |

<!-- SCHEMA_RESULT {"verdict": "中", "exposure_index": 27, "fixable": 3, "unfixable": 0, "findings": 3, "avoid_rework_hours": 2} -->
