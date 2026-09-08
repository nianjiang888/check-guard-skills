# check-lockfile 常见问题（FAQ）

| 场景 | 话术 |
|---|---|
| 「我的 package-lock 里 version 写的是 ^4.17.0，会报吗？」 | 会。LOCK-FLOATING 命中期版本范围（^ ~ >= * x），说明并未真正锁定，依赖可能随源漂移，故定中级并建议换成精确版本。 |
| 「为什么 sha512-xxxx 里的 x 不会被误报成浮动版本？」 | 规则只认版本字段处的浮动符号（如 "version": "^..." 或 version: ^...），不会把 integrity 哈希里的 x 当成浮动版本，已专门规避。 |
| 「锁文件里某个依赖没有 integrity 字段，会报吗？」 | 会。LOCK-NO-INTEGRITY 命中有依赖条目（resolved/url/name/version）却无 integrity/sha 哈希，无法校验被篡改，故定中级并建议补哈希。 |
| 「从明文 http 源拉包为什么是高级？」 | LOCK-HTTP-SOURCE 定为高级：明文 http 传输可被中间人篡改注入恶意包，是供应链投毒的高危入口，建议改 https 或自建可信镜像。 |
| 「unresolved / extraneous 是什么？」 | 它们是包管理器标记的「未解析 / 悬空」依赖，说明依赖树不完整。LOCK-UNRESOLVED 定为中级并建议重新解析锁定、移除悬空条目。 |
| 「和 guard 的依赖安全成员有什么区别？」 | guard 深度版做依赖投毒检测、供应链溯源；check-lockfile 做快检版（模式命中即报缺锁定/缺哈希/明文源），入口不同、互补不替代。 |
| 「扫描会扫到测试文件吗？」 | 文件名含 test_/example/sample 或内容带明确测试标记（fixture/测试专用示例）会被跳过，避免把示例锁文件报成真实缺陷。 |
| 「支持哪些锁文件？」 | 任意文本锁文件（package-lock.json/yarn.lock/poetry.lock/Cargo.lock/requirements 等），二进制自动跳过。 |
| 「升级后规则变了，旧报告还作数吗？」 | 以当前版本 rules.json 为准。升级时建议按新规则重跑一次，对比 LOCK_RESULT 判定块。 |
| 「怎样加新的锁定规则？」 | 直接编辑 resources/rules.json，追加 {"id": "...", "layer": "...", "kind": "regex", ...}，引擎实时加载、无需改代码。 |
