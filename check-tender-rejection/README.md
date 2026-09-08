# check-tender-rejection 快速上手

标书提交前的最后一次体检。31 条废标雷区规则，纯标准库零依赖，跑完出一份带量化判定的自查报告。

## 30 秒上手

```bash
# 扫一份标书
python scripts/check.py scan 我的标书.md 自查报告.md

# 扫整个标书目录
python scripts/check.py scan ./投标资料/ 自查报告.md

# 只看结论（JSON，方便接脚本）
python scripts/check.py ledger ./投标资料/

# 看内置了哪些规则
python scripts/check.py rules

# 跑自检（改过规则后必做）
python scripts/smoke_test.py
```

## 报告长什么样

```
判定：**极端**　废标风险指数：**100/100**　可修正：10 / 不可修正：3　发现项：13　预计避免损失：¥1450000
```

跟着一张表，每行一条命中项：严重度、规则名、所在层、文件、说明、能否补救、怎么改。

报告末尾附机器可读判定块，供程序消费：

```json
{"verdict": "极端", "exposure_index": 100, "fixable": 10, "unfixable": 3, "findings": 13, "avoid_loss": 1450000, "scan_time": "..."}
```

## 五层规则在查什么

| 层 | 查什么 | 典型命中 |
|---|---|---|
| qualification 资格 | 营业执照、资质证书、安全生产许可证、授权委托书、保证金、业绩、人员证书 | 缺一项直接出局 |
| formality 形式 | 签章、投标有效期、报价超限价、投标函、条款偏离 | 可补救，但要赶在截止前 |
| consistency 一致性 | 金额大小写、工期逻辑、证书有效期、人员与证书匹配、页码 | 前后矛盾会被判非响应 |
| format 格式 | 字体字号页边距、占位符残留、公司名写错、联系方式 | 部分招标文件列为废标条款 |
| technical 技术 | 施工方案章节完整、技术参数逐条响应 | 关键参数不响应即废 |

完整 31 条见 `resources/rules.json`，改规则不用动代码。

## 四份样例（引擎实跑产出，非手写）

| 输入样例 | 判定 | 暴露指数 | 发现项 | 预计避免损失 | 退出码 |
|---|---|---|---|---|---|
| `examples/tender-demo-clean.md` | 通过 | 0/100 | 0 | ¥0 | 0 |
| `examples/tender-demo-mid.md` | 中 | 48/100 | 4 | ¥200,000 | 1 |
| `examples/tender-demo-high.md` | 极端 | 100/100 | 13 | ¥1,450,000 | 4 |
| `examples/tender-demo-combo.md` | 高 | 100/100 | 9 | ¥700,000 | 1 |

复现方式：`python scripts/smoke_test.py`，四档全 PASS 才算交付。

## 接进流程里

```bash
python scripts/check.py scan ./投标资料/ report.md
case $? in
  0) echo "干净，可以提交" ;;
  4) echo "命中必废标项，禁止提交" ; exit 1 ;;
  1) echo "有硬伤，先看报告再决定" ;;
  *) echo "命令或输入有问题" ; exit 2 ;;
esac
```

## 先说清楚做不到什么

- 只读纯文本（.md/.txt），Word/PDF 需先转文本，扫描件要先 OCR
- 不知道你这次招标的具体限价、资质等级、有效期要求，涉及数字的会提示"需人工核"
- 判不了量身定制的隐形排他条款，那需要专业法务
- 命中不等于必然废标，未命中也不保证中标——这是提交前的体检，不是中标保险

## 其他

- 方法论与规则设计思路：`references/rejection-methodology.md`
- 高频废标坑：`references/common-pitfalls.md`
- 误报怎么压：`references/defense-stance.md`
- 场景对照表：`FAQ.md`
