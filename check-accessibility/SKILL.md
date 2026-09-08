---
name: check-accessibility
display_name: 可访问性护栏（a11y lint）
version: 2.0.1
description: 可访问性护栏（技术触发词：可访问性校验/无障碍检查/a11y lint/alt 属性检查/按钮标签检查；口语触发词：我的页面无障碍过关没/img 有没有加 alt/按钮没文字能被读吗/html 有没有 lang/标题层级跳了/视障用户能不能用；英文触发词：accessibility check / a11y lint / missing alt / button no label / no lang attribute；一句话功能：在 HTML/组件/Markdown 上线前静态扫 img 缺 alt、button 无标签、html 缺 lang/title、标题层级跳跃等无障碍坑，算验证暴露指数并出可修正性报告，看清可访问性雷区再发布）
license: MIT
---

# check-accessibility 是什么（人格锚：无，纯专业校验域）

check-accessibility 是 check-* 系列的「可访问性基线护栏」。它不是屏幕阅读器仿真（那是运行时的事），也不是全量 WCAG 审计（那是专业无障碍咨询），而是更日常的「a11y lint」——在你把页面、组件或文档推上线之前，先替你把最常见、最容易被看漏的无障碍硬伤扫一遍：图片没写 alt、按钮既无文字也无 aria-label、html 没标 lang、页面没 title、标题层级从 h1 直接跳到 h3。

文档/页面/锁文件「看起来没问题」往往只是没被认真扫过。这些缺陷不会让构建失败，却会在发布后被人点开死链、被视障用户卡住、被供应链投毒、被卡死的流水线拖垮。check-accessibility 要做的，就是把这道「发布前最后一次体检」变成可重跑、可量化、留证据的静态检查。

## 能做什么

- 扫 HTML / 组件（jsx/tsx/vue/svelte）/ Markdown 里的无障碍基线问题。
- 语义级判定：<img> 缺 alt（高，限 html/htm/jsx/tsx/vue/svelte/md）、<button> 无标签（中，限组件类）、<html> 缺 lang（中）、无 <title>（低）。
- 结构级判定：标题层级跳跃超过一级（低，限 md/html/htm）。
- 鼓励信号：已接入可访问性基线（a11y/accessibility/无障碍），仅正向标记。
- 算「验证暴露指数(0-100)」并出「可修正性」报告，退出码 0/1/2/3/4。

## 边界（重要）

- 仅静态检测，不跑屏幕阅读器、不做颜色对比度计算，故无法发现「对比度不足」「键盘焦点陷阱」这类需要渲染或交互才能判定的问题。
- 不修改文件、不拦截部署、不感知真实渲染、不承诺 100% 准确；是否阻断由 CI 策略决定。
- 与专业 WCAG 审计互补：check-accessibility 做快检版（模式命中即报硬伤），深度审计做全量合规。

## 怎么用

```
python scripts/check.py scan <目录或文件> [报告输出路径]
python scripts/check.py rules
python scripts/check.py ledger <目录>
python scripts/check.py version
```

扫描结束后会输出判定（通过/低/中/高/极端）、验证暴露指数、可修正/不可修正数量、发现项数与预计避免返工工时，并在报告末尾附上机器可读的 `A11Y_RESULT {...}` 判定块，供 CI 程序化消费。

## 与其他 check 成员的关系

- check-config：校验配置项本身。
- check-links：校验「引用关系」是否断裂。
- check-spelling：校验「文字与排版」是否干净。
- check-secret-scan：校验「明文密钥/凭证」是否泄露。
- check-schema：校验「数据 schema 字段约束」是否缺失。
- check-docs：校验「文档与代码一致性」。
- check-lockfile：校验「依赖锁定完整性」。
- check-accessibility（本包）：校验「可访问性基线」——img 缺 alt、按钮无标签、html 缺 lang/title、标题层级跳跃。
- 后续 check-ci：深入 CI 配置。

check-accessibility 专注「页面/组件无障碍的底线硬伤」这一层。
