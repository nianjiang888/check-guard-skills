# check-ci 常见问题（FAQ）

| 场景 | 话术 |
|---|---|
| 「我的 CI 里明文写了 API_KEY: sk_live_xxx，会报吗？」 | 会。CI-SECRET-PLAIN 命中 password/token/secret/api_key/access_key 后跟 10 位以上字面值，泄露即失陷，故定高级并建议改密钥管理器引用、轮换已泄露凭据。 |
| 「任务没写 timeout 会怎样？」 | CI-NO-TIMEOUT 定为中级（限 yml/yaml）：卡死的步骤会一直占用 runner、拖垮整个流水线，建议加 timeout-minutes。 |
| 「permissions: write-all 为什么是中级？」 | CI-PERMISSIONS-WIDE 定为中级：过宽权限让被攻陷的步骤可篡改仓库与发布，建议按最小权限收缩 scopes。 |
| 「工作流没有任何 on: / push: 会报吗？」 | 会。CI-NO-TRIGGER 定为高级（限 yml/yaml）：没有任何触发条件的工作流实际上永远不会运行，是个「假流水线」，建议补 on: push/pull_request/schedule。 |
| 「和 check-secret-scan 有什么区别？」 | check-secret-scan 做全仓库明文密钥扫描；check-ci 聚焦 CI 配置里的高危明文凭据，并额外查超时/权限/触发这类流水线结构问题，入口不同、互补不替代。 |
| 「扫描会扫到测试文件吗？」 | 文件名含 test_/example/sample 或内容带明确测试标记（fixture/测试专用示例）会被跳过，避免把示例配置报成真实缺陷。 |
| 「支持哪些 CI 配置？」 | 任意 YAML 流水线（GitHub Actions / GitLab CI / 通用 yaml），二进制自动跳过；超时/密钥/权限/触发规则按 .yml/.yaml 限定生效。 |
| 「升级后规则变了，旧报告还作数吗？」 | 以当前版本 rules.json 为准。升级时建议按新规则重跑一次，对比 CI_RESULT 判定块。 |
| 「怎样加新的 CI 规则？」 | 直接编辑 resources/rules.json，追加 {"id": "...", "layer": "...", "kind": "regex", ...}，引擎实时加载、无需改代码。 |
| 「明文密钥报了，但我用的是环境变量引用 ${{ secrets.X }}，会误报吗？」 | 不会。规则只认「密钥名后直接跟 10 位以上字面值」，环境变量引用（${{ secrets.X }} 或 ${VAR}）不含字面值，不触发。 |
