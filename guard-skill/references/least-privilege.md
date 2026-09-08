# 最小权限：为什么"能跑"不等于"该给"

> guard-skill 的红线里，权限越界（远程命令执行、管道执行远程脚本、全局提权）权重最高。本篇解释其理论根基：最小权限原则，以及它在 AI Agent 时代为什么比过去更关键。

## 一、最小权限原则的来源

最小权限（Least Privilege）由 Saltzer 与 Schroeder 在《Protection and Control of Information Sharing in Multics》（*Communications of the ACM*, 1975）中列为操作系统八大设计原则之首：

> "每个程序、每个用户，应当仅拥有完成当前任务所必需的最小权限集合。"

这条原则的反面——"给了过多权限图省事"——正是绝大多数安全事故的根。一个本只需读配置文件的技能，如果顺手拿到了执行任意命令的能力，一旦它被注入，破坏半径就从"读了一个文件"变成"控制了整台机器"。

## 二、能力安全：权限应随对象携带

Dennis 与 Van Horn 在《Programming Semantics for Multiprogrammed Computations》（*CACM*, 1966）提出能力安全（Capability-based Security）：权限不应该是全局提升的"开关"，而应当**绑定在对象本身**——你拿到某个文件句柄，就只对这个文件有权，而不是对整个文件系统有权。

这对 AI 技能生态极其贴合：一个翻译技能需要的"能力"是"读这段文本、写回翻译结果"，而不是"执行 shell、访问 .ssh、联网外发"。guard-skill 的权限范围评估（统计网络 / 文件写入 / shell 三类信号）就是在本地层面近似能力安全的检查——如果一个技能的信号分布远超其声称的功能，本身就是红旗。

## 三、为什么 AI Agent 让最小权限更难、也更必要

传统软件的权限在部署时由运维静态授予，边界相对清晰。AI Agent 的权限是**运行时动态组合**的：它能读上下文、能调工具、能执行代码。一次提示注入，就能让一个"本应只总结文档"的 Agent 变成"读取凭据并外传"的执行体。

这带来两个推论：

1. **默认权限必须收窄**。Agent 不该默认拥有 shell 与全网外联；需要时才显式授予，且范围最小。
2. **每次能力使用都要可审查**。这正是 guard-skill 存在的意义——在能力被授予之前，先看清这个包到底会碰什么。

## 四、与"硬禁止"的边界

最小权限不等于"什么都禁"。Saltzer & Schroeder 自己也强调**可用性**——权限过小系统就无法工作。guard-skill 的设计因此不是"见 shell 就杀"，而是"高危动作要求看清后果再决定"：远程命令执行（SK-PRV-01）、管道执行远程脚本（SK-PRV-02）这类**高危组合**命中即升级判定，但中危的删除/提权信号（SK-PRV-03/04）只提示不阻断。硬禁止会逼用户 `--no-verify` 绕过，那是更坏的结局。

## 五、参考来源

- Saltzer, J. H. & Schroeder, M. D., *Protection and Control of Information Sharing in Multics*, CACM 17(7):388-402, 1974（1975 正式发表）.
- Dennis, J. B. & Van Horn, E. C., *Programming Semantics for Multiprogrammed Computations*, CACM 9(3):143-155, 1966.
- NIST SP 800-53, *AC-6 Least Privilege*.
- OWASP, *Top 10*（A04 不安全设计 / A05 安全配置错误）。
