from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# -----------------------------
# DATABASE
# -----------------------------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# MAIL AYARLARI
# -----------------------------
SENDER_EMAIL = "cinareymenozcelik733@gmail.com"
SENDER_PASSWORD = "khlj klrg typq epqh"  # Gmail “App Password” olmalı

def send_email(to_email, subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()

        print("Mail gönderildi")

    except Exception as e:
        print("Mail gönderilemedi, hata:", e)
        # Hata oluşsa bile siteyi kırmaz, sadece terminale yazılır

# -----------------------------
# ANA SAYFA
# -----------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]

        if password != password2:
            flash("Şifreler eşleşmiyor!")
            return redirect(url_for("register"))

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()

        if user:
            flash("Bu email zaten kayıtlı!")
            conn.close()
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                  (name, email, hashed_password))
        conn.commit()
        conn.close()

        # Mail gönderme artık güvenli
        try:
            send_email(email, "Hoşgeldiniz!", f"Merhaba {name}, kayıt başarılı!")
        except:
            pass  # Hata olsa bile site çalışmaya devam eder

        flash("Kayıt başarılı!")
        return redirect(url_for("login"))

    return render_template("register.html")

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Giriş başarılı!")
            return redirect(url_for("dashboard"))
        else:
            flash("Email veya şifre yanlış!")
            return redirect(url_for("login"))

    return render_template("login.html")

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Önce giriş yap!")
        return redirect(url_for("login"))

    return render_template("dashboard.html", name=session["user_name"])

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Çıkış yapıldı!")
    return redirect(url_for("login"))

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
