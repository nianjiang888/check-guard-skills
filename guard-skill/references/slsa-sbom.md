# 供应链完整性：SLSA 与 SBOM

> 本篇讲清楚一件事：当我们说"装一个第三方技能包之前要做入职背调"，这件事在软件供应链安全领域早有成熟框架。guard-skill 的溯源 + 全文件审查，本质上是在个人 / 小团队层面落地 SLSA 与 SBOM 的思想。

## 一、问题的性质：你装的不是功能，是一段会自己跑的代码

第三方 Skill、MCP server、agent 包，本质上和 npm 包、pip 包没有区别——它们进入你的环境后，拥有读文件、联网、执行命令的能力。区别只在于：开发者工具链的供应链审查已经高度自动化，而 AI 技能生态还停留在"看着名字顺眼就装"的阶段。

这正是 2020 年 SolarWinds、2021 年 Codecov 等事件反复证明的事实：**最危险的入侵往往不是正面突破，而是从你信任的供应链侧翼渗透**。美国行政令 EO 14028（2021）因此强制要求联邦软件提供软件物料清单（SBOM），把"你装的到底含了什么"变成强制披露项。

## 二、SLSA：从源码到交付的可溯源链

SLSA（Supply-chain Levels for Software Artifacts，Google 2021 提出，现由 OpenSSF 维护）定义了软件制品的四个等级，核心是保障**来源可追溯**与**构建完整性**：

- **来源可追溯（Provenance）**：这个制品是谁、在什么环境、由什么源码构建出来的？没有 provenance 的二进制，本质上等同于"来历不明的陌生人"。
- **构建完整性（Build integrity）**：构建过程是否防篡改？越高等级要求构建在隔离、可审计的环境中进行。

guard-skill 把 SLSA 的 provenance 思想降维到个人可用：审查一个技能包时，先问"它有作者吗？有版本吗？有更新时间吗？"——一份缺失 author / updated 的 SKILL.md，就相当于一个没有 provenance 的制品，信任分直接扣减。这不是吹毛求疵，而是供应链安全的第一性原则。

## 三、SBOM：软件里的"配料表"

SBOM（Software Bill of Materials，NTIA 在 EO 14028 下标准化的格式包含 SPDX、CycloneDX、SWID）要求软件披露它包含的所有组件及其版本。它的价值在于：**当某个底层组件爆出漏洞（如 Log4Shell / CVE-2021-44228），你能立刻查到自己的哪些制品受影响**。

对个人技能生态而言，完整 SBOM 尚不现实，但"全文件审查"是它的精神子集——guard-skill 逐文件扫描每条红线，等价于强制展开包的"配料表"，让藏在深层文件里的危险依赖、硬编码密钥、远程脚本无处遁形。

## 四、为什么是"审查"而非"禁止"

SLSA 与 SBOM 的目标从来不是把门关死，而是**让信任变得可验证、可审计**。一个 provenance 完整、红线零命中的包，理应顺畅安装；一个来历不明、命中多条高危红线的包，理应被拦下。这正是 guard-skill 四级判定的底层逻辑：用可溯源 + 可审计代替主观信任。

## 五、参考来源

- Google / OpenSSF, *SLSA: Supply-chain Levels for Software Artifacts*, 2021.
- NIST, *Executive Order 14028: Improving the Nation's Cybersecurity*, 2021（要求 SBOM）.
- NTIA, *The Minimum Elements For a Software Bill of Materials (SBOM)*, July 2021.
- MITRE, *Supply Chain Compromise* (ATT&CK T1195).
