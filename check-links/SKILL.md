---
name: check-links
display_name: 链接死链检查
version: 2.0.0
description: 死链与坏引用检测护栏（技术触发词：死链检测/断链检查/坏引用/链接校验/anchor 校验/相对路径校验/import 缺失/markdown 链接检查/文档链接lint；口语触发词：这个链接是不是死的/有没有打不开的引用/文档里的锚点是不是失效了/图片路径是不是丢了/import 的文件是不是没了/发布前检查链接；英文触发词：dead link check / broken reference / link validation / anchor check / dangling reference；一句话功能：在文档/代码/配置上线前静态扫缺失的 import/include 引用、缺失的相对文件、语法非法链接、失效页内锚点、占位域名与空链接，算验证暴露指数并出可修正性报告，看清死链再发布）
license: MIT
---

# check-links 是什么（人格锚：无，纯专业校验域）

check-links 是 check-* 系列的第二个成员，定位是「死链 / 坏引用检测护栏」。它不是链接监控器（那是运行时的事），也不是安全扫描器（那是 guard 的事），而是更日常的「lint」——在你把文档、代码或配置推上线之前，先替你把明显的引用坑扫一遍：import 的文件是不是没了、图片路径是不是丢了、页内锚点是不是跳空了、链接是不是指向 example.com 这种占位域名、有没有 `[]()` 这种空链接。

死链是最隐蔽也最常见的发布缺陷：本地能跑、仓库能过，一发布读者点击就 404，或 CI 构建直接挂掉。check-links 要做的，就是把这个「发布前最后一次引用复核」变成可重跑、可量化、留证据的静态检查。

## 能做什么

- 扫文档 / 代码 / 配置里的各类引用（Markdown 链接与图片、HTML 的 src/href、YAML 的 include/path/url、Python/JS 的 import/require/!include）。
- 可解析性判定：缺失的 import/include、缺失的相对文件、失效的页内锚点、逃出仓库根的引用。
- 链接卫生判定：语法非法的 URL（含空格、www 缺协议头）、占位域名、空链接、目标首尾空白、重复锚点。
- 算「验证暴露指数(0-100)」并出「可修正性」报告，退出码 4=极端级问题（构建级缺失）建议阻断发布。

## 边界（重要）

- 仅静态检测，不实际发起网络请求探活外链，因此不受网络/墙影响、可重跑、可进 CI。
- 不修改文件、不拦截部署、不感知运行时真实行为、不承诺 100% 准确。
- 与 guard 互补：check-links 做死链快检版，guard-network（外联通道）/ guard-publish（发布合规）做深度版，入口不同、互不替代。

## 怎么用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

扫描结束后会输出判定（通过/低/中/高/极端）、验证暴露指数、可修正/不可修正数量、发现项数与预计避免返工工时，并在报告末尾附上机器可读的 `LINK_RESULT {...}` 判定块，供 CI 程序化消费。

## 与其他 check 成员的关系

- check-config：校验配置项本身（必填/类型/密钥）。
- check-links（本包）：校验「引用关系」是否断裂。
- 后续 check-schema / check-api 等：分别深入数据结构与接口契约。

check-links 专注「引用能不能解析到」这一层，不做内容正确性判断。
