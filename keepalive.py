import os
import re
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
            print(f"Telegram 推送失败: {e}", flush=True)

def main():
    if not EMAIL or not PASSWORD:
        print("未检测到账号密码配置！", flush=True)
        return

    launch_args = [
        '--no-sandbox', 
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled'
    ]
    
    launch_opts = {"headless": True, "args": launch_args}
    if PROXY_SERVER:
        print(f"🚀 启用代理服务器: {PROXY_SERVER}", flush=True)
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
            print("正在访问 Vortexa 登录页面...", flush=True)
            page.goto("https://vortexa.cloud/login", wait_until="domcontentloaded", timeout=60000)

            print("输入账号密码并登录...", flush=True)
            page.locator('input[type="email"]').Wait_for(state="visible", timeout=30000) if hasattr(page.locator('input[type="email"]'), 'Wait_for') else page.locator('input[type="email"]').wait_for(state="visible", timeout=30000)
            page.locator('input[type="email"]').fill(EMAIL)
            page.locator('input[type="password"]').fill(PASSWORD)
            page.get_by_role("button", name="Sign In").click()
            
            page.wait_for_url("**/dashboard**", timeout=45000)
            print(f"✅ 成功进入 Dashboard (URL: {page.url})", flush=True)

            # 2. 跳转到所有服务列表页
            print("前往 Services 列表页面...", flush=True)
            page.goto("https://vortexa.cloud/services", wait_until="domcontentloaded", timeout=30000)

            # 3. 点击 Manage 按钮进入服务详情页
            print("点击 Manage 按钮...", flush=True)
            manage_btn = page.locator('a:has-text("Manage"), button:has-text("Manage")').first
            manage_btn.wait_for(state="visible", timeout=20000)
            manage_btn.click()

            # 等待进入 /services/xxxx 页面
            page.wait_for_url("**/services/**", timeout=30000)
            current_url = page.url
            print(f"✅ 已进入服务详情页: {current_url}", flush=True)

            # 4. 提取服务 ID 直接进入 Server Panel（最稳妥，且指定 domcontentloaded 避免被 WebSocket 卡死）
            match = re.search(r'/services/(\d+)', current_url)
            if match:
                service_id = match.group(1)
                target_url = f"https://vortexa.cloud/server/{service_id}"
                print(f"🔄 正在跳转至服务器控制台: {target_url}", flush=True)
                page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            else:
                print("点击 Open Server Panel...", flush=True)
                page.get_by_text("Open Server Panel").first.click()

            # 5. 等待最终面板渲染（绝对不要用 networkidle，直接等界面元素出现）
            print("等待加载 Server 控制台面板元素...", flush=True)
            panel_indicator = page.locator('text=/console|power controls|files|startup|overview/i').first
            panel_indicator.wait_for(state="visible", timeout=30000)
            
            # 缓冲 8 秒，让 WebSocket 实时日志和 CPU/内存图表完整渲染出来
            time.sleep(8) 
            print(f"🎉 成功进入最终服务器面板！(当前 URL: {page.url})", flush=True)

            # 6. 截图保存并发送 TG
            screenshot_path = "vortexa_success.png"
            page.screenshot(path=screenshot_path, full_page=True)
            send_tg_photo(f"✅ Vortexa 服务器自动保活成功！\n当前节点面板: {page.url}", screenshot_path)

        except Exception as e:
            error_screenshot = "error.png"
            try:
                page.screenshot(path=error_screenshot, full_page=True)
            except Exception:
                pass
            error_msg = f"❌ Vortexa 保活执行失败 (当前停留 URL: {page.url})：\n{str(e)}"
            print(error_msg, flush=True)
            send_tg_photo(error_msg, error_screenshot)
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    main()
