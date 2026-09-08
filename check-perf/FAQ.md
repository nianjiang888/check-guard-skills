# check-perf 常见问题（FAQ）

| 场景 | 话术 |
|---|---|
| 「我的请求都走统一封装设了超时，还会报吗？」 | 可能。本包只看静态文本里是否出现 `timeout` 字样（不区分大小写）。若通过基类/中间件统一设置、源码字面不出现 `timeout`，仍会被报——可改成显式 timeout 或把文件加入测试白名单。 |
| 「为什么网络调用无 timeout 直接判高？」 | 因为 requests/httpx/fetch/socket/urllib 不设超时，一旦对端卡死就会永久挂起、占满线程或协程，几乎必然在某天拖垮服务，故定高级并建议修复（退出码 1）。 |
| 「while True 一定有问题吗？」 | 不一定。守护进程/轮询场景的 while True 常配退出或超时条件；本包只报「裸 while True」，由人判断是否真缺保护。 |
| 「循环里读本地 dict 也被报 N+1 了？」 | 会。PERF-NPLUS1 命中「for ... in ... + .get(」时可能误报（并非查库）；把测试文件命名带 test_/example/sample 会被自动跳过，也可调规则压制。 |
| 「async 里用 asyncio.sleep 会误报吗？」 | 不会。本包匹配的是 `time.sleep(`（而非 `asyncio.sleep(`），async def 内用 `await asyncio.sleep` 不会被判为阻塞。 |
| 「列表接口用了 .query 单条查询，为什么没报无分页？」 | 无分页规则只匹配 `.all()`/`findAll`/`list()` 这类整表返回；`.query(` 单条调用不算列表返回，故不触发，避免与 N+1 规则重复计数。 |
| 「和 guard-* 有什么区别？」 | guard-* 做运行期/深度防护，check-perf 做快检版（模式命中即报），入口不同、互补不替代。 |
| 「扫描会扫到测试文件吗？」 | 文件名含 test_/example/sample 或内容带明确测试标记（fixture/测试专用示例）会被跳过；真实代码即使含 example 等词也不会被跳过，以免漏报真实性能缺陷。 |
| 「支持哪些文件类型？」 | 任意文本文件（Python/JS/Go/YAML/JSON/TOML/Markdown 等），二进制自动跳过。 |
| 「怎样加新的性能规则？」 | 直接编辑 resources/rules.json，追加一条 `{"id": "...", "layer": "...", "kind": "regex", ...}`，引擎实时加载、无需改代码。 |
