---
name: check-perf
display_name: 性能基线检查
version: 2.0.0
description: 性能阈值与资源预算护栏（技术触发词：性能阈值校验/性能护栏/静态性能检查/超时检测/timeout 检查/N+1 查询检测/while True 检测/async 阻塞检测/分页检查/perf lint/resource budget guard；口语触发词：代码有没有性能雷区/网络调用是不是没设超时/有没有死循环/循环里是不是在逐条查库/async 里有没有同步阻塞/列表接口有没有加分页/上线前查一下性能问题；英文触发词：perf check / performance guard / timeout lint / n+1 query / blocking in async / no pagination / resource budget；一句话功能：在文档/代码/配置上线前静态扫网络调用未设 timeout、while True 无限循环、循环内 N+1 查询、async 同步阻塞、列表无分页等性能雷区，算验证暴露指数并出可修正性报告，看清性能护栏再发布）
license: MIT
---

# check-perf 是什么（人格锚：无，纯专业校验域）

check-perf 是 check-* 系列的新成员，定位是「性能阈值与资源预算护栏」。它不是压测平台（那是运行时的事），也不是性能剖析器（那是 cProfile/py-spy/pprof 的事），而是更日常的「性能 lint」——在你把代码推上线之前，先替你把最致命的性能雷区扫一遍：网络/IO 调用未设 timeout、while True 无限循环、循环内 N+1 查询、async 函数里的同步阻塞、列表接口无分页，以及是否已接入性能分析/压测工具。

性能缺陷是最隐蔽也最容易被放过的发布隐患：功能正常、构建通过，可一旦无 timeout 的网络调用遇到卡死的对端、或 while True 占满 CPU、或循环里逐条查库随数据量放大，服务就会假死或雪崩。check-perf 要做的，就是把这个「上线前最后一次性能体检」变成可重跑、可量化、留证据的静态检查，命中无 timeout 网络调用时直接给退出码 1 建议修复。

## 能做什么

- 扫代码里的性能雷区（Python/JS/Go/YAML/JSON/TOML/Markdown 等文本文件）。
- 高优先级判定：网络/IO 调用（requests/httpx/fetch/socket/urllib/aiohttp）没有设置 timeout。
- 中优先级判定：while True 无限循环、循环内逐条查库（N+1）、async 函数里的同步阻塞。
- 低优先级判定：列表接口无分页（.all()/findAll/list() 且无 limit/offset/page/cursor）。
- 鼓励信号：已接入性能分析/压测工具（cProfile/py-spy/pprof/locust/wrk/benchmark 等）。
- 算「验证暴露指数(0-100)」并出「可修正性」报告，退出码 0/1/2/3/4（1=发现性能护栏问题，建议修复后发布）。

## 边界（重要）

- 仅静态检测，不做运行时压测，故无法给出真实吞吐/延迟；只判定「是否触碰已知雷区」。
- 不修改文件、不拦截部署、不感知运行时真实流量、不承诺 100% 准确；是否阻断由 CI 策略决定。
- 与 guard-* 互补：check-perf 做性能快检版，guard-* 做运行期/深度版，入口不同、互不替代。

## 怎么用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

扫描结束后会输出判定（通过/低/中/高）、验证暴露指数、可修正/不可修正数量、发现项数与预计避免返工工时，并在报告末尾附上机器可读的 `PERF_RESULT {...}` 判定块，供 CI 程序化消费。

## 与其他 check 成员的关系

- check-config：校验配置项本身（必填/类型）。
- check-links：校验「引用关系」是否断裂。
- check-spelling：校验「文字与排版」是否干净。
- check-secret-scan：校验「明文密钥/凭证」是否泄露。
- check-perf（本包）：校验「性能雷区/资源预算」是否触碰。
- 后续 check-schema / check-api 等：分别深入数据结构与接口契约。

check-perf 专注「性能护栏有没有被写错/漏写」这一层，不做运行时性能量化。
