# Vortexa Auto Keep-Alive 🚀

基于 Python Playwright 和 GitHub Actions 的 [Vortexa](https://vortexa.cloud/) 免费服务器自动保活脚本。

根据 Vortexa 的公平使用政策 (Fair Use Policy)，免费服务器要求 **“每 7 天至少有一次活跃登录或产生网络流量”**，否则节点将被挂起并在 7 天后删除。本项目通过定时自动化模拟浏览器登录控制面板，帮助你轻松完成保活任务，告别遗忘焦虑！

## ✨ 功能特点

- **完全自动化**：依托 GitHub Actions 定时执行，默认每 3 天运行一次。
- **真实浏览器模拟**：使用 Playwright 驱动 Chromium 无头浏览器，模拟真实用户的登录行为。
- **消息推送**：支持接入 Telegram Bot，每次执行结果（成功或失败异常）都会推送到你的手机。
- **安全可靠**：账号密码及 Token 均存储在 GitHub Secrets 中，不会泄露在代码里。

## 🛠️ 使用说明

### 1. Fork 本仓库
点击页面右上角的 `Fork` 按钮，将本项目复制到你自己的 GitHub 账号下。

### 2. 配置环境变量 (Secrets)
进入你 Fork 后的仓库，依次点击 `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`，添加以下机密变量：

| 变量名 (Name) | 是否必填 | 描述说明 |
| --- | --- | --- |
| `VORTEXA_EMAIL` | **必填** | 你登录 Vortexa 控制面板的注册邮箱 |
| `VORTEXA_PASSWORD` | **必填** | 你登录 Vortexa 控制面板的密码 |
| `TG_BOT_TOKEN` | *可选* | Telegram 机器人的 Token（通过 @BotFather 获取） |
| `TG_CHAT_ID` | *可选* | 接收 TG 消息的用户 ID（通过 @userinfobot 获取） |

*(注：如果不需要 Telegram 推送，可以不配置 TG 相关的变量，脚本会自动跳过推送步骤。)*

### 3. 启用 Actions 工作流
1. 点击仓库顶部的 `Actions` 标签页。
2. 可能会看到一个提示：“I understand my workflows, go ahead and enable them”，点击确认启用。
3. 在左侧菜单选择 **Vortexa Auto Keep-Alive**，点击右侧的 `Run workflow` 按钮，进行一次手动触发测试。
4. 观察运行日志，如果最后一步显示绿色打勾且输出了 `🎉 登录成功，已成功进入 Dashboard！`，则代表配置成功。

### 4. 日常运行
配置无误后，GitHub Actions 将会自动在每隔 3 天的 UTC 时间 08:00 (北京时间 16:00 左右) 自动执行，无需你再进行任何手动干预。

## ⚠️ 注意事项与进阶建议

1. **GitHub Actions 暂停机制**：如果你的仓库连续 60 天没有任何代码提交活动，GitHub 可能会自动暂停定时任务。建议每隔一两个月来看看，或者给自己发个 PR 改改标点符号。
2. **双重保活建议 (Traffic 保活)**：Vortexa 的规则是“登录 **或** 网络流量”。为了追求极致稳定，建议在你的服务器内跑一个 Web 服务，并注册一个免费的 [UptimeRobot](https://uptimerobot.com/) 账号，每 5 分钟 Ping 一次你的业务端口或隧道域名。这样既能产生实际流量，又能监控机器存活状态。

## 📝 免责声明
本项目仅供学习与自动化运维交流使用。请合理使用免费资源，遵守各大云服务商的 TOS 与 AUP。如果官方后续加入验证码或更改规则，脚本可能需要对应更新。
