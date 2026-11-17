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
PROXY_SERVER = os.environ.get("PROXY_SERVER")

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
        stealth_sync(page)

        try:
            # 1. 访问并登录
            print("正在访问 Vortexa 登录页面...")
            page.goto("https://vortexa.cloud/login", timeout=60000)
            page.wait_for_load_state("networkidle")

            print("输入账号密码并登录...")
            page.locator('input[type="email"]').fill(EMAIL)
            page.locator('input[type="password"]').fill(PASSWORD)
            page.get_by_role("button", name="Sign In").click()
            
            page.wait_for_url("**/dashboard**", timeout=45000)
            print("✅ 成功进入 Dashboard")

            # 2. 跳转到所有服务列表页
            print("前往 Services 列表页面...")
            page.goto("https://vortexa.cloud/services", timeout=30000)
            page.wait_for_load_state("networkidle")

            # 3. 精准点击 Manage 按钮（过滤掉普通文本，只找 a 标签或 button 标签）
            print("点击 Manage 按钮...")
            manage_btn = page.locator('a:has-text("Manage"), button:has-text("Manage")').first
            manage_btn.wait_for(state="visible", timeout=15000)
            manage_btn.click()

            # 4. 不再傻等 URL 变化，直接等待下个页面的专属按钮出现
            print("等待进入服务详情页...")
            open_panel_btn = page.locator('a:has-text("Open Server Panel"), button:has-text("Open Server Panel")').first
            open_panel_btn.wait_for(state="visible", timeout=30000)
            
            print("点击 Open Server Panel...")
            open_panel_btn.click()
            
            # 5. 等待最终的 Console 面板出现
            print("等待加载 Console 面板...")
            console_tag = page.locator('text="CONSOLE"').first
            console_tag.wait_for(state="visible", timeout=30000)
            
            # 缓冲 5 秒，确保 CPU、内存等图表数据完整渲染完毕
            time.sleep(5) 
            print("🎉 成功进入最终服务器面板！")

            # 6. 截图保存并发送 TG
            screenshot_path = "vortexa_success.png"
            page.screenshot(path=screenshot_path, full_page=True)
            send_tg_photo("✅ Vortexa 服务器保活成功！已成功进入 Server Panel，详情见截图。", screenshot_path)

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
