import os
import time
import requests
from playwright.sync_api import sync_playwright

# 从环境变量获取配置
EMAIL = os.environ.get("VORTEXA_EMAIL")
PASSWORD = os.environ.get("VORTEXA_PASSWORD")
TG_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

def send_tg_msg(text):
    """发送 Telegram 通知"""
    if TG_TOKEN and TG_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TG_CHAT_ID, "text": text}, timeout=10)
        except Exception as e:
            print(f"Telegram 推送失败: {e}")

def main():
    if not EMAIL or not PASSWORD:
        print("未检测到账号或密码环境变量，请在 GitHub Secrets 中配置！")
        return

    with sync_playwright() as p:
        # 启动无头浏览器
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("正在访问 Vortexa 登录页面...")
            page.goto("https://vortexa.cloud/login", timeout=60000)
            page.wait_for_load_state("networkidle")

            print("定位输入框并输入账号密码...")
            page.locator('input[type="email"]').fill(EMAIL)
            page.locator('input[type="password"]').fill(PASSWORD)
            
            print("点击登录按钮...")
            page.locator('button:has-text("Sign In")').click()
            
            # 等待 URL 发生跳转至 dashboard，或等待页面出现特定元素
            page.wait_for_url("**/dashboard**", timeout=30000)
            print("🎉 登录成功，已成功进入 Dashboard！")
            
            send_tg_msg("✅ Vortexa 服务器自动登录保活成功！")
            
        except Exception as e:
            error_msg = f"❌ Vortexa 保活登录失败：\n{str(e)}"
            print(error_msg)
            send_tg_msg(error_msg)
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    main()
