# main.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import json
from datetime import datetime
import schedule
import requests

class CookiesFacebookBot:
    def __init__(self):
        self.cookies_file = os.getenv("COOKIES_FILE", "cookies.json")
        self.driver = None
        self.groups = []
        self.messages = [
            "🔐 Cyber Security ও Ethical Hacking শিখতে চান?\n\n💻 Online Safety, WiFi Security, Ethical Hacking Tutorials এবং নতুন নতুন Tech Tips পেতে এখনই Join করুন আমাদের Telegram Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 এখনই Join করুন: https://t.me/CybarSecurity\n\n📚 শুধুমাত্র Educational Purpose এর জন্য।",

"🔐 Cyber Security সম্পর্কে জানতে আগ্রহী?\n\n💻 WiFi Security, Online Safety ও Ethical Hacking Tutorials নিয়মিত পেতে এখনই Join করুন আমাদের Telegram Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join Now: https://t.me/CybarSecurity\n\n📚 Educational Purpose Only।",

"🔐 Ethical Hacking শিখতে চান?\n\n💻 Cyber Security Tips, WiFi Security Guide এবং নতুন Tech Updates পেতে এখনই Join করুন আমাদের Telegram Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join করুন: https://t.me/CybarSecurity\n\n📚 শুধুমাত্র শেখার উদ্দেশ্যে।",

"🔐 Cyber Security ও Online Protection সম্পর্কে জানতে চান?\n\n💻 Ethical Hacking Tutorials, WiFi Security এবং Security Tips পেতে Join করুন আমাদের Telegram Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join Now: https://t.me/CybarSecurity\n\n📚 Educational Purpose Only।",

"🔐 Ethical Hacking ও Cyber Security শেখার সেরা জায়গা খুঁজছেন?\n\n💻 Online Safety, WiFi Security এবং Tech Tips পেতে Join করুন আমাদের Telegram Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join করুন: https://t.me/CybarSecurity\n\n📚 শুধুমাত্র Educational Purpose।",

"🔐 Cyber Security ও Ethical Hacking সম্পর্কে শিখতে চান?\n\n💻 WiFi Security, Facebook Security Tips ও Online Safety Tutorials পেতে Join করুন আমাদের Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join Now: https://t.me/CybarSecurity\n\n📚 Educational Purpose Only।",

"🔐 Cyber Security সম্পর্কে নতুন কিছু শিখতে চান?\n\n💻 Ethical Hacking Tutorials, WiFi Security Guide এবং Tech Tips পেতে Join করুন আমাদের Telegram Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join করুন: https://t.me/CybarSecurity\n\n📚 শুধুমাত্র Educational Purpose।",

"🔐 Online Security ও Ethical Hacking শিখতে চান?\n\n💻 Cyber Security Tutorials, WiFi Security Tips এবং Online Safety Guide পেতে Join করুন আমাদের Telegram Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join Now: https://t.me/CybarSecurity\n\n📚 Educational Purpose Only।",

"🔐 Cyber Security সম্পর্কে জানুন সহজভাবে!\n\n💻 Ethical Hacking Tutorials, WiFi Security এবং Online Safety Tips পেতে Join করুন আমাদের Telegram Channel!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join করুন: https://t.me/CybarSecurity\n\n📚 শুধুমাত্র Educational Purpose।",

"🔐 Ethical Hacking ও Cyber Security শেখার জন্য Join করুন আমাদের Channel!\n\n💻 WiFi Security, Online Safety এবং Tech Tutorials নিয়মিত পেতে Join করুন এখনই!\n\n🚀 Channel Name: Cybar Security Lab\n\n👉 Join Now: https://t.me/CybarSecurity\n\n📚 Educational Purpose Only।"
        ]
    
    def load_cookies(self):
        """cookies.json থেকে load করে"""
        try:
            with open(self.cookies_file, 'r') as f:
                return json.load(f)
        except:
            print("❌ cookies.json not found!")
            return []
    
    def stealth_browser(self):
        """Undetectable Chrome for Render"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--headless")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def login_with_cookies(self):
        """Cookies দিয়ে auto login"""
        cookies = self.load_cookies()
        if not cookies:
            return False
        
        self.stealth_browser()
        self.driver.get("https://www.facebook.com")
        time.sleep(3)
        
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except:
                pass
        
        self.driver.refresh()
        time.sleep(8)
        
        # Login check
        if "facebook.com" in self.driver.current_url and "login" not in self.driver.current_url:
            print("✅ Cookies login successful!")
            return True
        else:
            print("❌ Cookies expired - update cookies.json")
            return False
    
    def scrape_all_groups(self):
        """সব joined groups scrape করে"""
        print("📋 Scraping joined groups...")
        self.driver.get("https://www.facebook.com/groups/?category=membership")
        time.sleep(10)
        
        # Scroll to load more groups
        for _ in range(5):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        
        # Extract group links
        group_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/')]")
        group_ids = []
        
        for link in group_links:
            href = link.get_attribute('href')
            if '/groups/' in href:
                gid = href.split('/groups/')[1].split('?')[0].split('/')[0]
                if len(gid) > 10:
                    group_ids.append(gid)
        
        self.groups = list(set(group_ids))[:30]  # Top 30 unique
        print(f"✅ Found {len(self.groups)} groups")
        return self.groups
    
    def post_to_group(self, group_id):
        """Single group এ random message দিয়ে post"""
        try:
            message = random.choice(self.messages)
            self.driver.get(f"https://m.facebook.com/groups/{group_id}")
            time.sleep(random.randint(3, 6))
            
            # Post box
            post_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[placeholder*='mind'], div[role='textbox']"))
            )
            post_box.click()
            time.sleep(1)
            
            # Type message
            post_box.clear()
            post_box.send_keys(message)
            time.sleep(2)
            
            # Post button
            post_btn = self.driver.find_element(By.XPATH, "//button[@type='submit'], //div[@aria-label*='Post'], //div[contains(text(), 'Post')]")
            post_btn.click()
            
            time.sleep(4)
            print(f"✅ Posted to {group_id[:15]}...")
            return True
            
        except Exception as e:
            print(f"❌ {group_id[:15]} failed: {str(e)[:50]}")
            return False
    
    def hourly_post_batch(self):
        """1 ঘন্টায় সব groups এ post"""
        print(f"\n🚀 HOURLY BATCH START | {datetime.now().strftime('%H:%M:%S')}")
        
        success = 0
        for i, group_id in enumerate(self.groups):
            if self.post_to_group(group_id):
                success += 1
            
            # Random delay between groups
            delay = random.randint(45, 120)
            time.sleep(delay)
        
        print(f"📊 Batch complete: {success}/{len(self.groups)} successful")

def main():
    bot = CookiesFacebookBot()
    
    if bot.login_with_cookies():
        bot.scrape_all_groups()
        
        # Schedule 1 hour intervals
        schedule.every(1).hours.do(bot.hourly_post_batch)
        
        # First run immediately
        bot.hourly_post_batch()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        print("Login failed - regenerate cookies!")

if __name__ == "__main__":
    main()
