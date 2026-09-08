---
name: check-ci
display_name: CI 流水线检查
version: 2.0.0
description: CI 配置护栏（技术触发词：CI 配置校验/流水线校验/工作流检查/CI 安全校验/yaml lint；口语触发词：我的 CI 配得对不对/流水线有没有明文字密钥/任务会不会卡死没超时/权限是不是给太大/工作流会不会根本不触发；英文触发词：CI config check / pipeline lint / plaintext secret in CI / CI timeout missing / workflow no trigger；一句话功能：在 CI/流水线 YAML 上线前静态扫任务无超时、明文密钥、过宽权限、无触发条件，算验证暴露指数并出可修正性报告，看清流水线雷区再发布）
license: MIT
---

# check-ci 是什么（人格锚：无，纯专业校验域）

check-ci 是 check-* 系列的「CI/流水线配置护栏」。它不是流水线运行时调试器（那是跑起来看日志），也不是 secret 扫描器（那是 check-secret-scan 的活），而是更日常的「CI lint」——在你把 CI 配置推上线之前，先替你把最常见、最容易被看漏的流水线坑扫一遍：任务没设超时（卡死拖垮 runner）、配置里明文写了密钥、授予了过宽权限、工作流根本没有任何触发条件（实际上永远不跑）。

文档/页面/锁文件「看起来没问题」往往只是没被认真扫过。这些缺陷不会让构建失败，却会在发布后被人点开死链、被视障用户卡住、被供应链投毒、被卡死的流水线拖垮。check-ci 要做的，就是把这道「发布前最后一次体检」变成可重跑、可量化、留证据的静态检查。

## 能做什么

- 扫 CI/流水线 YAML（GitHub Actions / GitLab CI / 通用 YAML 等任意文本）。
- 安全级判定：明文写了密码/令牌/密钥字面值（高）、授予过宽权限 write-all/contents: write（中）。
- 结构级判定：任务未设超时（中，限 yml/yaml）、工作流无触发条件（高，限 yml/yaml）。
- 鼓励信号：已接入 CI 校验流程（pipeline lint/ci-check/流水线校验），仅正向标记。
- 算「验证暴露指数(0-100)」并出「可修正性」报告，退出码 0/1/2/3/4。

## 边界（重要）

- 仅静态检测，不连密钥库、不真跑流水线，故无法发现「密钥引用其实指向保险库」「超时设了但值过大」这类需要上下文才能判定的问题。
- 不修改文件、不拦截部署、不感知真实执行、不承诺 100% 准确；是否阻断由 CI 策略决定。
- 与 check-secret-scan 互补：check-secret-scan 做全仓库明文密钥扫描，check-ci 聚焦 CI 配置里的高危明文凭据与权限/触发结构。

## 怎么用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

扫描结束后会输出判定（通过/低/中/高/极端）、验证暴露指数、可修正/不可修正数量、发现项数与预计避免返工工时，并在报告末尾附上机器可读的 `CI_RESULT {...}` 判定块，供 CI 程序化消费。

## 与其他 check 成员的关系

- check-config：校验配置项本身。
- check-links：校验「引用关系」是否断裂。
- check-spelling：校验「文字与排版」是否干净。
- check-secret-scan：校验「明文密钥/凭证」是否泄露（全仓库）。
- check-schema：校验「数据 schema 字段约束」是否缺失。
- check-docs：校验「文档与代码一致性」。
- check-lockfile：校验「依赖锁定完整性」。
- check-accessibility：校验「可访问性基线」。
- check-ci（本包）：校验「CI/流水线配置」——无超时、明文密钥、过宽权限、无触发条件。

check-ci 专注「流水线配置是不是安全、是不是真会跑」这一层，与 check-secret-scan 错位互补。
