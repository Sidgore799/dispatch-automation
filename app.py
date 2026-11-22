import os
from functools import wraps
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dispatch-dev-key")

USER = {"username": "admin", "password": "admin", "name": "Administrator", "role": "Admin"}
STAGES = ["Proposal received", "Underwriting", "Approved", "Policy issued", "Dispatched", "Delivered"]
PRODUCTS = ["Term Life", "Health Shield", "Motor Comprehensive", "Home Secure", "Travel Plus"]

# Sample data lives in memory: it resets whenever the container restarts.
CASES = [
    {"id": "CASE-1001", "customer": "Rahul Patil", "mobile": "9876500001", "product": "Term Life",
     "sum_assured": 5000000, "premium": 14200, "term": 20, "stage": 5, "policy_no": "POL-500101", "created": "2026-11-02"},
    {"id": "CASE-1002", "customer": "Sneha Kulkarni", "mobile": "9876500002", "product": "Health Shield",
     "sum_assured": 1000000, "premium": 18500, "term": 1, "stage": 4, "policy_no": "POL-500102", "created": "2026-11-09"},
    {"id": "CASE-1003", "customer": "Amit Deshmukh", "mobile": "9876500003", "product": "Motor Comprehensive",
     "sum_assured": 650000, "premium": 12800, "term": 1, "stage": 1, "policy_no": None, "created": "2026-11-18"},
]


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == USER["username"] and request.form.get("password") == USER["password"]:
            session["user"] = USER["username"]
            return redirect(url_for("tracker"))
        return render_template("login.html", error="Wrong username or password. Try again.")
    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    return redirect(url_for("tracker"))


@app.route("/tracker")
@login_required
def tracker():
    q = request.args.get("q", "").strip().lower()
    cases = [c for c in CASES if q in c["id"].lower() or q in c["customer"].lower()]
    return render_template("tracker.html", cases=cases, stages=STAGES, q=q)


@app.route("/advance/<cid>", methods=["POST"])
@login_required
def advance(cid):
    for c in CASES:
        if c["id"] == cid and c["stage"] < len(STAGES) - 1:
            c["stage"] += 1
            if STAGES[c["stage"]] == "Policy issued":
                c["policy_no"] = f"POL-{500101 + sum(1 for x in CASES if x['policy_no'])}"
            flash(f"{cid} moved to {STAGES[c['stage']]}.")
    return redirect(url_for("tracker"))


@app.route("/view")
@login_required
def view():
    status = request.args.get("status", "")
    cases = [c for c in CASES if not status or STAGES[c["stage"]] == status]
    return render_template("view.html", cases=cases, stages=STAGES, status=status)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        f = request.form
        cid = f"CASE-{1001 + len(CASES)}"
        CASES.append({"id": cid, "customer": f["customer"].strip(), "mobile": f["mobile"].strip(),
                      "product": f["product"], "sum_assured": int(f["sum_assured"]),
                      "premium": int(f["premium"]), "term": int(f["term"]), "stage": 0,
                      "policy_no": None, "created": date.today().isoformat()})
        flash(f"Case {cid} created. Track it under Case Tracker.")
        return redirect(url_for("tracker"))
    return render_template("create.html", products=PRODUCTS)


@app.route("/policy")
@login_required
def policy():
    issued = [c for c in CASES if c["policy_no"]]
    return render_template("policy.html", cases=issued, stages=STAGES)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=USER, total=len(CASES))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
