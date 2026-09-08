# check-secret-scan 评测报告（EVALUATION REPORT）
> 版本：check-secret-scan 2.0.1　生成方式：`python scripts/smoke_test.py`
> 结论：**ALL PASS**（8 PASS / 0 FAIL）

## 一、冒烟测试（引擎实跑，独立子目录隔离）
| 场景 | 预期判定 | 退出码 | 可修正 | 不可修正 | 发现项 | 结果 |
|---|---|---|---|---|---|---|
| extreme | 极端 | 4 | 2 | 0 | 2 | PASS |
| high | 高 | 1 | 2 | 0 | 2 | PASS |
| mid | 中 | 1 | 1 | 0 | 1 | PASS |
| clean | 通过 | 0 | 0 | 0 | 0 | PASS |

## 二、子命令可用性
| 子命令 | 结果 |
|---|---|
| rules（列规则） | PASS |
| version（看版本） | PASS |
| 未知命令 rc=3 | PASS |
| 缺路径 rc=1 | PASS |

## 三、合规红线扫描
运行 `_tools/scan_redline.py` 对本包扫描：**RED-LINE PASS: 0 问题**（BOM/CRLF/明文协议头/真实地址/绝对路径 五项预检全过），可安全上架。

## 四、TRACE 5D 自评摘要
见 `SELF_EVAL.md`：Task 5.0 / Robustness 5.0 / Applicability 5.0 / Clarity 5.0 / Evidence 5.0，总分 5.0。

## 五、诚实边界
- 仅静态检测，不做全量熵分析，无法发现「无前缀的高熵随机密钥」（与 guard-secret 深度版分工）。
- 不修改文件、不拦截部署、不承诺 100% 准确；是否阻断由 CI 策略决定。
- 验证暴露指数为经验估算，真实风险以你的密钥管理记录为准。

---
_本报告由包内冒烟测试自动生成，可重跑复现。_
