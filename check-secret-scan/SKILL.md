---
name: check-secret-scan
display_name: 密钥明文快检
version: 2.0.1
description: 密钥明文快检护栏（技术触发词：密钥扫描/明文密钥检测/私钥检测/secret scan/凭证泄露检查/硬编码密码/hardcoded credential/dotenv 检查；口语触发词：代码里有没有明文密码/有没有把密钥写死在配置里/私钥是不是不小心提交了/.env 文件是不是进仓库了/发布前查一下密钥泄露；英文触发词：secret scan / plaintext secret / leaked credential / hardcoded password / private key detection；一句话功能：在文档/代码/配置上线前静态扫私钥块、已知前缀明文密钥、硬编码凭证、URL 内嵌 user:pass 与被提交的 .env 文件，算验证暴露指数并出可修正性报告，看清密钥雷区再发布）
license: MIT
---

# check-secret-scan 是什么（人格锚：无，纯专业校验域）

check-secret-scan 是 check-* 系列的第四个成员，定位是「密钥明文快检护栏」。它不是密钥保险箱（那是运行时的事），也不是安全深度扫描器（那是 guard-secret 的事），而是更日常的「密钥 lint」——在你把文档、代码或配置推上线之前，先替你把最致命的明文密钥坑扫一遍：PEM 私钥块、已知前缀明文密钥（AWS/GitHub/OpenAI 等）、硬编码的 password/secret/token、塞进 URL 的 user:pass、还有被不小心提交进仓库的 .env 文件。

明文密钥是最不可逆也最容易被爬取的发布缺陷：功能正常、构建通过，可一旦私钥或真实密钥进仓库，就等于公开，即便立刻删掉历史提交仍可恢复。check-secret-scan 要做的，就是把这个「发布前最后一次密钥体检」变成可重跑、可量化、留证据的静态检查，命中明文私钥/已知前缀密钥时直接给退出码 4 建议阻断。

## 能做什么

- 扫文档 / 代码 / 配置里的明文密钥与凭证（Python/JS/Go/YAML/JSON/ENV/TOML/Markdown）。
- 泄露级判定：PEM 私钥块、已知前缀明文密钥（AKIA/ghp_/sk-/AIza/glpat- 等）。
- 可读级判定：password/secret/token/api_key 被硬编码为字面值、URL 内嵌 user:pass。
- 风险信号：被提交进仓库的 .env 文件（里面通常装真实凭证）。
- 算「验证暴露指数(0-100)」并出「可修正性」报告，退出码 0/1/2/3/4（4=发现明文私钥/已知前缀密钥，建议阻断发布）。

## 边界（重要）

- 仅静态检测，不做全量熵分析，故无法发现「无前缀的高熵随机密钥」；那是深度版或专业密钥扫描器的范围。
- 不修改文件、不拦截部署、不感知运行时真实调用、不承诺 100% 准确；是否阻断由 CI 策略决定。
- 与 guard-secret 互补：check-secret-scan 做密钥快检版，guard-secret 做安全深度版，入口不同、互不替代。

## 怎么用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

扫描结束后会输出判定（通过/低/中/高/极端）、验证暴露指数、可修正/不可修正数量、发现项数与预计避免返工工时，并在报告末尾附上机器可读的 `SECRET_RESULT {...}` 判定块，供 CI 程序化消费。

## 与其他 check 成员的关系

- check-config：校验配置项本身（必填/类型/密钥明文属其子集，但只查「明文」形态）。
- check-links：校验「引用关系」是否断裂。
- check-spelling：校验「文字与排版」是否干净。
- check-secret-scan（本包）：校验「明文密钥/凭证」是否泄露。
- 后续 check-schema / check-api 等：分别深入数据结构与接口契约。

check-secret-scan 专注「秘密有没有被写死/泄露」这一层，不做内容正确性判断。
