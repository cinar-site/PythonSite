from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# -----------------------------
# MAIL BİLGİLERİ (direkt)
# -----------------------------
SENDER_EMAIL = "cinareymenozcelik733@gmail.com"
SENDER_PASSWORD = "khlj klrg typq epqh"

# -----------------------------
# DATABASE OLUŞTUR
# -----------------------------
def init_db():
    conn = sqlite3.connect("users.db")
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
# MAIL GÖNDERME
# -----------------------------
def send_email(to_email, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"Email gönderildi: {to_email}")
    except Exception as e:
        print("Email gönderilemedi:", e)

# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]

        if password != password2:
            flash("Şifreler eşleşmiyor!")
            return redirect(url_for("register"))

        # --- DB işlemleri ---
        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            if c.fetchone():
                flash("Bu email zaten kayıtlı!")
                conn.close()
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)
            c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                      (name, email, hashed_password))
            conn.commit()
            conn.close()
        except Exception as e:
            print("DB hatası:", e)
            flash("Kayıt sırasında bir hata oluştu!")
            return redirect(url_for("register"))

        # --- Mail gönderimi ---
        try:
            send_email(email, "Hoşgeldiniz!", f"Merhaba {name}, kayıt işleminiz başarılı!")
            flash("Kayıt başarılı! E-posta gönderildi.")
        except Exception as e:
            print("Mail hatası:", e)
            flash("Kayıt başarılı! Ama e-posta gönderilemedi.")

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

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            flash(f"Hoşgeldiniz, {user[1]}!")
            return redirect(url_for("dashboard"))
        else:
            flash("Email veya şifre hatalı!")
            return redirect(url_for("login"))

    return render_template("login.html")

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Önce giriş yapmalısınız!")
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
    app.run(debug=True)
