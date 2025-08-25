# app.py
from flask import Flask, render_template
from attendance import get_attendance
from totalses import get_total_sessions

app = Flask(__name__)

@app.route("/")
def home():
    subjects = get_attendance()
    totals = get_total_sessions()
    return render_template("index.html", subjects=subjects, totals=totals)

if __name__ == "__main__":
    app.run(debug=True)
