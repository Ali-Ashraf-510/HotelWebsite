import logging
from os import getenv
import pyodbc
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, url_for, session, jsonify
from datetime import datetime
import atexit
import bcrypt

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY", "your_secret_key")  # جلب المفتاح من .env

# Database Connection
server = getenv("DB_SERVER", ".")
database = getenv("DB_NAME", "HotelBooking")

conn = pyodbc.connect(
    f"Driver={{SQL Server}};Server={server};Database={database};Trusted_Connection=yes;"
)
cursor = conn.cursor()
logging.basicConfig(level=logging.DEBUG)

# إغلاق الاتصال عند إغلاق التطبيق
atexit.register(cursor.close)
atexit.register(conn.close)

# Custom Jinja filter for datetime
def date_to_datetime(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

app.jinja_env.filters['datetime'] = date_to_datetime

# ---------- Service Functions ----------

def get_all_hotels(cursor):
    query = """
        SELECT hotel_id, name, description, location, price_per_night, image_url
        FROM Hotels;
    """
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_hotel_by_id(cursor, hotel_id):
    query = """
        SELECT hotel_id, name, description, location, price_per_night, image_url
        FROM Hotels
        WHERE hotel_id = ?;
    """
    cursor.execute(query, (hotel_id,))
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None

def create_user(cursor, full_name, email, password):
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        query = """
            INSERT INTO Users (full_name, email, password)
            VALUES (?, ?, ?);
        """
        cursor.execute(query, (full_name, email, hashed_password.decode('utf-8')))
    except pyodbc.IntegrityError:
        raise ValueError("Email already exists")
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise

def login_user(cursor, email, password):
    query = """
        SELECT user_id, full_name, password FROM Users
        WHERE email = ?;
    """
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        return user
    return None

def book_hotel_for_user(cursor, user_id, hotel_id, date_from, date_to):
    query = """
        INSERT INTO Bookings (user_id, hotel_id, date_from, date_to)
        VALUES (?, ?, ?, ?);
    """
    cursor.execute(query, (user_id, hotel_id, date_from, date_to))

def add_review_for_hotel(cursor, user_id, hotel_id, review_text):
    query = """
        INSERT INTO Reviews (user_id, hotel_id, content)
        VALUES (?, ?, ?);
    """
    cursor.execute(query, (user_id, hotel_id, review_text))

def get_reviews_for_hotel(cursor, hotel_id):
    query = """
        SELECT R.content, U.full_name
        FROM Reviews R
        JOIN Users U ON R.user_id = U.user_id
        WHERE R.hotel_id = ?;
    """
    cursor.execute(query, (hotel_id,))
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def search_hotels(cursor, keyword):
    query = """
        SELECT hotel_id, name, description, location, price_per_night, image_url
        FROM Hotels
        WHERE name LIKE ? OR description LIKE ?;
    """
    pattern = f"%{keyword}%"
    cursor.execute(query, (pattern, pattern))
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_random_hotels(cursor):
    query = """
        SELECT TOP 3 hotel_id, name, location, description, price_per_night, image_url
        FROM Hotels
        ORDER BY NEWID();
    """
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_user_bookings(cursor, user_id):
    query = """
        SELECT B.booking_id, B.date_from, B.date_to, H.name, H.price_per_night, H.image_url
        FROM Bookings B
        JOIN Hotels H ON B.hotel_id = H.hotel_id
        WHERE B.user_id = ?;
    """
    cursor.execute(query, (user_id,))
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

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
        try:
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            create_user(cursor, name, email, password)
            conn.commit()
            return redirect(url_for("login"))
        except ValueError as e:
            return render_template("auth/register.html", error=str(e))
        except Exception as e:
            logging.error(f"Registration error: {e}")
            return render_template("auth/register.html", error="An error occurred")
    return render_template("auth/register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = login_user(cursor, email, password)
        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
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
    if not hotel:
        abort(404)
    reviews = get_reviews_for_hotel(cursor, hotel_id)
    return render_template("hotel/hotel_detail.html", hotel=hotel, reviews=reviews)

@app.route("/book/<int:hotel_id>", methods=["POST"])
def book_hotel(hotel_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    date_from = request.form["date_from"]
    date_to = request.form["date_to"]

    try:
        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
        if date_to_dt <= date_from_dt:
            return render_template("hotel/hotel_detail.html", 
                                 hotel=get_hotel_by_id(cursor, hotel_id), 
                                 reviews=get_reviews_for_hotel(cursor, hotel_id), 
                                 error="Check-out date must be after check-in date")
        book_hotel_for_user(cursor, user_id, hotel_id, date_from, date_to)
        conn.commit()
        return redirect(url_for("home"))
    except Exception as e:
        logging.error(f"Booking error: {e}")
        return render_template("hotel/hotel_detail.html", 
                             hotel=get_hotel_by_id(cursor, hotel_id), 
                             reviews=get_reviews_for_hotel(cursor, hotel_id), 
                             error="An error occurred during booking")

@app.route("/review/<int:hotel_id>", methods=["POST"])
def add_review(hotel_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    content = request.form["review"]
    try:
        add_review_for_hotel(cursor, user_id, hotel_id, content)
        conn.commit()
        return redirect(url_for("hotel_detail", hotel_id=hotel_id))
    except Exception as e:
        logging.error(f"Review error: {e}")
        return render_template("hotel/hotel_detail.html", 
                             hotel=get_hotel_by_id(cursor, hotel_id), 
                             reviews=get_reviews_for_hotel(cursor, hotel_id), 
                             error="An error occurred while adding review")

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "")
    hotels = search_hotels(cursor, keyword)
    return jsonify(hotels)

@app.route("/my_bookings")
def my_bookings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    bookings = get_user_bookings(cursor, user_id)
    return render_template("booking/my_bookings.html", bookings=bookings)

@app.route("/cancel_booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    try:
        query = "DELETE FROM Bookings WHERE booking_id = ? AND user_id = ?"
        cursor.execute(query, (booking_id, user_id))
        conn.commit()
        return redirect(url_for("my_bookings"))
    except Exception as e:
        logging.error(f"Cancel booking error: {e}")
        return render_template("booking/my_bookings.html", 
                             bookings=get_user_bookings(cursor, user_id), 
                             error="An error occurred while canceling booking")

# ---------- App Run ----------
if __name__ == "__main__":
    app.run(debug=True)