from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import time
import re
# --- Selenium imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Attendance scraping ---
def get_attendance():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("https://my.flame.edu.in/s/")
    wait = WebDriverWait(driver, 20)
    username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
    username.send_keys("garv.mittal@flame.edu.in")  # replace with your username
    password.send_keys("ilovedev1")                  # replace with your password
    password.send_keys(Keys.RETURN)
    menu_trigger = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.themeNavTrigger.comm-navigation__mobile-trigger")))
    menu_trigger.click()
    academic_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Academic']")))
    academic_btn.click()
    attendance_summary = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Attendance Summary']")))
    attendance_summary.click()
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
    df = pd.DataFrame(all_subjects)
    df.to_csv("attendance.csv", index=False)
    return all_subjects

# --- Totalses scraping ---
def get_total_sessions():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("https://my.flame.edu.in/s/")
    wait = WebDriverWait(driver, 20)
    username = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    password = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
    username.send_keys("garv.mittal@flame.edu.in")  # replace
    password.send_keys("ilovedev1")                  # replace
    password.send_keys(Keys.RETURN)
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
                match = re.search(r"([A-Z]{3,4}\d{3})", text)
                if match:
                    course_code = match.group(1)
                    course_totals[course_code] = course_totals.get(course_code, 0) + 1
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
    df = pd.DataFrame(totals_list)
    df.to_csv("totalses.csv", index=False)
    return totals_list

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

@app.route("/fetch-attendance")
def fetch_attendance_route():
    get_attendance()
    flash("Live attendance fetched and updated.")
    return redirect(url_for("home"))

@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    att_df = pd.read_csv("attendance.csv")
    tot_df = pd.read_csv("totalses.csv")
    att_df.rename(columns={"course": "Course Code", "attended": "Attended", "missed": "Missed", "percentage": "Percentage Attendance"}, inplace=True)
    att_df["Course Code"] = att_df["Course Code"].astype(str).str.strip().str.upper()
    tot_df["Course Code"] = tot_df["Course Code"].astype(str).str.strip().str.upper()
    att_df["Course Code"] = att_df["Course Code"].apply(lambda x: re.search(r"[A-Z]{3,4}\d{3}", x).group(0) if pd.notnull(x) and re.search(r"[A-Z]{3,4}\d{3}", x) else x)
    for col in ["Attended", "Missed", "Percentage Attendance"]:
        if col in att_df.columns:
            att_df[col] = pd.to_numeric(att_df[col], errors="coerce").fillna(0).astype(int)
    for col in ["Total Sessions", "Sessions Can Be Missed"]:
        if col in tot_df.columns:
            tot_df[col] = pd.to_numeric(tot_df[col], errors="coerce").fillna(0).astype(int)
    merged = pd.merge(att_df, tot_df, on="Course Code", how="inner")
    table_data = merged.to_dict(orient="records")
    merged.to_csv("attendance_summary.csv", index=False)
    first_name = None
    if "siteusername" in session:
        import csv
        with open("users.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["siteusername"] == session["siteusername"]:
                    uname = row["username"]
                    if "@" in uname:
                        first_name = uname.split("@")[0].split(".")[0].capitalize()
                    else:
                        first_name = row["siteusername"].capitalize()
                    break
    return render_template("index.html", table_data=table_data, first_name=first_name)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        siteusername = request.form["username"]
        sitepassword = request.form["password"]
        import csv
        with open("users.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["siteusername"] == siteusername and row["sitepassword"] == sitepassword:
                    session["logged_in"] = True
                    session["siteusername"] = siteusername
                    return redirect(url_for("home"))
        error = "Invalid site username or password."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
