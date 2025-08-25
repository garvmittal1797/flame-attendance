# attendance.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_attendance():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://my.flame.edu.in/s/")

    wait = WebDriverWait(driver, 20)

    # --- Login ---
    username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

    username.send_keys("garv.mittal@flame.edu.in")  # replace with your username
    password.send_keys("ilovedev1")                  # replace with your password
    password.send_keys(Keys.RETURN)

    # --- Navigation ---
    menu_trigger = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.themeNavTrigger.comm-navigation__mobile-trigger")))
    menu_trigger.click()
    academic_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Academic']")))
    academic_btn.click()
    attendance_summary = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Attendance Summary']")))
    attendance_summary.click()

    # --- Switch to summary iframe ---
    iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    driver.switch_to.frame(iframe)

    dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[contains(@class,'slds-select')]")))
    dropdown.click()
    option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[contains(text(),'2025/26S1')]")))
    option.click()

    time.sleep(2)
    spans = driver.find_elements(By.XPATH, "//span[@style='cursor: pointer; text-decoration: underline;']")

    all_subjects = []

    for i in range(len(spans)):
        spans = driver.find_elements(By.XPATH, "//span[@style='cursor: pointer; text-decoration: underline;']")
        span = spans[i]
        span.click()
        time.sleep(1)

        driver.switch_to.default_content()
        detail_iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(detail_iframe)

        tds = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//td[@class='THIS.header-data']")))
        subject_data = {
            "name": tds[0].text.strip(),
            "course": tds[1].text.strip(),
            "attended": tds[2].text.strip(),
            "missed": tds[3].text.strip(),
            "percentage": tds[4].text.strip()
        }
        all_subjects.append(subject_data)

        back = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Back'] | //button[@title='Back']")))
        back.click()
        driver.switch_to.default_content()
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        time.sleep(1)

    driver.quit()
    return all_subjects
