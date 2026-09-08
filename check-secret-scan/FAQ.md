# check-secret-scan 常见问题（FAQ）

| 场景 | 话术 |
|---|---|
| 「我的密码是用环境变量读的，还会报吗？」 | 不会。本包只看静态文本里写死的字面值（带引号的 password="..."）。从环境变量 / 密钥管理器正确注入的不会误报。 |
| 「为什么命中 GitHub Token 直接判极端？」 | 因为 ghp_/gho_ 这类前缀几乎只出现在真实密钥上，命中即等于泄露，故定极端级并建议阻断（退出码 4）。 |
| 「测试代码里写了 password="test1234"，会不会误报？」 | 会。硬编码凭证在测试代码里是误报高发区；把测试文件命名带 test_/example/sample 会被自动跳过，也可调规则压制。 |
| 「它会不会漏报没有前缀的随机密钥？」 | 会。本包不做全量熵分析，无前缀的高熵随机密钥需要 guard-secret 深度版或专业密钥扫描器（gitleaks 等）来发现。 |
| 「.env 里只有 APP_ENV=production 也报？」 | 报。因为「被提交的 .env」本身就是风险信号（真实凭证常被顺手塞进去）。需要提交的非敏感文件请改名 .env.example。 |
| 「和 guard-secret 有什么区别？」 | guard-secret 做深度防护（分级 + 阻断建议 + 历史扫描），check-secret-scan 做快检版（模式命中即报），入口不同、互补不替代。 |
| 「扫描会扫到测试文件吗？」 | 文件名含 test_/example/sample 或内容带明确测试标记（fixture/测试专用示例）会被跳过；真实文档即使含 example 等词也不会被跳过，以免漏报真实密钥。 |
| 「支持哪些文件类型？」 | 任意文本文件（Python/JS/Go/YAML/JSON/ENV/TOML/Markdown 等），二进制自动跳过。 |
| 「升级后规则变了，旧报告还作数吗？」 | 以当前版本 rules.json 与 secret-patterns.json 为准。升级时本包会保留旧版说明，建议按新规则重跑一次。 |
| 「怎样加新的密钥前缀？」 | 直接编辑 resources/secret-patterns.json，追加 `{"name": "厂商名", "pattern": "正则"}`，引擎实时加载、无需改代码。 |
