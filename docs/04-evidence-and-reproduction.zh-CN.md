# 证据索引与复现边界

## 实验覆盖

| 能力 | 实际证据 |
|---|---|
| GSA draft 与常设私有 case/PR 关联 | github-hybrid-receipts.json、hybrid-drafts.json |
| private issue 标签、comment、关闭/重开 | github-api-receipts.json |
| 两条独立普通 private PR merge | integration-api-receipts.json |
| 非 main base 的两条回补 PR | backport-heads.json |
| 真实 cherry-pick 冲突 | backport-conflicts.json |
| private Actions success | Actions run38506893672 |
| 修复前 Jenkins FAIL 与修复后 PASS | jenkins-builds.json 与 build logs |
| 真实 GitHub webhook delivery | github-hook-deliveries.json |
| HMAC 拒绝与真实状态回写 | bridge 源码、webhook-builds.github.json |
| 当前 private gate 套餐限制 | protection 请求403回执 |
| 公开 harmless gate 拦截 pending 后允许 success | public-gate-receipts.json |
| owner 自己批准 PR 被拒绝 | public-gate-receipts.json |
| private release 匿名访问失败 | release-promotion-results.json |
| GPG 正确/错误接收者、签名篡改 | manual-results.json 与对应 log |
| 两条 LTS 离线完整回归 | downstream8.5/8.1 test logs |
| 两客户变体有序重建 | customer-variant-results.json |
| private/public 核心制品同 hash | release-promotion-results.json |

## 共享实验模型

LAB-A 是合成 tenant 匹配模型，LAB-B 是合成 batch 上限模型。
两个文件/两个独立 commit；把新回归放在未修复基线上会失败。
两个模拟 LTS 的代码故意不同，用来验证真实 Git conflict 和回补动作。
这些测试说明操作和管线可用，不说明真实 TiDB 安全补丁已经通过产品测试。

## 工具与运行位置

- GitHub 主账号：YangKeao。
- Runtime computer：home-gentoo；workspace 为本轮 agent 目录。
- Jenkins：独立实例，localhost18981；[版本与 image digest](../evidence/versions.json)。
- HTTP bridge：只处理本轮实验 repo 的签名事件。
- Public/private repo 都是新建实验资源，真实组织仓库未改动。

Jenkins data、GPG test keyring 和运行记录保留在本机。
公开仓库只含脱敏记录、公开 key、脚本和截图，不含私钥/token/密码。
本轮 container 数据挂载适用于受控合成代码，不是生产 untrusted runner 配置模板。

## 脚本如何对应报告

1. `seed.py`：模型代码、两个 release base 和初始 workflow。
2. `github_cases.py`：两个 case、独立 fix PR、lifecycle 和 protection/status probes。
3. `jenkins_setup.py`：建立独立 job；`jenkins_run.py`：失败/成功真实 build。
4. `github_webhook.py`：注册真实 hook、push 触发。
5. `github_webhook_bridge.py`：GitHub-only HMAC/CI/status bridge。
6. `integrate_backport.py`：逐个 merge、两条回补和 conflict。
7. `jenkins_one.py`：精确 SHA 的独立 CI 和 status。
8. `github_hybrid.py`：两个 draft 与 ordinary private case 关联。
9. `public_gate.py`：公开 harmless required-check enforcement。
10. `manual_bundle.py`：bundle、签名、加密、负向检查、离线验证。
11. `github_release.py`：private candidate/download 和 public promotion。
12. `customer_variants.py`：共同 base + 两客户有序 patch 重建。

这些是本轮实际脚本，不是已经发布的生产自动化产品。
脚本中的仓库名和对象 ID 对应本轮保留痕迹；再次演练应替换新 repo 名/新目录，不直接重复执行建对象步骤。
CI 完成判断应绑定 SHA，case/manifest 应使用实际返回的对象 ID，不依赖全新仓库的编号推测。

## 暂停与保留

- GitHub repos、issues、PR、draft、tags、release 和 API 证据继续保留。
- Jenkins 数据和实例保留，方便同机或 SSH 转发检查。
- 临时公网 tunnel 和 webhook 自动触发在收尾暂停。
- GitHub hook 的 delivery history 仍可以检查，不把 trycloudflare URL 当成长期服务。
- 私有 GSA draft 不申请 CVE，也不 publish。

## 没有验证到的范围

1. 未操作 pingcap/tidb 的生产 Jenkins/GitHub App。
2. 没有第二个 GitHub 人类账号的 collaborator 或 team 邀请/撤销验证。
3. 没有验证 org SSO、企业审计日志、受信 runner/cache/artifact 隔离。
4. 当前个人套餐没有 private protection；公开门禁演练不能替代组织套餐验收。
5. 没有用真实漏洞、真实客户制品或真实预披露名单。
6. 没有证明上百个 hotfix 变体的性能；只验证两套有序变体的正确重建。

## 对 TiDB 最有用的下一步

常设 private 工作区、isolated CI、case/version/release manifest 应在平时准备好。
每个 case 独立，多个 case 可以一起形成一次协调发布。
支持分支收敛到产品 release lines；客户变体在可行时以基础版本和有序 patch manifest 重建。
GSA 继续作为入口和公告，不把它的临时 fork 当作多版本主集成区。

## GitHub-only 最小启动环境

以下补齐脚本所需的本地环境。再次执行时先替换新的实验仓库名；本轮保留仓库不是重置目标。
在克隆的实验脚本根目录运行，`TASK_LAB_PATH` 是任务目录变量。

```bash
TASK_LAB_PATH="$(pwd)"
mkdir -p .secrets runtime/jenkins/home runtime/jenkins/init
chmod 700 .secrets
python3 - <<'PY'
from pathlib import Path
import json,secrets
p=Path('.secrets/lab-auth.json')
p.write_text(json.dumps({
  'jenkins_admin_password': secrets.token_urlsafe(32),
  'webhook_secret': secrets.token_urlsafe(32),
}))
p.chmod(0o600)
PY
cp scripts/jenkins-init.groovy runtime/jenkins/init/00-lab.groovy

docker run -d --name sec-alt-jenkins-20261014 \
  --memory 2g --cpus 2 --user "$(id -u):$(id -g)" \
  -p 127.0.0.1:18981:8080 \
  -e JAVA_OPTS='-Djenkins.install.runSetupWizard=false -Xms128m -Xmx768m' \
  -v "$TASK_LAB_PATH/runtime/jenkins/home:/var/jenkins_home" \
  -v "$TASK_LAB_PATH/runtime/jenkins/init:/var/jenkins_home/init.groovy.d:ro" \
  -v "$TASK_LAB_PATH:/lab:ro" \
  jenkins/jenkins:lts-jdk21

docker exec --user 0 sec-alt-jenkins-20261014 sh -c \
  'apt-get update -qq && apt-get install -y -qq --no-install-recommends python3'
```

这个挂载方式是实际实验配置，只跑自己创建的受控模型代码。
它把实验目录挂入 built-in node，不应作为生产 untrusted PR runner 的隔离模板。
真实 runner 应只挂必须的源码/制品，并与 controller/bridge 凭据分离。
实验没有把用户的 GitHub token 放进 Jenkins；GitHub 身份由宿主机的现有 `gh` 授权访问。

按实验顺序执行：

```bash
python3 scripts/seed.py
python3 scripts/github_cases.py
python3 scripts/jenkins_setup.py
python3 scripts/jenkins_run.py
# 另一个受控进程启动签名事件 bridge。
python3 scripts/github_webhook_bridge.py
```

bridge 与 Jenkins 的口令是这次新生成的本地测试凭据，不是生产 Jenkins 凭据。
真实 Github webhook URL 应是团队已有的可达 HTTPS endpoint。
本轮为了验证公网事件使用临时 cloudflared tunnel：

```bash
cloudflared tunnel --url http://127.0.0.1:18989 --protocol http2 --no-autoupdate
```

初次 QUIC 连接超时，切到 HTTP/2 后实际 delivery 成功。
后续用 `github_webhook.py` 注册带 secret 的 push hook，`Recent Deliveries` 可检查服务端回执。
临时 URL 没有当成永久基础设施保留。

继续多版本、混合 case 和交付：

```bash
python3 scripts/integrate_backport.py
python3 scripts/github_hybrid.py
python3 scripts/manual_bundle.py
python3 scripts/github_release.py
python3 scripts/customer_variants.py
```

`jenkins_one.py SHA` 可以独立验证一个精确 SHA 并回写 status。
`public_gate.py` 演练的是公开的无害 policy 分支；不能代替 private repo 套餐和组织 gate 的验收。
