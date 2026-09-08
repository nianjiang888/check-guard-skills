---
name: guard-network
display_name: 网络访问护栏
version: 2.0.0
description: 外联与数据外泄通道检测（技术触发词：外联/出口/exfil/C2/反弹 shell/DNS 隧道/raw socket/ngrok/信标/beacon；口语触发词：代码别往外连/数据别溜走/这段是不是在偷传数据/出口有没有护栏；英文触发词：network egress/exfiltration/C2 beacon/reverse shell/DNS tunneling；一句话功能：在代码发布前静态扫描外联通道与可疑外泄手法，算外联暴露指数并出可阻断性报告，看清出口再上线）
license: MIT
---

# guard-network · 外联 / 数据外泄通道检测

## 这个包是谁（定位锚点）

guard-network 是 guard 安全护栏系列的第八条，专门管**出口**：在代码发布前，静态扫一遍里面有没有往外连的通道、有没有数据外泄的经典手法。它不替你拦流量，只把"这段代码开了一个出口"这件事摊开，让你看清后果再决定。

适用场景：AI Agent 自动生成的脚本、第三方技能/MCP 包、CI 里要合入的代码——任何"跑起来可能往外发东西"的地方。

## 它能做什么 / 不能做什么

能做的：
- 扫描目录，识别 6 类外联/外泄通道：外联 POST、编码后外发、原始 socket 直连、DNS 隧道、C2 信标、反弹 shell、内网穿透、原始套接字造包。
- 算**外联暴露指数（0-100）**，按严重度优先级链给判定：极端 / 高 / 中 / 低。
- 标出每条命中的**可阻断性**（应用层能拦 vs 需内核/网络层才能管）。
- 量化**安全控制价值**（避免的外泄阻断与排查工时），并聚合出 `guard-ledger.md` 价值账本。
- 落**实物报告**（network_report.md + 机器可读 JSON 尾块），不是日志。

不能做的（诚实边界）：
- 不实际拦截任何流量，决策权在你。
- 对运行时真实外联无感知（代码跑没跑、网络放不放行它不知道）。
- 不承诺 100%：加密隧道、域名分段、变量延迟拼装都会漏；个别合法长随机串会误报。
- 不评估数据价值，只量化静态可见风险。

## 怎么用

```
python scripts/guard.py scan <目录>            # 扫描并出 network_report.md，高/极端返回码 4
python scripts/guard.py scan <目录> --json     # 同上加 --json 输出结构化命中
python scripts/guard.py rules                  # 列出 12 条外联/外泄通道规则
python scripts/guard.py ledger <目录>          # 聚合该目录下所有 report 生成价值账本
python scripts/guard.py version                # 打印引擎版本
```

退出码：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / **4 已拦截（高/极端风险）**。

## 判定与量化（原创点）

- **外联暴露指数**：命中严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低（取最高，不平均）。
- **可阻断性维度**：每条标 可阻断 / 不可阻断，提示出口防护该落在哪一层。
- **安全控制价值量化**：极端 8h / 高 4h / 中 1h / 低 0h 的避免损失工时。

## 理论根基（可溯源）

最小权限与出口过滤（CIS Controls）、MITRE ATT&CK T1041（C2 通道外泄）/ T1048（替代协议外泄）、C2 信标检测、DNS 隧道识别。详细见 `references/network-egress-theory.md`、`references/c2-detection.md`、`references/defense-stance.md`。

## 文件导航

- `scripts/guard.py` — 主引擎（scan/rules/ledger/version 四子命令）
- `resources/rules.json` — 12 条规则（6 层）
- `resources/network-models.json` — 理论根基与量化模型
- `resources/network-domains.json` — 字段定义 / 诚实边界 / 退出码
- `references/` — 三篇长文方法论
- `FAQ.md` — 场景→话术映射与误用/升级回退
- `README.md` — 完整使用说明
- `SELF_EVAL.md` — 五维自评估（TRACE 5D）
- `CHANGELOG.md` — 变更记录
- `examples/` — 四档示例报告
