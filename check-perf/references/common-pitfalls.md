# 常见误报与边界（check-perf）

本文件列出发包前已知、且已做规避处理的几类边界，便于使用者理解「为什么有时没报、为什么有时报了但可关」。

## 一、无 timeout 判定的边界

- PERF-NO-TIMEOUT 用「网络调用模式 + 全文无 timeout 字样」判定。若你通过统一封装（如基类给默认值）设置超时，但源码字面不出现 `timeout`，仍可能被报——这是模式检查的天然盲区，可改用显式 timeout 或白名单跳过。

## 二、N+1 判定的边界

- PERF-NPLUS1 用「for ... in ... + .query/.filter/.all/.get」双重约束，但可能在循环里调用 `.get(` 读取本地 dict/缓存时误报（并非查库）。
- 规避手段：测试文件命名带 test_/example/sample 会被自动跳过；也可在 rules.json 收窄关键词。

## 三、async 阻塞判定的边界

- PERF-SYNC-IN-ASYNC 要求同时出现 `async def` 与 `time.sleep(`/`subprocess.`/`os.system(`。注意 `await asyncio.sleep(` 不算阻塞（匹配的是 `time.sleep(` 而非 `asyncio.sleep(`），故不会误报；这是有意为之的区分。

## 四、列表无分页的边界

- PERF-NO-PAGINATION 仅匹配 `.all()`/`findAll`/`list()` 且全文无分页字样。`.query(` 单条调用不算列表返回，故不触发本规则（避免与 N+1 规则重复计数）。正常带 `limit/offset/page/cursor` 的写法不会误报。

## 五、测试 / 示例文件

- 文件名含 test_/example/sample，或内容带明确测试标记（fixture/测试专用示例）会被跳过，避免把示例里的「故意坏代码」报成真实问题。
- 真实代码即使正文里出现 example 等词，也不会被跳过，以免漏报真实性能缺陷。这是有意为之的取舍：宁可在示例上多扫，也不在真实代码上漏报。

## 六、合规红线

- 本包所有源文件与压缩包均不含明文协议头、真实地址、绝对路径、BOM 与 CRLF，可安全上架分发。
