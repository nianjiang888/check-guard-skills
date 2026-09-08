# guard-secret 端到端走查示例

本示例用一个"看起来普通、实则埋了密钥"的代码仓库，演示 guard-secret 怎么把它揪出来。

## 第一步：准备一个被测仓库

假设一个项目 `my-app`，目录结构：

```
my-app/
├── config.py            # 配置文件
├── utils.py             # 工具函数
└── tests/fixtures.py    # 测试夹具
```

`config.py` 里藏着两处危险：

```python
# config.py
DB_PASSWORD = "ProdPassw0rd!"                       # SEC-PWD-01 硬编码密码
AWS_KEY = "AKIA1A2B3C4D5E6F7G8H"                   # SEC-AWS-01 AWS 访问密钥 ID
print("debug token = bearer abc123def456ghi789")    # SEC-TOK-01 Bearer 令牌
```

`tests/fixtures.py` 里放了测试用的假值（应被白名单放过）：

```python
# tests/fixtures.py
TEST_API_KEY = "your-api-key-here"                 # 白名单：your-*-here，不报
```

`utils.py` 是一段普通代码（无密钥）。

## 第二步：跑扫描

```bash
python scripts/guard.py scan my-app
```

## 第三步：看到的报告（节选）

```markdown
# guard-secret 密钥泄露扫描报告

- 扫描时间：2026-09-01 21:30
- 目标目录：/tmp/my-app
- 引擎版本：2.0.0

## 一、判定
- **风险等级：高**
- **密钥暴露面指数：120 / 100**（封顶）
- **处置建议：拦下，人工确认后决定；疑似泄露凭据必须轮换**

## 二、命中汇总（3 处）
- 按严重度：极端 0 / 高 3 / 中 0 / 低 0
- 按类型：数据库密码 1、云凭据 1、令牌 1

## 三、命中清单
| 严重度 | 置信度 | 类型 | 规则 | 文件:行 | 片段 |
|---|---|---|---|---|---|
| 高 | 高 | 数据库密码 | 硬编码密码赋值(SEC-PWD-01) | config.py:2 | DB_PASSWORD = "ProdPassw0rd!" |
| 高 | 高 | 云凭据 | AWS 访问密钥 ID(SEC-AWS-01) | config.py:3 | AWS_KEY = "AKIA1A2B3C4D5E6F7G8H" |
| 高 | 高 | 令牌 | Bearer / JWT 令牌(SEC-TOK-01) | config.py:4 | ...bearer abc123def456ghi789 |

## 四、疑似已泄露凭据（必须轮换）
- [高] AWS 访问密钥 ID @ config.py:3
- [高] 硬编码密码赋值 @ config.py:2
> **关键纠正**：Git 里「删掉那一行」没用——历史记录里凭据仍在。正确动作是立即轮换凭据。
```

命令以**退出码 4（已拦截）**结束——agent 编排看到 4 就知道：停下，别提交，向用户报告。注意 `tests/fixtures.py` 里的 `your-api-key-here` 被正确放过，没有误报。

## 第四步：对照"干净仓库"

同一个引擎扫一个只有普通代码、无密钥、无高熵串的仓库，会得到：

```
风险等级：低
密钥暴露面指数：0 / 100
退出码：0
```

## 第五步：累积价值账本

多次扫描后，跑 `python scripts/guard.py ledger .`，把每份 `secret_report.md` 聚合成 `guard-ledger.md`：

```markdown
## 价值量化
- 累计拦下估算避免损失：约 4 小时凭据轮换与事故响应
- 累计需轮换凭据：3 条
```

这就是 guard 系列反复强调的"把没发生的泄露事故变成可感知数字"——安全工具唯一能证明自己有用的方式。
