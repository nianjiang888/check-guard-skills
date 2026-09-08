# 数据 schema 校验方法论（check-schema）

本文件说明 check-schema 能判定什么、不能判定什么，以及各类规则背后的取舍。

## 一、能确定性判定的（本包范围）

1. 缺 required 数组：schema 声明了 `properties` 却没有 `required` 数组，调用方无法判断哪些字段必填，定为中级。
2. 缺 type 字段：schema 声明了 `properties` 却全程没有 `type`，字段类型完全不约束，定为中级。
3. 邮箱字段未标 format：出现 `email/mail/邮箱` 这类字段却没标 `format: email`，校验会放行进错格式，定为低级。
4. 有限值字段未标 enum：出现 `status/state/role/type/level` 这类有限值字段却没标 `enum`，取值无约束，定为低级。
5. 字段无 description：schema 声明了 `properties` 却没有任何 `description`，消费者看不懂字段含义，定为低级。
6. 已接入校验工具：命中 `jsonschema/pydantic/sqlalchemy/cerberus/dataclass/marshmallow/voluptuous/avro/protobuf` 等，定为安全变体（仅鼓励信号，不计入发现项）。

## 二、不能判定、也不假装能判定的

- 字段类型逻辑矛盾（如 type 为 integer 却给了字符串默认值）：本包不做全量类型推导，会漏报。那是 guard-schema 深度版或专业 schema 校验器的活。
- 跨字段依赖约束（如「A 与 B 至少填其一」）：本包只看单文件静态文本，不建模字段间关系。
- schema 是否「在运行时真的被校验」：那是运行时框架的事，超出静态快检。

## 三、严重度设定

- 中：缺 required、缺 type。这两类直接让下游无法正确校验必填与类型，故定为中级并建议修复。
- 低：邮箱未标 format、有限值未标 enum、字段无 description。可读性/语义约束缺口，但不如结构缺失致命。
- 安全变体：已接入专业 schema 校验工具，仅鼓励信号，不计入发现项、不影响判定。

## 四、为什么用「模式匹配」而非实时推导

实时类型推导需要接运行时或采样数据、慢、难进 CI、结果不稳定。本包只用不需语义理解的确定性模式，因此可重跑、可留证据、可进 CI，专门拦住「缺 required/type/format/enum/description」这类一眼就能揪的约束缺失。

## 五、如何扩展规则库

直接编辑 resources/rules.json，追加 `{"id": "...", "layer": "...", "kind": "regex", ...}` 即可，引擎在每次扫描时实时加载，无需改代码。
