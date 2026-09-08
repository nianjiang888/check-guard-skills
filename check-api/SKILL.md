---
name: check-api
display_name: API 契约检查
version: 2.0.1
description: 技术触发词：API 契约校验/OpenAPI 一致性检查/接口契约 lint/Swagger 规范检查/responses 缺失检测/接口鉴权缺失检查/GET 带 body 检测/API 规范护栏；口语触发词：接口写得规不规范/这个 API 契约有没有问题/响应结构没写全吗/接口怎么没鉴权/GET 请求带 body 是不是写错了/上线前帮我扫一下接口定义；英文触发词：API contract check / OpenAPI lint / response schema missing / missing auth in API / GET with body / API spec guard；一句话功能：在 API 定义（OpenAPI/Swagger/YAML/JSON）上线前静态校验响应结构、错误响应、鉴权、描述与动词用法是否齐全，算验证暴露指数并出可修正性报告，看清接口雷区再发布
license: MIT
---

# check-api 是什么（人格锚：无，纯专业校验域）

check-api 是 check-* 系列的新成员，定位是「API 契约一致性护栏」。它不是规范深度校验器（那是语义级 OpenAPI linter 的事），也不是运行时监控（那是网关/观测的事），而是更日常的「接口 lint」——在你把 API 定义推上线之前，先替你把最致命的契约坑扫一遍：漏写 responses、只有 200 缺错误响应、GET 带了 requestBody、全程没鉴权声明、接口没 description。

接口契约是最容易被「先上线后补文档」拖垮的发布缺陷：功能跑通、构建通过，可一旦响应结构/错误分支/鉴权声明没写清，调用方就只能靠猜，生产环境静默崩。check-api 要做的，就是把这个「发布前最后一次契约体检」变成可重跑、可量化、留证据的静态检查，命中契约缺口时给出退出码 1 建议修复后发布。

## 能做什么

- 扫 API 定义（OpenAPI/Swagger 的 YAML/JSON，或任意含接口描述的文本）。
- 契约缺口判定：漏写 responses（中）、只有 200 缺 4xx/5xx 错误响应（中）、GET 带 requestBody（高）、定义了 paths 却无鉴权声明（中）、无 description（低）。
- 正向信号：命中 openapi/swagger/pydantic/fastapi 等规范工具（safe 层，仅鼓励，不计入发现项）。
- 算「验证暴露指数(0-100)」并出「可修正性」报告，退出码 0/1/2/3/4（4 预留与系列一致，本包未启用极端级）。

## 边界（重要）

- 仅静态检测，不做语义级 schema 校验，故无法发现「字段类型错误/必填漏标/枚举越界」；那是专业 OpenAPI linter 的范围。
- 不修改文件、不拦截部署、不感知运行时真实调用、不承诺 100% 准确；是否阻断由 CI 策略决定。
- 与专业 OpenAPI linter 互补：check-api 做契约快检版，linter 做语义深度版，入口不同、互不替代。

## 怎么用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

扫描结束后会输出判定（通过/低/中/高/极端）、验证暴露指数、可修正/不可修正数量、发现项数与预计避免返工工时，并在报告末尾附上机器可读的 `API_RESULT {...}` 判定块，供 CI 程序化消费。

## 与其他 check 成员的关系

- check-config：校验配置项本身（必填/类型/密钥明文属其子集）。
- check-links：校验「引用关系」是否断裂。
- check-spelling：校验「文字与排版」是否干净。
- check-secret-scan：校验「明文密钥/凭证」是否泄露。
- check-api（本包）：校验「接口契约缺口」是否齐全。
- 后续 check-schema 等：深入数据结构与更多契约维度。

check-api 专注「响应/错误/鉴权/描述/动词」这一层，不做内容正确性判断。
