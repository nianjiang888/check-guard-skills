# 标书废标自查报告（check-tender-rejection v1.0.0）
扫描目标：`examples/tender-demo-mid.md`
判定：**中**　废标风险指数：**48/100**　可修正：4 / 不可修正：0　发现项：4　预计避免损失：¥200000

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 中 | qual_financial | qualification | tender-demo-mid.md | 财务报表或资信证明未检出（未检出：财务报[表告]、审计报告、资信证明 任一表述） | 可修正 | 补充近三年审计报告或银行资信证明 |
| 中 | qual_social_security | qualification | tender-demo-mid.md | 社保或纳税证明未检出（未检出：社保、纳税证明、社会保险 任一表述） | 可修正 | 补充近三个月社保缴纳证明或纳税证明 |
| 中 | form_attachment_checklist | formality | tender-demo-mid.md | 缺少附件清单或逐项响应表（未检出：附件清单、响应表、逐项响应 任一表述） | 可修正 | 附一张附件清单，对照招标文件逐项打钩，评委也省事 |
| 中 | cons_date_conflict | consistency | tender-demo-mid.md | 文档出现多个日期，需人工核对工期与进度计划逻辑（发现 4 个日期，需人工核对工期安排是否矛盾） | 可修正 | 核：开工不晚于竣工、工期天数与日历一致、与进度计划表一致 |

<!-- REJECTION_RESULT {"verdict": "中", "exposure_index": 48, "fixable": 4, "unfixable": 0, "findings": 4, "avoid_loss": 200000, "scan_time": "2026-09-06T06:31:49.325755"} -->
