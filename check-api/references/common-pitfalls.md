# 常见误报与边界（check-api）

本文件列出发包前已知、且已做规避处理的几类边界，便于使用者理解「为什么有时没报、为什么有时报了但可关」。

## 一、漏写 responses 的边界

- API-NO-RESPONSE-SCHEMA 用「出现动词(get/post/...)且无 responses」判定。若你的接口把 `responses` 写成别的形式（极少见），可能漏报或需调规则。
- 规避手段：统一用 `responses` 关键字；或调整规则的 `req_regex`/`absent_patterns`。

## 二、缺错误响应的边界

- API-NO-ERROR-RESPONSE 用「有 responses 且无 4xx/5xx」判定。仅匹配数字状态码 `4xx/5xx`；若你用非数字错误标识，需调整正则。
- 规避手段：补上 `400/401/403/404/500` 等错误响应即可消除该发现项。

## 三、GET 带 body 的边界

- API-GET-WITH-BODY 用 JSON 风格 `"get": { ... "requestBody"` 判定。YAML 里 `get:` 不带引号与花括号时不会误触发，符合预期。
- 若确有 GET 带体的历史接口（不符合 REST 语义），建议改为 POST；本包报出正是为了提示动词误用。

## 四、无鉴权的边界

- API-NO-AUTH 用「有 paths 且无 security/authorization/apiKey 等」判定。仅做声明级检查，不验证鉴权是否真的有效。
- 若你的鉴权关键字不在列表（如自研 `x-token`），可把关键字加入 `absent_patterns`。

## 五、缺 description 的边界

- API-NO-DESCRIPTION 用「有 paths 且无 description」判定。仅做关键词存在性检查；若 `description` 作为普通变量名恰好出现在别处，可能误报，可加白名单文件名规避。

## 六、测试 / 示例文件

- 文件名含 test_/example/sample，或内容带明确测试标记（fixture/测试专用示例）会被跳过，避免把示例里的「故意缺陷」报成真实问题。
- 真实接口定义即使正文里出现 example 等词，也不会被跳过，以免漏报真实缺陷。这是有意为之的取舍：宁可在示例上多扫，也不在真实定义上漏报。

## 七、合规红线

- 本包所有源文件与压缩包均不含明文协议头、真实地址、绝对路径、BOM 与 CRLF，可安全上架分发。
