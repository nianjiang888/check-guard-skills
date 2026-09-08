# CHANGELOG — check-config

## v2.0.0（2026-09-02）初始版本

- 首个 check-* 系列成员，定位「配置与参数校验护栏」。
- 引擎 `scripts/check.py`：scan / rules / ledger / version 四子命令，纯标准库依赖，确定性可重跑。
- 9 条检查规则 + 1 条安全变体，覆盖 9 个层：required / type / value / deprecated / secret / env / path / protocol / schema(safe)。
- 原创量化口径：验证暴露指数（0–100）+ 可修正性维度 + 预计避免返工工时。
- 退出码 0/1/2/3/4（4=已拦下/极端风险），与 guard 系列一致。
- 误报控制：示例/测试白名单 + 明文密钥占位符排除 + 复合规则（缺鉴权/生产开 debug 需多条件同时命中）。
- 配套：resources×3（rules / models / domains）+ references×3 + FAQ / README / SELF_EVAL / CHANGELOG + examples×4。
- 诚实边界：仅静态检测，不修改文件、不拦截部署、不承诺 100%、价值量化为估算。
