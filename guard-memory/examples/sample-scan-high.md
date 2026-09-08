# guard-memory 记忆污染风险检测报告

- 扫描时间：2026-09-02 07:27
- 目标：示例目录
- 引擎版本：2.0.0

## 一、判定

- **风险等级：高**
- **记忆污染暴露指数：100 / 100**
- **可清洗性：4 处可清洗 / 0 处不可清洗**
- **处置建议：拦下，人工确认后再决定；记忆读写必须先加护栏**

## 二、命中汇总（4 处）

- 按严重度：极端 0 / 高 3 / 中 1 / 低 0
- 按类型：RAG 溢出 2、跨会话混染 2

## 三、命中清单

| 严重度 | 类型 | 可清洗 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 中 | RAG 溢出 | 可清洗 | 检索上下文无预算上限(MEM-RAG-NOCAP) | agent_mem.py:4 | docs = retrieve(query) | 建议：检索结果设 max_tokens/top_k/窗口上限，并按信任排序 |
| 高 | RAG 溢出 | 可清洗 | 不可信文档喂上下文无标注(MEM-RAG-UNTRUSTED) | agent_mem.py:4 | docs = retrieve(query) | 建议：外部内容入上下文前打"不可信"标签并隔离渲染 |
| 高 | 跨会话混染 | 可清洗 | 全局/共享记忆无隔离(MEM-CROSS-SESSION) | agent_mem.py:1 | global_memory = MemoryStore() | 建议：记忆按 user_id/session_id 分桶，禁止全局可读写单例 |
| 高 | 跨会话混染 | 可清洗 | 全局/共享记忆无隔离(MEM-CROSS-SESSION) | agent_mem.py:2 | global_memory.add(response.text) | 建议：记忆按 user_id/session_id 分桶，禁止全局可读写单例 |

## 四、安全控制价值量化

- 本次若放行，估算可避免损失：约 4 小时记忆清洗与纠偏响应

> 说明：本工具立场是「看清后果再决定」，不是硬禁止——硬禁止会逼用户绕过护栏，那是更坏结局。判定依据为命中的严重度优先级链，非平均。诚实边界：仅做静态检测，不实际拦请求；对运行时动态写入频次无感知；污染后果取决于下游如何使用记忆，本工具只量化静态可见风险。

```json
{"time": "2026-09-02 07:27", "target": "示例目录", "verdict": "高", "exposure_index": 100, "recoverable": "可清洗", "irrecoverable": 0, "findings": 4, "avoided_poison_hours": 4}
```