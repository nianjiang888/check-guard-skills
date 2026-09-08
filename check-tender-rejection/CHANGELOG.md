# CHANGELOG

## [1.0.0] - 2026-09-06

首个版本。31 条检查规则 + 1 条鼓励信号，五层组织，四种判定机制。

### 结构

```
SKILL.md
README.md
FAQ.md
SELF_EVAL.md
CHANGELOG.md
scripts/check.py          引擎，纯标准库
scripts/smoke_test.py     冒烟测试，四档隔离实跑
resources/rules.json      31+1 条规则，外置
resources/check-tender-rejection-domains.json
resources/check-tender-rejection-models.json
references/rejection-methodology.md
references/common-pitfalls.md
references/defense-stance.md
examples/tender-demo-clean.md    输入样例 ×4
examples/tender-demo-mid.md
examples/tender-demo-high.md
examples/tender-demo-combo.md
examples/sample-scan-clean.md    引擎实跑产出报告 ×4
examples/sample-scan-mid.md
examples/sample-scan-high.md
examples/sample-scan-combo.md
```

### 规则设计

五层对应评审三道闸口：qualification（资格性审查）、formality（形式性审查）、consistency（一致性核查）、format（格式与低级错误）、technical（技术响应）。

四种判定机制：missing_any（同义词全未检出才算缺失）、regex（正向危险信号）、deadline（解析日期真比大小）、date/amount/pagegap（计算型，带 min_count 阈值）。

### 开发过程中修掉的三个真问题

1. **missing_any 同义词语义写反**。初版是"任一叫法未检出就报缺失"，导致写了"审计报告"的合规标书被误报成"缺财务报表"。同义词是 OR 关系，改为"全部叫法都没检出才算真缺失"。误报会直接杀死这类工具。
2. **工期倒挂只判断字段存在**。初版正则只要匹配到"开工日期 X …竣工日期 Y"就报，任何正常标书都会被判倒挂。改为解析出具体日期后真比大小，只在确实倒挂时报告。
3. **样例文件撞上引擎白名单**。样例命名为 sample-tender-*.md，被 `_skip_file` 的 sample 前缀规则整体跳过，四档扫描全部 0 命中。输入样例改名 tender-demo-*.md，报告输出名保持 sample-scan-*.md。

另修：日期正则不允许"2027 年 6 月"（数字与汉字间带空格），导致日期类规则全部漏检；报价超限表述漏了"高出"这一种常见说法。

### 验证

`python scripts/smoke_test.py` 四档全 PASS。clean 0 命中（证明零误报）、mid 48/100 退出码 1、high 100/100 退出码 4、combo 100/100 退出码 1。

### 已知限制

- 只读 .md/.txt，Word/PDF 需先转文本，扫描件需先 OCR
- rules.json 的 pattern 字段无正则合法性校验，写坏会崩（SELF_EVAL Robustness 维度已记）
- 规则是通用最大公约数，未按工程/货物/服务分化
- 读不到招标文件，涉及具体数字的比对只能提示人工核
