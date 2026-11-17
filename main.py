import os
import time
import requests
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# 获取环境变量
EMAIL = os.environ.get("VORTEXA_EMAIL")
PASSWORD = os.environ.get("VORTEXA_PASSWORD")
TG_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")
PROXY_SERVER = os.environ.get("PROXY_SERVER") # 例如: socks5://127.0.0.1:2080

def send_tg_photo(text, photo_path=None):
    """发送 Telegram 图文消息"""
    if TG_TOKEN and TG_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
            payload = {"chat_id": TG_CHAT_ID, "caption": text}
            if photo_path and os.path.exists(photo_path):
                with open(photo_path, 'rb') as photo:
                    requests.post(url, data=payload, files={"photo": photo}, timeout=20)
            else:
                # 如果没有图片，降级发送纯文本
                text_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
                requests.post(text_url, json={"chat_id": TG_CHAT_ID, "text": text}, timeout=10)
        except Exception as e:
            print(f"Telegram 推送失败: {e}")

def main():
    if not EMAIL or not PASSWORD:
        print("未检测到账号密码配置！")
        return

    launch_args = [
        '--no-sandbox', 
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled'
    ]
    
    launch_opts = {"headless": True, "args": launch_args}
    if PROXY_SERVER:
        print(f"🚀 启用代理服务器: {PROXY_SERVER}")
        launch_opts["proxy"] = {"server": PROXY_SERVER}

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_opts)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page) # 应用 stealth 隐藏无头浏览器特征

        try:
            # 1. 访问登录页
            print("正在访问 Vortexa 登录页面...")
            page.goto("https://vortexa.cloud/login", timeout=60000)
            page.wait_for_load_state("networkidle")

            # 2. 填写表单并登录
            print("输入账号密码并登录...")
            page.locator('input[type="email"]').fill(EMAIL)
            page.locator('input[type="password"]').fill(PASSWORD)
            page.get_by_role("button", name="Sign In").click()
            
            # 等待跳转到 Dashboard
            page.wait_for_url("**/dashboard**", timeout=45000)
            print("✅ 成功进入 Dashboard")

            # 3. 跳转到所有服务列表页 (Services)
            print("前往 Services 列表页面...")
            page.goto("https://vortexa.cloud/services", timeout=30000)
            page.wait_for_load_state("networkidle")

            # 4. 点击 Manage 进入服务详情页
            print("点击 Manage 按钮...")
            page.get_by_text("Manage").first.click()
            page.wait_for_url("**/services/*", timeout=30000)

            # 5. 点击 Open Server Panel 进入最终服务器控制台
            print("点击 Open Server Panel...")
            page.get_by_text("Open Server Panel").first.click()
            page.wait_for_url("**/server/*", timeout=30000)
            
            # 稍作等待，确保 Console 面板及数据完全渲染
            time.sleep(5) 
            page.wait_for_selector('text="CONSOLE"', timeout=15000)
            print("🎉 成功进入最终服务器面板！")

            # 6. 截图保存
            screenshot_path = "vortexa_success.png"
            page.screenshot(path=screenshot_path, full_page=True)

            send_tg_photo("✅ Vortexa 服务器保活成功！已成功登录并进入最终 Server Panel，详情见截图。", screenshot_path)

        except Exception as e:
            error_screenshot = "error.png"
            page.screenshot(path=error_screenshot, full_page=True)
            error_msg = f"❌ Vortexa 保活执行失败：\n{str(e)}"
            print(error_msg)
            send_tg_photo(error_msg, error_screenshot)
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    main()
