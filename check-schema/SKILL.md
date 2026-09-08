---
name: check-schema
display_name: Schema 结构与类型检查
version: 2.0.0
description: 数据 schema 校验护栏（技术触发词：schema 校验/JSON Schema 校验/data schema 校验/schema lint/字段约束校验/OpenAPI schema 校验/接口契约校验；口语触发词：我的 schema 有没有缺必填/字段类型没约束怎么办/邮箱字段要不要标 format/状态字段要不要加 enum/这个 JSON Schema 写得规不规范/接口文档字段说明不全；英文触发词：schema validation / JSON Schema check / data schema lint / missing required field / enum format check / openapi schema lint；一句话功能：在文档/接口/配置上线前静态扫 JSON Schema 是否缺 required/type/format/enum/description 等字段约束，算验证暴露指数并出可修正性报告，看清 schema 雷区再发布）
license: MIT
---

# check-schema 是什么（人格锚：无，纯专业校验域）

check-schema 是 check-* 系列的「数据 schema 校验护栏」。它不是类型推导引擎（那是运行时的事），也不是 schema 深度扫描器（那是 guard-schema 的事），而是更日常的「schema lint」——在你把文档、接口或配置推上线之前，先替你把最常见、最容易被看漏的字段约束坑扫一遍：缺 required 数组、缺 type 字段、邮箱字段没标 format:email、有限值字段没标 enum、字段没有 description，以及是否已接入 schema 校验工具（jsonschema/pydantic 等）。

字段约束缺失是最隐蔽也最容易被放过的结构缺陷：功能可能照常、构建通过，可一旦 schema 没写 required/type/format/enum，下游解析就会静默接受脏数据，问题要等到线上才暴露。check-schema 要做的，就是把这个「发布前最后一次 schema 体检」变成可重跑、可量化、留证据的静态检查。

## 能做什么

- 扫文档 / 接口 / 配置里的 JSON Schema 字段约束缺失（JSON/YAML/Markdown 等任意文本）。
- 结构级判定：声明了 properties 却没写 required（中）、全程没有 type（中）。
- 语义级判定：email/mail/邮箱 字段没标 format:email（低）、status/state/role/type/level 字段没标 enum（低）、字段无 description（低）。
- 鼓励信号：已接入 schema 校验工具（jsonschema/pydantic/sqlalchemy/cerberus 等），仅正向标记。
- 算「验证暴露指数(0-100)」并出「可修正性」报告，退出码 0/1/2/3/4（缺极端级约束缺失建议阻断）。

## 边界（重要）

- 仅静态检测，不做全量类型推导，故无法发现「字段类型逻辑矛盾」「跨字段依赖约束」；那是深度版或专业 schema 校验器的范围。
- 不修改文件、不拦截部署、不感知运行时真实调用、不承诺 100% 准确；是否阻断由 CI 策略决定。
- 与 guard-schema 互补：check-schema 做 schema 快检版，guard-schema 做深度版，入口不同、互不替代。

## 怎么用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

扫描结束后会输出判定（通过/低/中/高/极端）、验证暴露指数、可修正/不可修正数量、发现项数与预计避免返工工时，并在报告末尾附上机器可读的 `SCHEMA_RESULT {...}` 判定块，供 CI 程序化消费。

## 与其他 check 成员的关系

- check-config：校验配置项本身（必填/类型属其子集，但只查配置语义）。
- check-links：校验「引用关系」是否断裂。
- check-spelling：校验「文字与排版」是否干净。
- check-secret-scan：校验「明文密钥/凭证」是否泄露。
- check-schema（本包）：校验「数据 schema 字段约束」是否缺失。
- 后续 check-api 等：深入接口契约。

check-schema 专注「schema 有没有把字段约束写全」这一层，不做内容正确性判断。
