
# app.py
from flask import Flask, render_template


import pandas as pd
from attendance import get_attendance
from totalses import get_total_sessions
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():

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
    return render_template("index.html", table_data=table_data)

if __name__ == "__main__":
    app.run(debug=True)
