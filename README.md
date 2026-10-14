# 基于 GitHub 的保密修复与发布实验

2026-10-14。只讨论 GitHub 主平台，不涉及迁移到 GitLab。

本仓库保留三种方法的实际操作、中文体验报告、API 回执、脚本、截图和模拟发布物。
实验用 LAB-A / LAB-B 两个合成案例、两条模拟 LTS 和两套模拟客户变体。
没有真实产品漏洞，没有申请 CVE，没有发布 GSA advisory。
公开 Release 明确标为 SYNTHETIC，仅用于制品 promotion 演练。

## 三种方法

| 方法 | 实验报告 | 主要适用场景 |
|---|---|---|
| GSA 管报告和公告，常设 private repo 管代码和 CI | [混合流程](docs/01-hybrid-gsa-private.zh-CN.md) | 保留 GitHub 原生外部报告、GHSA 和后续 CVE 入口，同时解决 CI/多版本限制 |
| 独立 private embargo repo 管 case/PR/CI/release | [私有工作区](docs/02-private-embargo-repo.zh-CN.md) | 多漏洞、多组件、多 release line 集成；入口由邮件、GSA 或 PSIRT 转接 |
| GitHub 私有 RC 加签名/加密 Git 包和 patch manifest | [手动交付](docs/03-private-rc-manual-delivery.zh-CN.md) | 少量受控下游预验证，客户补丁变体重建，披露日按同一批制品公开 |

三者可组合，不必选一个承载全部职责。
推荐结构：GSA/case 各自独立；代码和 CI 共用常设私有工作区；发布按协调日期组成 release bundle。

## 实际保留的地址

- [常设私有工作区](https://github.com/YangKeao/security-embargo-private-lab-20261014)：需要有权限的 GitHub 身份。
- [LAB-A 私有修复 PR #2](https://github.com/YangKeao/security-embargo-private-lab-20261014/pull/2)：已逐 PR 合并。
- [LAB-B 私有修复 PR #4](https://github.com/YangKeao/security-embargo-private-lab-20261014/pull/4)：已逐 PR 合并。
- [8.5 回补 PR #6](https://github.com/YangKeao/security-embargo-private-lab-20261014/pull/6)：保留 open，CI 通过。
- [8.1 回补 PR #7](https://github.com/YangKeao/security-embargo-private-lab-20261014/pull/7)：保留 open，CI 通过；实际发生并解决 cherry-pick 冲突。
- [GSA draft A](https://github.com/YangKeao/security-alternatives-public-lab-20261014/security/advisories/GHSA-pjwp-c2g7-4xhc)：仍是 draft。
- [GSA draft B](https://github.com/YangKeao/security-alternatives-public-lab-20261014/security/advisories/GHSA-2652-9xcx-9vg4)：仍是 draft。
- [私有 RC](https://github.com/YangKeao/security-embargo-private-lab-20261014/releases/tag/lab-private-rc1)：匿名下载失败。
- [公开模拟 promotion](https://github.com/YangKeao/security-alternatives-public-lab-20261014/releases/tag/lab-public-rc1-8.5)：保留同一批演示制品。
- [公开无害分支上的门禁验证 PR](https://github.com/YangKeao/security-alternatives-public-lab-20261014/pull/1)：pending 时合并失败，真实 Jenkins 成功后合并。
- [私有 Actions 实际成功运行](https://github.com/YangKeao/security-embargo-private-lab-20261014/actions/runs/38506893672)。

## 关键结论

1. 普通 private repo 能用 PR、非 main base、独立 merge、Actions、webhook 和 commit status。
2. 实际跑通 GitHub push → 签名 webhook → 独立 Jenkins → GitHub status。
3. 当前个人账号的 private repo 分支保护 API 返回 403，要求 GitHub Pro。
4. 这不等于平台没有门禁：公开演示分支已实测强制门禁，包括管理员。
5. GitHub 文档规定私有门禁要匹配 Pro/Team/Enterprise 等相应套餐。
6. 不应把“CI 能跑”当成“合并被强制拦截”。
7. 本次用独立 Jenkins 2.580.1；没有改动 TiDB 生产 Jenkins。
8. 对 TiDB 现有 CI，还要验证 App 授权、触发白名单、私有 repo checkout 和 runner/log/cache 隔离。

## 证据与复现

- [证据索引](docs/04-evidence-and-reproduction.zh-CN.md)。
- `evidence/`：脱敏 API 回执、build 结果、冲突记录、签名与 hash 校验。
- `scripts/`：本轮实际使用的 GitHub/CI/交付脚本。
- `screenshots/`：真实浏览器截图，没有用 API 文本伪造私有 UI。
- [既有 GSA 全流程报告](https://github.com/YangKeao/gsa-ci-integration-lab-20261012)。

实验 webhook 和临时 tunnel 在收尾时暂停；GitHub 对象、Jenkins 数据和本地实验目录继续保留。
私有页面没有安全可复用的 GitHub 浏览器登录态，因此用 CLI/API 回执和准确点击路径补齐。
