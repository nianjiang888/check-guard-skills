# CHANGELOG — check-links

## v2.0.0（2026-09-02）初始版本

- check-* 系列第二个成员，定位「死链 / 坏引用检测护栏」。
- 引擎 `scripts/check.py`：scan / rules / ledger / version 四子命令，纯标准库依赖，确定性可重跑；沿用 #1 check-config 引擎骨架（_parse_argv + preflight + 退出码 0/1/2/3/4 + 可修正性维度 + 实物证据报告）。
- 9 条检查规则 + 1 条安全变体，覆盖 9 个层：import / fileref / malformed / anchor / placeholder / empty / escape / whitespace / dupanchor(safe)。
- 原创量化口径：验证暴露指数（0–100）+ 可修正性维度 + 预计避免返工工时。
- 链接专属计算检查：import/require/include 缺失（极端，构建级）、相对文件引用缺失（高）、页内锚点失效（中）、路径逃逸根（中）、重复锚点（低）；纯正则检查：URL 语法非法/www 缺协议（高）、占位域名（中）、空链接（中）、目标首尾空白（低）。
- 误报控制：仅跳过明确测试标记文件、抽取引用时跳过外链与裸域名、锚点采用 GitHub 风格 slug。
- 退出码 0/1/2/3/4（4=已拦下/极端风险），与 guard / check 系列一致。
- 诚实边界：仅静态检测、不联网探活、不修改文件、不拦截部署、不承诺 100%、价值量化为估算。
- 配套：resources×3（rules / models / domains）+ references×3 + FAQ / README / SELF_EVAL / CHANGELOG + examples×4。
