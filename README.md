# Vortexa Auto Keep-Alive 🚀

基于 Python Playwright 和 GitHub Actions 的 Vortexa 免费服务器自动保活脚本。
已实现全流程模拟：登录 -> 服务列表 -> 服务详情 -> 进入最终服务器面板 (Server Panel)。

## 🛠️ 配置环境变量 (Secrets)
进入 `Settings` -> `Secrets and variables` -> `Actions`，添加以下机密变量：

| 变量名 (Name) | 是否必填 | 描述说明 |
| --- | --- | --- |
| `VORTEXA_EMAIL` | **必填** | 登录邮箱 |
| `VORTEXA_PASSWORD` | **必填** | 登录密码 |
| `PROXY_URL` | *可选* | **强烈建议配置**。传入 vless://, vmess://, hy2:// 等节点链接。脚本会自动使用 Sing-box 代理访问，防封防屏蔽。 |
| `TG_BOT_TOKEN` | *可选* | Telegram Bot Token，用于接收**执行截图**。 |
| `TG_CHAT_ID` | *可选* | 接收消息的用户 ID。 |

## ✨ 更新说明
- **代理支持**：无缝对接你的 Sing-box 代理节点链接。
- **全流程截图**：执行成功或失败都会在最终页面截图，并推送到 Telegram。
- **防指纹检测**：引入 `playwright-stealth` 突破 Cloudflare 等风控验证。
