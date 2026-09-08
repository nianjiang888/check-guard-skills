# guard-prompt 文件导航

> 提示注入检测。识别藏在网页/文档/邮件/图片描述/检索结果里的隐形指令，防止 AI 被远程操控。

## 30 秒上手

```bash
python scripts/guard.py scan <目录>      # 三维扫描 + 报告（高/极端退出码 4）
python scripts/guard.py rules            # 看三维检测规则库
python scripts/guard.py ledger <目录>    # 聚合价值账本
```

## 文件结构

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 定位、触发词海、理论地图、子命令速查、边界 |
| `scripts/guard.py` | 真引擎：三维检测 → 判定 → 出报告 → 价值账本 |
| `resources/rules.json` | 三维检测规则库（hijack/structure/intent）+ 隐形字符 + 白名单（可增改） |
| `resources/prompt-injection-models.json` | OWASP LLM01、直接/间接分类、注入风险分、StruQ/SecAlign、诚实边界 |
| `resources/prompt-domains.json` | 字段 / 边界 / 退出码定义 |
| `references/owasp-llm01.md` | OWASP LLM01:2025 与直接/间接分类、架构根因、硬数据 |
| `references/injection-defense.md` | 文本/模型/执行三层防御与诚实边界 |
| `references/indirect-injection.md` | 间接注入、RAG 投毒、多模态、上下文污染深潜 |
| `FAQ.md` | 场景 → 话术映射 + 边界声明 |
| `SELF_EVAL.md` | TRACE 五维自评 |
| `CHANGELOG.md` | 版本记录 |
| `examples/sample-scan.md` | 端到端走查示例 |

## 判定与退出码

| 等级 | 处置 | 退出码 |
|---|---|---|
| 低 | 可继续 | 0 |
| 中 | 可继续，留意角色覆盖/工具调用/上下文污染 | 0 |
| 高 | 拦下，需人工确认；必要时隔离来源 | 4 |
| 极端 | 禁止执行（无例外，人工复核并隔离） | 4 |

参数错 → 1，IO/运行错 → 2，未知子命令 → 3，已拦截 → 4。

## 边界

- 做：静态提示注入检测、可存档报告、注入类型与意图标注、拦截价值量化。
- 不做：运行时实时拦截、多模态内容分析、保证 100% 拦住所有注入。
- 隐私：扫描全程本地，不向外发送被扫目录内容。
