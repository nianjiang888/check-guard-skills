# check-script-health 短视频脚本体检评分

在短视频脚本开拍或发布前静态体检七维度，算「完播健康指数(0-100)」并出逐条可修正建议。

## 快速开始

```
python scripts/check.py scan 你的脚本.md
python scripts/check.py scan 脚本目录/ 报告.md
python scripts/check.py rules          # 列出 19 条规则
python scripts/check.py ledger 脚本.md # 机器可读 JSON
```

依赖：Python 3.8+，纯标准库，无需安装任何第三方包。

## 七维度

开头钩子(hook) / 完播留人(retention) / 信息密度(density) / 互动引导(cta) / 合规安全(compliance) / 情绪共鸣(emotion) / 口语表达(spoken)

任一合规红线（极限词、疗效承诺、私域引流、收益夸大）命中即判「红线」，健康指数强制压到 40 以下。

## 退出码

0 干净 · 1 有命中 · 2 IO 错误 · 3 命令错误 · 4 合规红线

详见 SKILL.md 与 references/methodology.md。
