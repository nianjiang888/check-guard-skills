# 标书废标自查报告（check-tender-rejection v1.0.0）
扫描目标：`examples/tender-demo-combo.md`
判定：**高**　废标风险指数：**100/100**　可修正：6 / 不可修正：3　发现项：9　预计避免损失：¥700000

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | qual_safety_license | qualification | tender-demo-combo.md | 安全生产许可证未检出（工程类招标必备）（未检出：安全生产许可证 任一表述） | 不可修正 | 补充安全生产许可证复印件，过期或缺失直接废标 |
| 高 | qual_pm_cert | qualification | tender-demo-combo.md | 项目经理注册证书未检出（未检出：注册建造师、项目经理.*证书、建造师注册证 任一表述） | 不可修正 | 补充项目经理注册建造师证及安全生产考核合格证 |
| 高 | form_seal_missing | formality | tender-demo-combo.md | 关键页签章缺失或未完成 | 可修正 | 逐页检查报价页、投标函、授权书是否已盖章签字，注意骑缝章 |
| 高 | form_deviation | formality | tender-demo-combo.md | 技术方案或商务条款偏离招标要求 | 不可修正 | 关键条款偏离通常直接废标，须逐条比对并书面响应，不可含糊 |
| 高 | cons_deadline_reverse | consistency | tender-demo-combo.md | 工期倒挂（开工日期晚于竣工日期）（开工 2027-09-01 晚于竣工 2026-07-15） | 可修正 | 修正工期起止日期，并同步修改进度计划与横道图 |
| 中 | qual_no_bribe | qualification | tender-demo-combo.md | 无行贿犯罪记录承诺或信用中国截图未检出（未检出：无行贿、信用中国、诚信承诺 任一表述） | 可修正 | 补充无行贿犯罪承诺书及信用中国查询结果截图 |
| 中 | form_attachment_checklist | formality | tender-demo-combo.md | 缺少附件清单或逐项响应表（未检出：附件清单、响应表、逐项响应 任一表述） | 可修正 | 附一张附件清单，对照招标文件逐项打钩，评委也省事 |
| 中 | cons_date_conflict | consistency | tender-demo-combo.md | 文档出现多个日期，需人工核对工期与进度计划逻辑（发现 3 个日期，需人工核对工期安排是否矛盾） | 可修正 | 核：开工不晚于竣工、工期天数与日历一致、与进度计划表一致 |
| 中 | format_placeholder_left | format | tender-demo-combo.md | 残留占位符未替换（低级但致命） | 可修正 | 全文搜索 XXX、待填、某某、TODO，逐个替换干净 |

<!-- REJECTION_RESULT {"verdict": "高", "exposure_index": 100, "fixable": 6, "unfixable": 3, "findings": 9, "avoid_loss": 700000, "scan_time": "2026-09-06T06:31:51.251960"} -->
