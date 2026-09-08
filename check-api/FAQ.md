# check-api 常见问题（FAQ）

| 场景 | 话术 |
|---|---|
| 「我的接口定义了操作但没写 responses，会报吗？」 | 会。只要出现 get/post/put/delete/patch 等操作且没有 responses 关键字，就命中 API-NO-RESPONSE-SCHEMA（中），调用方需要知道返回什么。 |
| 「只写了 200 响应，为什么还报？」 | 因为真实系统会出错。responses 里只有 200 而缺 4xx/5xx，客户端无法处理异常分支，命中 API-NO-ERROR-RESPONSE（中）。 |
| 「GET 带了 requestBody 会怎样？」 | 命中 API-GET-WITH-BODY（高）。GET 语义不应有请求体，通常是本该用 POST 却误用 GET，建议改动词或去掉 body。 |
| 「接口没有鉴权声明会报吗？」 | 会。定义了 paths 却全程没有 security/authorization/apiKey 等鉴权声明，命中 API-NO-AUTH（中），接口等于裸奔。 |
| 「为什么有的接口被要求补 description？」 | 命中 API-NO-DESCRIPTION（低）。定义了 paths 却没有任何 description，消费者看不懂用途，补上即可消除。 |
| 「已经用了 fastapi/swagger，还会扣分吗？」 | 不会。命中 openapi/swagger/pydantic/fastapi 等会记为正向信号（safe 层，仅鼓励），不计入发现项。 |
| 「它能发现字段类型写错吗？」 | 不能。本包只做确定性模式匹配，字段类型错误/必填漏标需要语义级 OpenAPI linter，二者可叠加。 |
| 「扫描会扫到测试文件吗？」 | 文件名含 test_/example/sample 或内容带明确测试标记（fixture/测试专用示例）会被跳过；真实接口定义即使含 example 等词也不会被跳过，以免漏报真实缺陷。 |
| 「支持哪些文件类型？」 | 任意文本文件（YAML/JSON/Python/Go/Markdown 等），二进制自动跳过。 |
| 「升级后规则变了，旧报告还作数吗？」 | 以当前版本 rules.json 为准。升级时建议按新规则重跑一次，examples/ 含四类样例报告可对照。 |
