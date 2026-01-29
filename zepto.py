import time
import pandas as pd
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ZeptoScraper:
    def __init__(self, device_udid, category, max_products=100):
        self.device_udid = device_udid
        self.category = category
        self.max_products = max_products
        self.products = []
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        desired_caps = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "Android",
            "appium:udid": self.device_udid,
            "appium:appPackage": "com.zeptoconsumerapp",
            "appium:appActivity": "com.zeptoconsumerapp.MainActivity",
            "appium:noReset": True,
            "appium:uiautomator2ServerInstallTimeout": 60000
        }
        options = UiAutomator2Options().load_capabilities(desired_caps)
        driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
        return driver

    def open_category(self):
        """Open category tab in Zepto app"""
        time.sleep(5)

        try:
            category_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "(//android.view.ViewGroup[@resource-id='com.zeptoconsumerapp:id/bottom-navigation-menu'])[2]/android.view.ViewGroup"
                    )
                )
            )
            category_button.click()
            time.sleep(3)
            print("Category tab opened successfully")

        except Exception as e:
            print("Category tab not found:", e)
            
    def open_fruits_vegetables(self):
        """Click Fruits & Vegetables category"""
        time.sleep(2)
        try:
            fruits_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//android.widget.Button[@content-desc='Fruits & Vegetables']"
                    )
                )
            )
            fruits_btn.click()
            time.sleep(3)
            print("Fruits & Vegetables category opened successfully")

        except Exception as e:
            print("Failed to open Fruits & Vegetables:", e)


    def scroll_and_extract(self):
        import re
        import time

        screen = self.driver.get_window_size()
        start_x = screen['width'] // 2
        start_y = int(screen['height'] * 0.8)
        end_y = int(screen['height'] * 0.3)

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

            for idx, product in enumerate(products):
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

                    print(f"✅ [{len(self.products)+1}] {name} | {weight} | ₹{price}")

                    img_path = f"product_images/{len(self.products)+1}.png"
                    product.screenshot(img_path)

                    self.products.append({
                        "Name": name,
                        "Weight": weight,
                        "MRP": mrp,
                        "Price": price,
                        "Image_Path": img_path
                    })

                except Exception as e:
                    print("❌ ERROR:", e)

            if new_found == 0:
                no_new_scrolls += 1
                print("⚠️ No new products found on this scroll")
            else:
                no_new_scrolls = 0

            self.driver.swipe(start_x, start_y, start_x, end_y, 800)
            time.sleep(3)

        print(f"\n✅ DONE: Collected {len(self.products)} products")
                    

    def save_to_excel(self, filename="zepto_products.xlsx"):
        """Save scraped products to Excel."""
        df = pd.DataFrame(self.products)
        df.to_excel(filename, index=False)
        print(f"Saved {len(self.products)} products to {filename}")

    def quit_driver(self):
        """Close Appium driver."""
        self.driver.quit()


if __name__ == "__main__":
    # Configuration
    DEVICE_UDID = "RZ8R11JAFXV"  # Replace with your device UDID
    CATEGORY = "Fruits & Vegetables"  # Replace with desired category
    MAX_PRODUCTS = 100  # Maximum number of products to scrape

    # Run scraper
    scraper = ZeptoScraper(device_udid=DEVICE_UDID, category=CATEGORY, max_products=MAX_PRODUCTS)
    scraper.open_category()
    scraper.open_fruits_vegetables()
    scraper.scroll_and_extract()
    scraper.save_to_excel()
    scraper.quit_driver()
