from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd 

# --- Setup ---
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://my.flame.edu.in/s/")

wait = WebDriverWait(driver, 20)

# --- Login ---
username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

username.send_keys("garv.mittal@flame.edu.in")
password.send_keys("ilovedev1")
password.send_keys(Keys.RETURN)

# --- Navigation ---
menu_trigger = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.themeNavTrigger.comm-navigation__mobile-trigger")))
menu_trigger.click()

academic_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Academic']")))
academic_btn.click()

my_sessions = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='My Sessions']")))
my_sessions.click()

# --- Wait for events to load ---
time.sleep(5)

# --- Scrape all events on current week ---
events = wait.until(EC.presence_of_all_elements_located(
    (By.XPATH, "//div[contains(@class, 'fc-timegrid-event')]")
))

print("✅ Found", len(events), "events on this week")

all_event_texts = []
for idx, event in enumerate(events, start=1):
    try:
        text = event.text.strip()
        print(f"📌 Event {idx}: {text}")
        all_event_texts.append(text)
    except Exception as e:
        print(f"⚠️ Could not read event {idx}: {e}")

# --- Save to CSV ---
df = pd.DataFrame(all_event_texts, columns=["Event"])
df.to_csv("events_week.csv", index=False, encoding="utf-8-sig")
print("💾 Saved events to events_week.csv")

# --- Click Next Week ---
next_week = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='fc-icon fc-icon-chevron-right']")))
next_week.click()
print("👉 Moved to Next Week")

time.sleep(5)

# (Optional: you can repeat the scraping again for next week in a loop)
