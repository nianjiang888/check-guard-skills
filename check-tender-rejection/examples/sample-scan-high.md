# 标书废标自查报告（check-tender-rejection v1.0.0）
扫描目标：`examples/tender-demo-high.md`
判定：**极端**　废标风险指数：**100/100**　可修正：10 / 不可修正：3　发现项：13　预计避免损失：¥1450000

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 极端 | form_price_over_limit | formality | tender-demo-high.md | 报价超出预算限价 | 可修正 | 核对招标文件最高限价，超出即废标，须重新组价 |
| 高 | qual_safety_license | qualification | tender-demo-high.md | 安全生产许可证未检出（工程类招标必备）（未检出：安全生产许可证 任一表述） | 不可修正 | 补充安全生产许可证复印件，过期或缺失直接废标 |
| 高 | qual_bid_bond | qualification | tender-demo-high.md | 投标保证金缴纳凭证未检出（未检出：投标保证金、保证金缴纳、保证金凭证 任一表述） | 可修正 | 补充保证金电汇回单或保函，注意金额、到账时间、账户名一致 |
| 高 | form_seal_missing | formality | tender-demo-high.md | 关键页签章缺失或未完成 | 可修正 | 逐页检查报价页、投标函、授权书是否已盖章签字，注意骑缝章 |
| 高 | form_validity_short | formality | tender-demo-high.md | 投标有效期可能不足招标文件要求 | 可修正 | 常见要求 90 天，核对标书承诺有效期是否不低于招标要求 |
| 高 | form_deviation | formality | tender-demo-high.md | 技术方案或商务条款偏离招标要求 | 不可修正 | 关键条款偏离通常直接废标，须逐条比对并书面响应，不可含糊 |
| 高 | cons_deadline_reverse | consistency | tender-demo-high.md | 工期倒挂（开工日期晚于竣工日期）（开工 2027-06-01 晚于竣工 2026-12-31） | 可修正 | 修正工期起止日期，并同步修改进度计划与横道图 |
| 高 | cons_cert_expired | consistency | tender-demo-high.md | 证书或资质已过期 | 不可修正 | 过期证书等同无效，须换成有效期覆盖投标期的版本 |
| 中 | qual_financial | qualification | tender-demo-high.md | 财务报表或资信证明未检出（未检出：财务报[表告]、审计报告、资信证明 任一表述） | 可修正 | 补充近三年审计报告或银行资信证明 |
| 中 | qual_no_bribe | qualification | tender-demo-high.md | 无行贿犯罪记录承诺或信用中国截图未检出（未检出：无行贿、信用中国、诚信承诺 任一表述） | 可修正 | 补充无行贿犯罪承诺书及信用中国查询结果截图 |
| 中 | form_attachment_checklist | formality | tender-demo-high.md | 缺少附件清单或逐项响应表（未检出：附件清单、响应表、逐项响应 任一表述） | 可修正 | 附一张附件清单，对照招标文件逐项打钩，评委也省事 |
| 中 | cons_date_conflict | consistency | tender-demo-high.md | 文档出现多个日期，需人工核对工期与进度计划逻辑（发现 3 个日期，需人工核对工期安排是否矛盾） | 可修正 | 核：开工不晚于竣工、工期天数与日历一致、与进度计划表一致 |
| 中 | cons_pm_mismatch | consistency | tender-demo-high.md | 项目人员与证书信息可能不一致 | 可修正 | 核：人员姓名、证书编号、注册单位三者一致，且与社保单位同名 |

<!-- REJECTION_RESULT {"verdict": "极端", "exposure_index": 100, "fixable": 10, "unfixable": 3, "findings": 13, "avoid_loss": 1450000, "scan_time": "2026-09-06T06:31:50.285264"} -->
