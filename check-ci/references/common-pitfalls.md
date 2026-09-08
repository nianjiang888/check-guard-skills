# 常见误报与边界（check-ci）

本文件列出发包前已知、且已做规避处理的几类边界，便于使用者理解「为什么有时没报、为什么有时报了但可关」。

1. 明文密钥的边界：CI-SECRET-PLAIN 只认「密钥名后直接跟 10 位以上字面值」，环境变量引用（${{ secrets.X }} / ${VAR}）不含字面值，不触发。但仍是高危入口，建议一律走密钥管理器。
2. 过宽权限的边界：CI-PERMISSIONS-WIDE 命中 write-all 或 contents: write。若你确需在某个 job 内写内容且已隔离风险，可收窄规则或仅在该 job 授权。
3. 无超时的边界：CI-NO-TIMEOUT 用「有 jobs 却无 timeout 字样」判定（限 yml/yaml）。若用非标准超时写法（如自定义 step 超时），可能误报，可在 rules.json 里调整关键词。
4. 无触发条件的边界：CI-NO-TRIGGER 用「有 name/jobs 却无 on/push/pull_request/schedule/workflow_dispatch」复合判定。若你的工作流靠 reusable workflow 被调用（本身无需 on），属误报高发区，可手动关该规则。
5. 已接入 CI 校验的边界：CI-CLEAN 仅做鼓励信号，不计入发现项、不提升判定等级；它存在的意义是「你已经做了该做的，给予正向标记」。
6. 测试 / 示例文件：文件名含 test_/example/sample，或内容带明确测试标记（fixture/测试专用示例）会被跳过。真实流水线即使正文出现 example 等词也不跳过，宁可在示例上多扫，也不在真实流水线上漏报。
7. 合规红线：本包所有源文件与压缩包均不含明文协议头、真实地址、绝对路径、BOM 与 CRLF，可安全上架分发。
