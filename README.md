# 代码检查与防护护栏技能集（Check + Guard）

27 个自包含 Agent 技能：检查校验类（check-*）+ 防护护栏类（guard-*），覆盖代码质量、合规、安全、隐私、成本等场景。

共 **27** 个技能包，全部自包含（包内即可跑通，无需额外依赖）。

## 技能一览

| # | 技能包 | 名称 | 做什么 |
|---|---|---|---|
| 1 | `check-accessibility` | 可访问性护栏（a11y lint） | 可访问性护栏（技术触发词：可访问性校验/无障碍检查/a11y lint/alt 属性检查/按钮标签检查；口语触发词：… |
| 2 | `check-api` | API 契约检查 | 技术触发词：API 契约校验/OpenAPI 一致性检查/接口契约 lint/Swagger 规范检查/respon… |
| 3 | `check-ci` | CI 流水线检查 | CI 配置护栏（技术触发词：CI 配置校验/流水线校验/工作流检查/CI 安全校验/yaml lint；口语触发词：… |
| 4 | `check-compliance` | 合规基线检查 | 技术触发词：合规点检/广告法极限词/免责声明缺失/数据来源标注/PII 脱敏/对外发布合规/文案合规检查/compl… |
| 5 | `check-config` | 配置项检查 | 配置与参数校验护栏（技术触发词：配置校验/config validate/参数检查/配置lint/必填项检查/类型校… |
| 6 | `check-docs` | 文档质量检查 | 文档校验护栏（技术触发词：文档校验/文档一致性校验/README 校验/文档 lint/死链检查/占位符检查/标题层… |
| 7 | `check-gov-doc-format` | 政府公文格式检查 | 公文格式终检（技术触发词：公文格式检查/公文格式终检/红头文件格式/GB/T 9704 合规/公文国标校验/发文字号… |
| 8 | `check-links` | 链接死链检查 | 死链与坏引用检测护栏（技术触发词：死链检测/断链检查/坏引用/链接校验/anchor 校验/相对路径校验/impor… |
| 9 | `check-lockfile` | 锁文件完整性检查 | 依赖锁定护栏（技术触发词：锁文件校验/依赖锁定校验/lockfile 检查/依赖完整性校验/浮动版本检查；口语触发词… |
| 10 | `check-perf` | 性能基线检查 | 性能阈值与资源预算护栏（技术触发词：性能阈值校验/性能护栏/静态性能检查/超时检测/timeout 检查/N+1 查… |
| 11 | `check-schema` | Schema 结构与类型检查 | 数据 schema 校验护栏（技术触发词：schema 校验/JSON Schema 校验/data schema … |
| 12 | `check-script-health` | 脚本健康检查 | 短视频脚本体检评分（技术触发词：脚本体检/脚本评分/短视频脚本检查/口播稿体检/脚本质量/完播率体检/开头钩子检查/… |
| 13 | `check-secret-scan` | 密钥明文快检 | 密钥明文快检护栏（技术触发词：密钥扫描/明文密钥检测/私钥检测/secret scan/凭证泄露检查/硬编码密码/h… |
| 14 | `check-spelling` | 拼写与术语检查 | 文字质量与排版检测护栏（技术触发词：错别字检查/拼写检查/排版检查/文字lint/叠字检测/中文标点检查/标题层级检… |
| 15 | `check-tender-rejection` | 标书废标自查 | 标书废标自查（技术触发词：废标自查/废标检查/废标风险/废标雷区/投标前检查/标书体检/资格性审查/形式性审查/响应… |
| 16 | `guard-command` | 命令执行护栏 | 高危命令与危险参数拦截（技术触发词：高危命令检测/危险参数/命令注入/最小权限/能力安全/blast radius/… |
| 17 | `guard-cost` | 成本护栏 | 在 while True 调大模型、无限重试、没预算上限、没熔断这些"删钱"操作上线前，先算一笔花费暴露指数、看清账… |
| 18 | `guard-delete` | 删除操作护栏 | 在 rm -rf /、DROP TABLE、git push --force 这类破坏性操作真正执行前，先算一遍爆炸… |
| 19 | `guard-dependency` | 依赖护栏 | 依赖漏洞与投毒护栏（技术触发词：依赖扫描/依赖投毒/依赖混淆/SLSA/SBOM/CVSS/typosquattin… |
| 20 | `guard-memory` | 记忆读写护栏 | AI 长期记忆与上下文污染防护：扫描记忆读写及 RAG 拼接代码，检测不可信来源直写、投毒指令固化、跨会话混染、系统… |
| 21 | `guard-network` | 网络访问护栏 | 外联与数据外泄通道检测（技术触发词：外联/出口/exfil/C2/反弹 shell/DNS 隧道/raw socke… |
| 22 | `guard-privacy` | PII 脱敏护栏 | PII 字段脱敏护栏（技术触发词：PII/个人信息/脱敏/去标识化/令牌化/假名化/k-匿名/差分隐私/PIPL/G… |
| 23 | `guard-prompt` | 提示词注入护栏 | 识别藏在网页、文档、邮件、图片描述、检索结果里的隐形指令，防止 AI 被远程操控。三维检测（指令劫持信号 → 结构/… |
| 24 | `guard-publish` | 发布前护栏 | 发布前合规检查护栏（技术触发词：发布前检查/发布合规/广告法极限词/疗效承诺/收益承诺/免责声明/隐私政策/数据来源… |
| 25 | `guard-secret` | 密钥安全护栏 | 提交代码或发布之前扫描密钥与凭据泄露。三层检测管线（正则查精度 → 香农熵查召回 → 上下文白名单降误报）识别 AP… |
| 26 | `guard-share` | 共享外发护栏 | 外发文件泄露检查护栏（技术触发词：外发文件/文件外发/DLP/数据防泄露/数据分级/溯源水印/蜜标/canary/P… |
| 27 | `guard-skill` | 第三方包安全审查 | 装任何第三方 Skill / MCP / 代码包之前的安全审查。扫描提示注入后门、硬编码密钥、数据外传、危险命令执行… |

## 目录结构

```
check-guard/
├── check-accessibility/
├── check-api/
├── check-ci/
├── check-compliance/
├── check-config/
├── ...（共 27 个技能目录）
```

每个技能包结构一致：`SKILL.md`（技能定义）、`scripts/`（引擎与冒烟测试）、`resources/`（规则与数据）、`references/`（依据）、`examples/`（输入输出样例）、`README.md`、`FAQ.md`、`CHANGELOG.md`。

## 本地使用

```
git clone <仓库地址>
```

把需要的技能目录整体复制到你的 Agent skills 目录即可。单个技能这样跑：

```
python <技能目录>/scripts/<引擎>.py --help
```

## 从 GitHub 导入到 SkillHub

每个技能独立目录，目录根即 `SKILL.md`，不含二进制文件。在 SkillHub 发布页选「从 GitHub 导入」，绑定账号后会自动扫出候选技能。

**注意：平台单次最多导入 5 个技能，27 个需要分 6 批。**

| 批次 | 技能 |
|---|---|
| 第 1 批 | `check-accessibility`、`check-api`、`check-ci`、`check-compliance`、`check-config` |
| 第 2 批 | `check-docs`、`check-gov-doc-format`、`check-links`、`check-lockfile`、`check-perf` |
| 第 3 批 | `check-schema`、`check-script-health`、`check-secret-scan`、`check-spelling`、`check-tender-rejection` |
| 第 4 批 | `guard-command`、`guard-cost`、`guard-delete`、`guard-dependency`、`guard-memory` |
| 第 5 批 | `guard-network`、`guard-privacy`、`guard-prompt`、`guard-publish`、`guard-secret` |
| 第 6 批 | `guard-share`、`guard-skill` |

## 许可

MIT

## 出品方与更多工具

本技能系列由墨金格团队出品。主产品[墨金格](https://www.mojinge.cloud/?utm_source=github_skills&utm_medium=readme&utm_campaign=skills_matrix)（mojinge.cloud）——把故事变成短剧：一句想法进来，一部能拍的剧本出去，分集剧情、人物 / 场景 / 道具资产、每集分镜提示词一次给齐；导入小说可走全流程改编（导入 → 故事中枢 → 分集大纲 → 改编剧本 → 分镜脚本）。按次付费，生成失败不扣费，邮箱即账号。

Made by the team behind [Mojinge](https://www.mojinge.cloud/?utm_source=github_skills&utm_medium=readme&utm_campaign=skills_matrix) — turn a story into a shootable screenplay: episode breakdowns, character/scene/prop assets, and per-shot prompts in one pass.

配套开源件 [ShotLock](https://github.com/nianjiang888/shotlock)：分镜脚本一致性校验引擎，十五条规则专抓角色漂移、越轴、语速超载，可作生成流程的卡口。
