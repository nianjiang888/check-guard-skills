# guard-memory 使用说明

> 系列：guard-*（12 条独立专业安全域）｜ 成员 #6：记忆 / 上下文污染防护
> 引擎版本：2.0.0 ｜ 零依赖（Python 标准库），装了即跑

## 一、它解决什么问题

AI Agent 的长期记忆（memory / notes / kb）和 RAG 上下文拼接，是被严重低估的攻击面：不可信内容写进记忆后跨会话反复生效，比单次注入更难治。guard-memory 在代码上线前静态扫一遍，把风险算清楚。

## 二、子命令

| 子命令 | 作用 | 退出码 |
|--------|------|--------|
| `scan <目录>` | 扫描目录，出 `memory_report.md`（判定/暴露指数/命中清单/价值量化） | 0 通过 / 4 已拦截 / 1 参数错 / 2 IO 错 |
| `rules` | 列出 12 条记忆污染规则库 | 0 |
| `ledger <目录>` | 聚合目录下所有 `memory_report.md`，生成 `guard-ledger.md` 价值账本 | 0 / 1 无报告 |
| `version` | 打印引擎版本 | 0 |

> 退出码总表：0 通过 / 1 参数错 / 2 IO·运行错 / 3 未知命令 / **4 已拦截（高/极端风险）**。

| 退出码 | 含义 |
|--------|------|
| 0 | 通过（低危/干净） |
| 1 | 参数错（缺路径/路径不存在） |
| 2 | IO·运行错（资源解析失败/报告写入失败） |
| 3 | 未知命令 |
| 4 | 已拦截（高/极端风险，建议不要直接上线） |

## 三、七层检测（12 规则）

| 层 | 规则 | 严重度 | 一句话 |
|----|------|--------|--------|
| 写入边界 | MEM-WRITE-UNTRUSTED | 高 | 不可信来源直写记忆，无信任边界 |
| 投毒信号 | MEM-POISON-PHRASE | 极端 | 记忆内容含「忽略/你现在是」类注入指令 |
| 投毒信号 | MEM-POISON-IMPERATIVE | 高 | 「记住你必须是/are」强制人设指令 |
| RAG 溢出 | MEM-RAG-NOCAP | 中 | 检索无长度/预算上限 |
| RAG 溢出 | MEM-RAG-UNTRUSTED | 高 | 不可信文档喂上下文无标注 |
| 跨会话 | MEM-CROSS-SESSION | 高 | 全局/共享记忆单例，跨主体混染 |
| 跨会话 | MEM-SESSION-NOID | 中 | 记忆读写无 user_id/session_id 作用域 |
| 溯源缺失 | MEM-NO-PROVENANCE | 中 | 记忆条目无 source/ts/author |
| 泄露 | MEM-LEAK-SYSPROMPT | 极端 | 系统提示写进记忆 |
| 泄露 | MEM-LEAK-SECRET | 极端 | 密钥/凭据写进记忆 |
| 安全变体 | MEM-SAFE-PROVENANCE | 低 | 写入带溯源（鼓励，不当命中） |
| 安全变体 | MEM-SAFE-QUARANTINE | 低 | 隔离/quarantine（鼓励，不当命中） |

## 四、原创量化点

- **记忆污染暴露指数（0-100）**：严重度权重累加（极端 100 / 高 40 / 中 12 / 低 3），封顶 100。
- **判定优先级链**：极端 > 高 > 中 > 低，按最坏一项定级，不被平均稀释。
- **安全控制价值量化**：把「没发生的污染扩散」折算成可感知工时（极端 8h / 高 4h / 中 1h / 低 0h）。
- **可清洗性维度**：每条命中标「可清洗/不可清洗」。

## 五、典型用法

```bash
# 扫一个 agent 项目，看记忆读写有没有污染雷区
python scripts/guard.py scan ./my_agent

# 跑出报告后，把多份报告聚成团队账本
python scripts/guard.py ledger ./scan_outputs
```

## 六、诚实边界

不实际拦截请求；不感知运行时动态写入；不承诺 100% 拦住；污染后果取决于下游如何使用记忆，本工具只量化静态可见风险。误报会杀死产品，故用「确实写记忆 + 确实不可信 + 强制指令短语检测」三重降误报。

## 七、文件导航

- `scripts/guard.py` 主引擎
- `resources/rules.json` `memory-models.json` `memory-domains.json` 规则与模型
- `references/` OWASP LLM07 记忆投毒 / RAG 投毒 / 防御立场
- `examples/` 极端 / 高 / 中 / 干净 四份样例报告
