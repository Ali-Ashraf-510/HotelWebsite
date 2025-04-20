import logging
from os import getenv
import pyodbc
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, url_for, session

from services import *  # لازم تكون الخدمات متوافقة مع الكيانات الجديدة: Hotels, Users, Bookings, Reviews

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # ضروري لتسجيل الدخول

# Database Connection
server = getenv("DB_SERVER", ".")
database = getenv("DB_NAME", "HotelBooking")

conn = pyodbc.connect(
    f"Driver={{SQL Server}};Server={server};Database={database};Trusted_Connection=yes;"
)
cursor = conn.cursor()
logging.basicConfig(level=logging.DEBUG)

# ---------- Routes ----------

@app.route("/")
def home():
    hotels = get_random_hotels(cursor)
    return render_template("home/home.html", hotels=hotels)


@app.route("/hotels")
def all_hotels():
    hotels = get_all_hotels(cursor)
    return render_template("hotel/all_hotels.html", hotels=hotels)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        create_user(cursor, name, email, password)
        conn.commit()
        return redirect(url_for("login"))
    return render_template("auth/register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = login_user(cursor, email, password)
        if user:
            session["user_id"] = user[0]  # استخدام 0 للوصول إلى user_id
            session["user_name"] = user[1]  # استخدام 1 للوصول إلى full_name
            return redirect(url_for("home"))
        else:
            return render_template("auth/login.html", error="Invalid credentials")
    return render_template("auth/login.html")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = login_user(cursor, email, password)
        if user:
            session["user_id"] = user.id
            session["user_name"] = user.name
            return redirect(url_for("home"))
        else:
            return render_template("auth/login.html", error="Invalid credentials")
    return render_template("auth/login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/hotel/<int:hotel_id>")
def hotel_detail(hotel_id):
    hotel = get_hotel_by_id(cursor, hotel_id)
    reviews = get_reviews_for_hotel(cursor, hotel_id)
    return render_template("hotel/detail.html", hotel=hotel, reviews=reviews)

@app.route("/book/<int:hotel_id>", methods=["POST"])
def book_hotel(hotel_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    date_from = request.form["date_from"]
    date_to = request.form["date_to"]
    book_hotel_for_user(cursor, user_id, hotel_id, date_from, date_to)
    conn.commit()
    return redirect(url_for("home"))

@app.route("/review/<int:hotel_id>", methods=["POST"])
def add_review(hotel_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    content = request.form["review"]
    add_review_for_hotel(cursor, user_id, hotel_id, content)
    conn.commit()
    return redirect(url_for("hotel_detail", hotel_id=hotel_id))

# ---------- App Run ----------
app.run(debug=True)
cursor.close()
conn.close()
