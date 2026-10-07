from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "my-secret-key"


# DB 연결
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


# 회원 테이블 생성
def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_table()


# 메인 페이지
@app.route("/")
def home():
    return render_template("index.html")


# 회원가입
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return "이미 사용 중인 아이디입니다."

    return render_template("signup.html")


# 로그인
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect("/mypage")

        return "아이디 또는 비밀번호가 틀렸습니다."

    return render_template("login.html")


# 마이페이지
@app.route("/mypage")
def mypage():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "mypage.html",
        username=session["username"]
    )


# 로그아웃
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# 서버 실행
if __name__ == "__main__":
    app.run(debug=True)