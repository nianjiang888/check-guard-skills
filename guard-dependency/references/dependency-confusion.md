# 依赖投毒的四类典型手法

依赖投毒不是玄学，它有清晰的攻击模式。本工具的规则正是围绕这四类高频手法设计的。

## 一、依赖混淆（Dependency Confusion）

2021 年安全研究者 Birsan 公开演示：很多企业内部的包使用 `corp-utils`、`@internal/foo` 这类命名，并配置包管理器「公开源优先 + 私有源兜底」。攻击者在公共 registry 上抢注同名、但版本号更高的包。包管理器按版本号优先解析，于是默默拉取了攻击者的代码。

特征就是「内部命名 + 公开源」的错配。本工具用 DEP-CONFUSION 检测 `internal-*`/`private-*`/`corp-*`/`@corp/*` 这类命名出现在清单里。

**防御**：内部包走独立私有 registry 并做 namespace 隔离，确保公共源上无法注册同名高版本包；项目级禁止同名公开包可被解析。

## 二、Typosquatting（拼写抢注）

攻击者抢注热门包的常见错拼：`requets`（requests）、`flaskk`（flask）、`numpyy`（numpy）、`djago`（django）。只要开发者打错一个字母，就装进了恶意包。

本工具 DEP-TYPOSQUAT 维护一份常见错拼清单做启发式检测。

**防御**：CI 中加包名拼写核对；用 lockfile 固定精确版本；依赖统一从受信代理源拉取（代理源只镜像白名单包）。

## 三、安装钩子执行任意代码

`postinstall`/`preinstall` 这类生命周期脚本，在包被安装时自动执行。历史上多个真实投毒事件（如 event-stream 后门）正是借安装钩子落地恶意代码：包一装，作者的 `curl | sh`、`node -e`、PowerShell 就跑了。

本工具 DEP-INSTALL-SCRIPT 检测安装钩子里出现管道、curl、wget、node -e、eval、powershell 等危险原语。

**防御**：生产安装用 `npm ci --ignore-scripts`（或等价参数）禁用自动脚本；确需脚本的包，人工审计后再开白名单。

## 四、幽灵依赖与已知投毒版本

- **幽灵依赖（ghost dependency）**：代码里 `import` 了某包，但清单没声明，靠传递依赖或误装「恰好存在」。一旦底层调整，构建就炸；也可能悄悄引入不受控的包。本工具提示人工核对未声明引用。
- **已知事故版本**：event-stream 3.3.6（后门）、colors 1.4.44（抗议软件）、faker 6.6.6（自毁）、left-pad 0.0.3（删包事故）、coa/rc/ua-parser-js 投毒版本。本工具 DEP-EOL-KNOWN 直接命中这些公开事故版本。

## 五、小结

四类手法里，前三类（混淆/抢注/钩子）是「主动投毒」，第四类是「历史事故复用」。本工具不替你删包、不替你拦安装，而是把这几类风险在合入前摊开，让人在「升级 / 替换 / 加锁 / 换源 / 关脚本」之间做出有依据的决定。
