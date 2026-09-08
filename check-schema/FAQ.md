# check-schema 常见问题（FAQ）

| 场景 | 话术 |
|---|---|
| 「我的 schema 用了 pydantic，还会报吗？」 | 不会当成缺陷。本包命中 jsonschema/pydantic 等会记为鼓励信号（SCHEMA-CLEAN），不计入发现项、不影响判定。 |
| 「为什么有 properties 没 required 直接判中？」 | 因为声明了 properties 却没写 required，调用方无法判断哪些字段必填，几乎必然让下游放行进缺字段，故定中级并建议修复。 |
| 「字段名就叫 email 但其实是别的意思，会不会误报？」 | 会。SCHEMA-EMAIL-NO-FORMAT 按「字段名含 email + 无 format」判定，命名巧合时会误报；测试文件会被自动跳过，也可调规则压制。 |
| 「status 字段不一定是枚举，也会被报吗？」 | 会。SCHEMA-ENUM-MISSING 按「字段名含 status/state/role/type/level + 无 enum」判定，确非有限值时属误报高发区，可手动关。 |
| 「只声明了 properties 但一个 description 都没写也报？」 | 报。因为「字段无说明」本身就是可读性信号（SCHEMA-NO-DESCRIPTION，低），消费者看不懂字段含义。 |
| 「和 guard-schema 有什么区别？」 | guard-schema 做深度防护（类型推导 + 依赖校验 + 历史扫描），check-schema 做快检版（模式命中即报缺约束），入口不同、互补不替代。 |
| 「扫描会扫到测试文件吗？」 | 文件名含 test_/example/sample 或内容带明确测试标记（fixture/测试专用示例）会被跳过；真实文档即使含 example 等词也不会被跳过，以免漏报真实缺陷。 |
| 「支持哪些文件类型？」 | 任意文本文件（JSON/YAML/Markdown/配置等），二进制自动跳过。 |
| 「升级后规则变了，旧报告还作数吗？」 | 以当前版本 rules.json 为准。升级时建议按新规则重跑一次，对比 SCHEMA_RESULT 判定块。 |
| 「怎样加新的约束规则？」 | 直接编辑 resources/rules.json，追加 `{"id": "...", "layer": "...", "kind": "regex", ...}`，引擎实时加载、无需改代码。 |
