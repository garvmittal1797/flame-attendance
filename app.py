
# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash

import pandas as pd
from attendance import get_attendance
from totalses import get_total_sessions
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Fetch live attendance route
@app.route("/fetch-attendance")
def fetch_attendance():
    from attendance import get_attendance
    get_attendance()
    flash("Live attendance fetched and updated.")
    return redirect(url_for("home"))


@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # Read attendance and totalses from CSV
    att_df = pd.read_csv("attendance.csv")
    tot_df = pd.read_csv("totalses.csv")

    # Defensive column renaming for merge
    att_df.rename(columns={"course": "Course Code", "attended": "Attended", "missed": "Missed", "percentage": "Percentage Attendance"}, inplace=True)


    # Standardize course codes for merge
    import re
    att_df["Course Code"] = att_df["Course Code"].astype(str).str.strip().str.upper()
    tot_df["Course Code"] = tot_df["Course Code"].astype(str).str.strip().str.upper()
    # Extract only the code part from attendance Course Code
    att_df["Course Code"] = att_df["Course Code"].apply(lambda x: re.search(r"[A-Z]{3,4}\d{3}", x).group(0) if pd.notnull(x) and re.search(r"[A-Z]{3,4}\d{3}", x) else x)

    # Convert columns to int if possible
    for col in ["Attended", "Missed", "Percentage Attendance"]:
        if col in att_df.columns:
            att_df[col] = pd.to_numeric(att_df[col], errors="coerce").fillna(0).astype(int)
    for col in ["Total Sessions", "Sessions Can Be Missed"]:
        if col in tot_df.columns:
            tot_df[col] = pd.to_numeric(tot_df[col], errors="coerce").fillna(0).astype(int)

    print("attendance course codes:", att_df["Course Code"].tolist())
    print("totalses course codes:", tot_df["Course Code"].tolist())

    # Merge
    merged = pd.merge(att_df, tot_df, on="Course Code", how="inner")
    print("DEBUG: merged DataFrame:")
    print(merged)

    # Prepare table data for template
    table_data = merged.to_dict(orient="records")

    # Save merged to CSV
    merged.to_csv("attendance_summary.csv", index=False)
    # Get first name from users.csv using siteusername in session
    first_name = None
    if "siteusername" in session:
        import csv
        with open("users.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["siteusername"] == session["siteusername"]:
                    # Try to extract first name from username or siteusername
                    # If username is email, take part before @, else use siteusername
                    uname = row["username"]
                    if "@" in uname:
                        first_name = uname.split("@")[0].split(".")[0].capitalize()
                    else:
                        first_name = row["siteusername"].capitalize()
                    break
    return render_template("index.html", table_data=table_data, first_name=first_name)

    
# Login route
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

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(debug=True)