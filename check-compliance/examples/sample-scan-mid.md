# 合规点检报告（check-compliance v2.0.1）
扫描目标：`示例目录`
判定：**中**　验证暴露指数：**36/100**　可修正：3 / 不可修正：0　发现项：3　预计避免返工工时：3

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | COMPLIANCE-NO-DISCLAIMER | disclaimer | content.md | 内容涉及疗效/收益/投资/赚钱却无免责声明，易被认定为违规承诺 | 可修正 | 补上免责/风险提示声明 |
| 中 | COMPLIANCE-NO-SOURCE | source | content.md | 出现统计/百分比/倍数/增长等数据断言却无来源标注，无法核验 | 可修正 | 为数据补上来源标注 |
| 中 | COMPLIANCE-PII | pii | content.md | 内容含未脱敏 PII（身份证号/手机号/邮箱），对外发布有泄露风险 | 可修正 | 对 PII 做脱敏或移出公开内容 |

<!-- COMPLIANCE_RESULT {"verdict": "中", "exposure_index": 36, "fixable": 3, "unfixable": 0, "findings": 3, "avoid_rework_hours": 3} -->
