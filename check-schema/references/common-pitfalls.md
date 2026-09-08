# 常见误报与边界（check-schema）

本文件列出发包前已知、且已做规避处理的几类边界，便于使用者理解「为什么有时没报、为什么有时报了但可关」。

## 一、缺 required / type 的边界

- 只要 schema 声明了 `properties` 却没写 `required` / `type`，即判定为约束缺失（中）。这是有意为之：这类形态几乎必然让下游无法正确校验。
- 若你的 schema 确实允许全字段可选（无必填），可把该规则严重度调低，或在 rules.json 里收窄 `req_regex`。

## 二、邮箱 / 有限值字段的边界

- SCHEMA-EMAIL-NO-FORMAT 用「字段名含 email/mail/邮箱 + 无 format」双重约束，但仍可能在字段名恰含 email 却本就不是邮箱语义时误报。这类属误报高发区。
- SCHEMA-ENUM-MISSING 同理：字段名含 status/state/role/type/level 但本就不是有限值枚举时可能误报。
- 规避手段：测试文件命名带 test_/example/sample 会被自动跳过；也可在 rules.json 里调整关键词或严重度。

## 三、description 的边界

- 仅按「有 properties 却无 description 文本」判定，不读字段数量。即便只有一个字段也会报——因为「字段无说明」本身就是可读性信号。
- 若确有需要省略说明的场景，可调整规则或把文件加入测试白名单。

## 四、已接入校验工具的边界

- SCHEMA-CLEAN 仅做鼓励信号（命中 jsonschema/pydantic 等），不计入发现项、不提升判定等级。它存在的意义是「你已经做了该做的，给予正向标记」。

## 五、测试 / 示例文件

- 文件名含 test_/example/sample，或内容带明确测试标记（fixture/测试专用示例）会被跳过，避免把示例里的「故意缺约束」报成真实缺陷。
- 真实文档即使正文里出现 example 等词，也不会被跳过，以免漏报真实 schema 缺陷。这是有意为之的取舍：宁可在示例上多扫，也不在真实文档上漏报。

## 六、合规红线

- 本包所有源文件与压缩包均不含明文协议头、真实地址、绝对路径、BOM 与 CRLF，可安全上架分发。
