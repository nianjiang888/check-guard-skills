# 熔断器模式与令牌桶：为什么付费调用必须有护栏

## 1. 熔断器模式（Circuit Breaker）

2007 年，Michael Nygard 在《Release It!》里把电力系统里的「熔断器」概念搬进了软件架构 [Nygard 2007]。核心思想：当某个依赖（这里就是付费 API）出错率或开销超过阈值，系统应当**自动断开**——在接下来一段时间里不再调用它，避免每一次请求都变成一次失败+一次烧钱，最终拖垮整体（雪崩）。

熔断器有三个状态：

- **闭合（Closed）**：正常调用；同时统计失败率。
- **打开（Open）**：失败率超阈值，直接拒绝调用，快速失败（fail fast），不再花冤枉钱。
- **半开（Half-Open）**：冷却期后放少量请求试探；成功了回到闭合，还失败就继续打开。

落到「无护栏的付费调用」上：没有熔断的代码，等于把电闸拆了——一次异常就会让循环/重试无限地把请求砸向服务商，账单跟着指数上涨。本包在静态层面提示「缺熔断」，逼你在上线前把闸装上。

## 2. 令牌桶（Token Bucket）

令牌桶是网络流量整形的经典算法（源自 Turner 1986 等的流量合同思想）。以固定速率往桶里放令牌，每次请求消耗一枚；桶空了就限流。它把「无限调用」硬生生变成「有限配额」。

对本包的意义：限速/配额缺失是成本雷区最常见的根因之一。一个没配 `RateLimiter`、没 `time.sleep`、没 `semaphore` 的付费调用，在流量一上来时花费就失控。所以本包把「无限速」单独列为中危提示，和「无熔断」并列。

## 3. 二者如何配合

- 令牌桶管「**速率**」：每秒/每分最多调多少次。
- 熔断器管「**异常**」：失败多了就整体断开。
- 预算上限管「**总量**」：累计到 X 元就停。

三者是不同维度但互补的护栏。代码里三者都缺，就是最危险的「裸调付费 API」。

## 4. 引用

- Nygard M. (2007). *Release It! Design and Deploy Production-Ready Software*. Pragmatic Bookshelf. 第 5 章 Circuit Breaker。
- Turner J.S. (1986). *New Directions in Communications (or Which Way to the Information Age?)*. IEEE Communications Magazine. 令牌桶流量整形。
- Google SRE Book (2016). *Site Reliability Engineering*. 章节：Handling Overload（限流与熔断的工程实践）。
