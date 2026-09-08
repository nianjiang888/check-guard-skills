# 链接校验报告（check-links v2.0.0）
扫描目标：`示例目录\case_high`
判定：**高**　验证暴露指数：**80/100**　可修正：2 / 不可修正：0　发现项：2　预计避免返工工时：8

## 发现清单
| 严重度 | 规则 | 层 | 文件 | 说明 | 可修正 | 建议 |
|---|---|---|---|---|---|---|
| 高 | LINK-FILE-MISSING | fileref | page.md | 文档/资源里引用的相对文件不存在（图片、子文档、配置 include）（缺失：./missing.png） | 可修正 | 补上缺失文件或修正相对路径 |
| 高 | LINK-MALFORMED | malformed | page.md | 链接语法非法：URL 内含空格，或 www 链接缺少协议头 | 可修正 | 去掉 URL 内空格、给 www 链接补 https 协议头 |

<!-- LINK_RESULT {"verdict": "高", "exposure_index": 80, "fixable": 2, "unfixable": 0, "findings": 2, "avoid_rework_hours": 8} -->
