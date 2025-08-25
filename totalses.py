# totalses.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def get_total_sessions():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://my.flame.edu.in/s/")

    wait = WebDriverWait(driver, 20)

    # --- Login ---
    username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
    username.send_keys("garv.mittal@flame.edu.in")  # replace
    password.send_keys("ilovedev1")                  # replace
    password.send_keys(Keys.RETURN)

    # --- Navigation ---
    menu_trigger = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.themeNavTrigger.comm-navigation__mobile-trigger")))
    menu_trigger.click()
    academic_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Academic']")))
    academic_btn.click()
    my_sessions = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='My Sessions']")))
    my_sessions.click()

    time.sleep(5)
    course_totals = {}
    empty_weeks = 0

    while True:
        time.sleep(3)
        events = driver.find_elements(By.XPATH, "//div[contains(@class, 'fc-timegrid-event')]")

        if len(events) == 0:
            empty_weeks += 1
        else:
            empty_weeks = 0
            for event in events:
                text = event.text.strip()
                # Try to extract course code from the event text robustly
                match = re.search(r"([A-Z]{3,4}\d{3})", text)
                if match:
                    course_code = match.group(1)
                    course_totals[course_code] = course_totals.get(course_code, 0) + 1
                else:
                    # Optionally log or skip events without a course code
                    pass

        if empty_weeks >= 3:
            break

        next_week = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='fc-icon fc-icon-chevron-right']")))
        next_week.click()

    driver.quit()

    totals_list = []
    for k, v in course_totals.items():
        totals_list.append({
            "Course Code": k,
            "Total Sessions": v,
            "Sessions Can Be Missed": int(v*0.25)
        })

    # Save to CSV
    import pandas as pd
    df = pd.DataFrame(totals_list)
    df.to_csv("totalses.csv", index=False)

    return totals_list

if __name__ == "__main__":
    get_total_sessions()
