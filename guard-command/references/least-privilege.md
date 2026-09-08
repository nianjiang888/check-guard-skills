# 最小权限与能力安全：理论底座

## 一、最小权限原则（Saltzer & Schroeder 1975）

每个主体只应拥有完成工作所必需的最小权限。这是操作系统安全的基石之一。

- `sudo su` / `sudo -i` 拿到常驻 root，把「按需的最小权限」变成「全局最高权限」——后续每条命令都在无约束下运行，违反最小权限。
- `chmod 777` 把对象开放给所有人写，等于撤销了原本精细的访问控制。
- `chmod 000` 反过来把属主也锁死，是「过度降权导致运维事故」的另一面。

> 引用：Saltzer & Schroeder, *The Protection of Information in Computer Systems* (1975).

## 二、能力安全（Dennis & Van Horn 1966）

权限应作为**可撤销、可限定**的「能力（capability）」授予，而非依靠一个全局 root 身份。

危险命令的本质，是把一个几乎不可撤销的全局能力一次性放出：

- `rm -rf /` 放出「删除整机文件系统」的能力。
- `dd of=/dev/sda` 放出「覆写整块磁盘」的能力。
- `:(){ :|:& };:` 放出「无限派生进程」的能力。

这些能力一旦行使，没有「撤销」按钮。能力安全的应对是：把能力拆小、加确认、加干跑（dry-run），让放出之前先看见后果。

> 引用：Dennis & Van Horn, *Programming Semantics for Multiprogrammed Computations* (1966).

## 三、与本引擎的映射

| 理论要点 | 本引擎规则 |
|----------|-----------|
| 最小权限 | `CMD-SUDO-SU`（提权）、`CMD-CHMOD-777`/`CMD-CHMOD-000`（权限越界） |
| 能力不可撤销 | `CMD-RM-RF`/`CMD-DD-DISK`/`CMD-MKFS`/`CMD-DEV-REDIRECT`/`CMD-FORKBOMB`（不可回滚，定极端） |
| 先确认/干跑 | `CMD-SAFE-DRYRUN`（鼓励信号，不当命中） |

## 四、落地要点

1. 脚本里尽量用 `rm -n` / `--dry-run` 先看会动什么。
2. 删除/格式化前先列清单或移到回收站，而非直接执行。
3. 提权针对单条命令（`sudo <cmd>`），避免常驻 root shell。
4. 网络脚本先下载审读，再用签名校验的渠道执行。
