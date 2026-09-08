# 合规点检报告（check-compliance v2.0.1）
扫描目标：`示例目录`
判定：**高**　验证暴露指数：**76/100**　可修正：4 / 不可修正：0　发现项：4　预计避免返工工时：7

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | COMPLIANCE-SUPERLATIVE | claim | content.md | 出现极限词（国家级/世界级/第一品牌/唯一指定/顶级/极致/百分百/全球领先/领导品牌/王牌/首选/绝无仅有/史无前例/空前/最强国/最先进），违反广告法风险高 | 可修正 | 删去极限词，改用可佐证的中性表述 |
| 中 | COMPLIANCE-NO-DISCLAIMER | disclaimer | content.md | 内容涉及疗效/收益/投资/赚钱却无免责声明，易被认定为违规承诺 | 可修正 | 补上免责/风险提示声明 |
| 中 | COMPLIANCE-NO-SOURCE | source | content.md | 出现统计/百分比/倍数/增长等数据断言却无来源标注，无法核验 | 可修正 | 为数据补上来源标注 |
| 中 | COMPLIANCE-PII | pii | content.md | 内容含未脱敏 PII（身份证号/手机号/邮箱），对外发布有泄露风险 | 可修正 | 对 PII 做脱敏或移出公开内容 |

<!-- COMPLIANCE_RESULT {"verdict": "高", "exposure_index": 76, "fixable": 4, "unfixable": 0, "findings": 4, "avoid_rework_hours": 7} -->
