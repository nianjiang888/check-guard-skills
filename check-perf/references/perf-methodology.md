# 性能阈值校验方法论（check-perf）

本文件说明 check-perf 能判定什么、不能判定什么，以及各类规则背后的取舍。

## 一、能确定性判定的（本包范围）

1. 网络/IO 调用未设 timeout：匹配 `requests.get/post`、`httpx.get/post`、`fetch(`、`socket.connect`、`urllib.request`、`aiohttp.request`，且全文无 `timeout` 字样，定为高级。一旦对端卡死会永久挂起。
2. while True 无限循环：匹配 `while\s+True`，定为中级。无退出/超时条件会占满 CPU。
3. 循环内 N+1 查询：匹配「for ... in ...」且同时出现 `.query(`/`.filter(`/`.all(`/`.get(`，定为中级。典型 N+1 放大。
4. async 函数里的同步阻塞：匹配 `async def` 且同时出现 `time.sleep(`/`subprocess.`/`os.system(`，定为中级。会卡死事件循环。
5. 列表接口无分页：匹配 `.all()`/`findAll`/`list()` 且全文无 `limit/offset/page/cursor/分页/paginate`，定为低级。数据量大时撑爆内存。

## 二、不能判定、也不假装能判定的

- 真实吞吐/延迟/P99：本包不做运行时压测，只判定「是否触碰已知雷区」；那是 cProfile/py-spy/pprof/locust/wrk 等剖析/压测工具的活。
- 是否真的「慢」：一个无 timeout 的调用平时可能很快，本包只报风险模式，不报实测性能。
- 资源预算是否超支：本包不读取运行时指标，只看静态文本。

## 三、严重度设定

- 高：网络/IO 调用无 timeout。一旦对端卡死即永久挂起，定为高级并建议修复（退出码 1）。
- 中：while True 无限循环、循环内 N+1 查询、async 内同步阻塞。高概率雷区，但有时是测试/守护场景。
- 低：列表接口无分页、已接入性能分析/压测工具（安全变体，仅鼓励信号）。

## 四、为什么用「模式」而非实时压测

实时压测需要环境、数据与较长耗时，难进 CI、结果不稳定。本包只用不需语义理解的确定性模式，因此可重跑、可留证据、可进 CI，专门拦住「无 timeout / 无限循环 / N+1 / async 阻塞 / 无分页」这类一眼就能揪的性能雷区。

## 五、如何扩展规则库

直接编辑 resources/rules.json，追加 `{"id": "...", "layer": "...", "kind": "regex", "severity": "...", "intent": "...", "pattern"/"req_regex"/"req_all"/"absent_patterns": ..., "recoverable": true, "rec": "..."}` 即可，引擎在每次扫描时实时加载，无需改代码。
