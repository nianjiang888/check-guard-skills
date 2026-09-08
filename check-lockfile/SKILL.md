---
name: check-lockfile
display_name: 锁文件完整性检查
version: 2.0.0
description: 依赖锁定护栏（技术触发词：锁文件校验/依赖锁定校验/lockfile 检查/依赖完整性校验/浮动版本检查；口语触发词：我的锁文件真锁住没/依赖有没有被篡改风险/怎么看锁文件安不安全/锁文件能不能用明文源/依赖条目是不是没解析；英文触发词：lockfile check / dependency lock lint / floating version / lockfile integrity / http source in lock；一句话功能：在锁文件（package-lock/yarn.lock/poetry.lock 等）上线前静态扫浮动版本、缺完整性哈希、明文 http 源、未解析条目，算验证暴露指数并出可修正性报告，看清依赖雷区再发布）
license: MIT
---

# check-lockfile 是什么（人格锚：无，纯专业校验域）

check-lockfile 是 check-* 系列的「依赖锁定完整性护栏」。它不是依赖审计器（那要连仓库历史与漏洞库），也不是 SBOM 生成器（那是资产清点），而是更日常的「锁文件 lint」——在你把锁文件推上线之前，先替你把最常见、最容易被看漏的依赖锁定坑扫一遍：版本还是浮动的没真锁住、依赖条目没有完整性哈希、从明文 http 源拉包、依赖树里还挂着未解析标记。

文档/页面/锁文件「看起来没问题」往往只是没被认真扫过。这些缺陷不会让构建失败，却会在发布后被人点开死链、被视障用户卡住、被供应链投毒、被卡死的流水线拖垮。check-lockfile 要做的，就是把这道「发布前最后一次体检」变成可重跑、可量化、留证据的静态检查。

## 能做什么

- 扫各类锁文件（package-lock / yarn.lock / poetry.lock / Cargo.lock / requirements 锁定段等任意文本）。
- 结构级判定：仍含浮动版本 ^ ~ >= * x（中）、依赖条目无完整性哈希 integrity/sha（中）、从明文 http 源拉取（高）、含未解析标记 unresolved/extraneous/missing（中）。
- 鼓励信号：已启用依赖锁定与完整性校验（lockfile/依赖锁/完整性校验），仅正向标记。
- 算「验证暴露指数(0-100)」并出「可修正性」报告，退出码 0/1/2/3/4。

## 边界（重要）

- 仅静态检测，不连漏洞库、不解析真实依赖树拓扑，故无法发现「某版本本身有已知漏洞」这类需要情报的缺陷。
- 不修改文件、不拦截部署、不感知真实安装行为、不承诺 100% 准确；是否阻断由 CI 策略决定。
- 与 guard 系列的依赖相关成员互补：check-lockfile 做快检版（模式命中即报），深度版做依赖投毒/供应链溯源。

## 怎么用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

扫描结束后会输出判定（通过/低/中/高/极端）、验证暴露指数、可修正/不可修正数量、发现项数与预计避免返工工时，并在报告末尾附上机器可读的 `LOCK_RESULT {...}` 判定块，供 CI 程序化消费。

## 与其他 check 成员的关系

- check-config：校验配置项本身。
- check-links：校验「引用关系」是否断裂。
- check-spelling：校验「文字与排版」是否干净。
- check-secret-scan：校验「明文密钥/凭证」是否泄露。
- check-schema：校验「数据 schema 字段约束」是否缺失。
- check-docs：校验「文档与代码一致性」。
- check-lockfile（本包）：校验「依赖锁定完整性」——浮动版本、缺哈希、明文源、未解析。
- 后续 check-accessibility / check-ci：深入可访问性、CI 配置。

check-lockfile 专注「锁文件有没有真正把依赖锁死、锁干净」这一层。
