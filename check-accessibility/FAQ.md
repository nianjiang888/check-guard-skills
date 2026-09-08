# check-accessibility 常见问题（FAQ）

| 场景 | 话术 |
|---|---|
| 「我的 <img> 没写 alt，会报吗？」 | 会。A11Y-IMG-NO-ALT 命中 <img> 却无 alt 属性（限 html/htm/jsx/tsx/vue/svelte/md），屏幕阅读器无法传达图片内容，故定高级并建议补有意义 alt。 |
| 「<button></button> 空按钮为什么报？」 | A11Y-BTN-NO-LABEL 定为中级：按钮既无可见文字也无 aria-label，辅助技术无法识别交互目标，建议补文字或 aria-label。 |
| 「<html> 没写 lang 会怎样？」 | A11Y-NO-LANG 定为中级：浏览器/屏幕阅读器无法正确选择语言与发音，建议补 lang="zh-CN"。仅对 .html/.htm 生效。 |
| 「页面没有 <title> 也算问题？」 | 算。A11Y-NO-TITLE 定为低级：标签页与书签无标识，可访问性与 SEO 双输，建议补 <title> 描述页面主题。 |
| 「标题从 h1 直接到 h3 会怎样？」 | A11Y-HEADING-SKIP 定为低级：大纲结构断裂、导航困难，建议补齐中间层级或调整标题级别。 |
| 「和 WCAG 全量审计有什么区别？」 | WCAG 审计做对比度、键盘可达性等全量合规；check-accessibility 做快检版（模式命中即报底线硬伤），入口不同、互补不替代。 |
| 「扫描会扫到测试文件吗？」 | 文件名含 test_/example/sample 或内容带明确测试标记（fixture/测试专用示例）会被跳过，避免把示例组件报成真实缺陷。 |
| 「支持哪些文件类型？」 | HTML（.html/.htm）、组件（.jsx/.tsx/.vue/.svelte）、Markdown（.md）；img/按钮/lang/title 规则按各自扩展名限定生效。 |
| 「升级后规则变了，旧报告还作数吗？」 | 以当前版本 rules.json 为准。升级时建议按新规则重跑一次，对比 A11Y_RESULT 判定块。 |
| 「怎样加新的无障碍规则？」 | 直接编辑 resources/rules.json，追加 {"id": "...", "layer": "...", "kind": "regex", ...}，引擎实时加载、无需改代码。 |
