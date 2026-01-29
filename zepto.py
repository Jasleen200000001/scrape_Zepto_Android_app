import os
import time
import re
import traceback
import pandas as pd
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


class ZeptoScraper:
    def __init__(self, device_udid, category="Fruits & Vegetables", max_products=10):
        self.device_udid = device_udid
        self.category = category
        self.max_products = max_products
        self.products = []

        # Ensure folder exists for images
        os.makedirs("product_images", exist_ok=True)

        # Initialize Appium driver
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        caps = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "Android",
            "appium:udid": self.device_udid,
            "appium:appPackage": "com.zeptoconsumerapp",
            "appium:appActivity": "com.zeptoconsumerapp.MainActivity",
            "appium:noReset": True,
            "appium:uiautomator2ServerInstallTimeout": 60000
        }
        options = UiAutomator2Options().load_capabilities(caps)
        return webdriver.Remote("http://127.0.0.1:4723", options=options)

    def open_category(self):
        """Open the category tab in Zepto app."""
        time.sleep(5)
        try:
            category_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "(//android.view.ViewGroup[@resource-id='com.zeptoconsumerapp:id/bottom-navigation-menu'])[2]/android.view.ViewGroup")
                )
            )
            category_button.click()
            time.sleep(2)
            print("✅ Category tab opened")
        except Exception as e:
            print("❌ Failed to open category tab:", e)
            traceback.print_exc()

    def open_category_by_name(self):
        """Click the desired category (dynamic)."""
        time.sleep(2)
        try:
            category_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//android.widget.Button[@content-desc='{self.category}']")
                )
            )
            category_btn.click()
            time.sleep(2)
            print(f"✅ Category '{self.category}' opened")
        except Exception as e:
            print(f"❌ Failed to open category '{self.category}':", e)
            traceback.print_exc()

    def scroll_and_extract(self):
        """Scroll through products and extract details."""
        screen = self.driver.get_window_size()
        start_x = screen["width"] // 2
        start_y = int(screen["height"] * 0.8)
        end_y = int(screen["height"] * 0.3)

        seen = set()
        no_new_scrolls = 0
        scroll_count = 0

        while len(self.products) < self.max_products and no_new_scrolls < 3:
            scroll_count += 1
            print(f"\n--- SCROLL {scroll_count} ---")

            products = self.driver.find_elements(
                By.XPATH,
                "//android.widget.Button[@resource-id='com.zeptoconsumerapp:id/product-card-container']"
            )
            print("Products visible:", len(products))
            new_found = 0

            for product in products:
                if len(self.products) >= self.max_products:
                    break
                try:
                    desc = product.get_attribute("content-desc")
                    if not desc or desc in seen:
                        continue

                    seen.add(desc)
                    new_found += 1

                    parts = [p.strip() for p in desc.split(",")]
                    name = parts[0] if len(parts) > 0 else ""
                    weight = parts[1] if len(parts) > 1 else ""

                    mrp = re.search(r"MRP is\s*₹(\d+)", desc)
                    price = re.search(r"Price.*₹(\d+)", desc)
                    mrp = mrp.group(1) if mrp else ""
                    price = price.group(1) if price else ""

                    img_path = f"product_images/{len(self.products)+1}_{re.sub(r'[^a-zA-Z0-9]', '_', name)}.png"
                    try:
                        product.screenshot(img_path)
                    except Exception as e:
                        print("⚠️ Failed to save screenshot:", e)

                    self.products.append({
                        "Name": name,
                        "Weight": weight,
                        "MRP": mrp,
                        "Price": price,
                        "Image_Path": img_path
                    })

                    print(f"✅ [{len(self.products)}] {name} | {weight} | ₹{price}")

                except Exception as e:
                    print("❌ ERROR extracting product:", e)
                    traceback.print_exc()

            if new_found == 0:
                no_new_scrolls += 1
                print("⚠️ No new products found on this scroll")
            else:
                no_new_scrolls = 0

            # Swipe up to load more products
            try:
                self.driver.execute_script('mobile: swipe', {'direction': 'up'})
            except WebDriverException:
                # fallback
                self.driver.swipe(start_x, start_y, start_x, end_y, 800)

            time.sleep(2)

        print(f"\n✅ DONE: Collected {len(self.products)} products")

    def save_to_excel(self, filename="zepto_products.xlsx"):
        """Save scraped products to Excel."""
        df = pd.DataFrame(self.products)
        df.to_excel(filename, index=False)
        print(f"📁 Saved {len(self.products)} products to {filename}")

    def save_to_csv(self, filename="zepto_products.csv"):
        """Save scraped products to CSV."""
        df = pd.DataFrame(self.products)
        df.to_csv(filename, index=False)
        print(f"📁 Saved {len(self.products)} products to {filename}")

    def quit_driver(self):
        """Quit Appium driver."""
        self.driver.quit()


if __name__ == "__main__":
    DEVICE_UDID = "RZ8R11JAFXV"  # Replace with your device UDID
    CATEGORY = "Fruits & Vegetables"
    MAX_PRODUCTS = 10

    scraper = ZeptoScraper(device_udid=DEVICE_UDID, category=CATEGORY, max_products=MAX_PRODUCTS)

    try:
        scraper.open_category()
        scraper.open_category_by_name()
        scraper.scroll_and_extract()
        scraper.save_to_excel()
        scraper.save_to_csv()
    finally:
        scraper.quit_driver()
