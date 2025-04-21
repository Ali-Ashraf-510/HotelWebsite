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
app.secret_key = getenv("SECRET_KEY", "your_secret_key")

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
        SELECT 
            h.hotel_id, h.name, h.description, h.location, h.price_per_night, h.image_url,
            h.star_rating, h.total_rooms, h.average_rating,
            STUFF((
                SELECT ', ' + a2.name
                FROM Amenities a2
                JOIN Hotel_Amenities ha2 ON a2.amenity_id = ha2.amenity_id
                WHERE ha2.hotel_id = h.hotel_id
                FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS amenities
        FROM Hotels h;
    """
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_hotel_by_id(cursor, hotel_id):
    query = """
        SELECT 
            h.hotel_id, h.name, h.description, h.location, h.price_per_night, h.image_url,
            h.star_rating, h.total_rooms, h.average_rating,
            STUFF((
                SELECT ', ' + a2.name
                FROM Amenities a2
                JOIN Hotel_Amenities ha2 ON a2.amenity_id = ha2.amenity_id
                WHERE ha2.hotel_id = h.hotel_id
                FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS amenities
        FROM Hotels h
        WHERE h.hotel_id = ?;
    """
    cursor.execute(query, (hotel_id,))
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None

def create_user(cursor, full_name, email, password, phone_number=None):
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        query = """
            INSERT INTO Users (full_name, email, password, phone_number)
            VALUES (?, ?, ?, ?);
        """
        cursor.execute(query, (full_name, email, hashed_password.decode('utf-8'), phone_number))
    except pyodbc.IntegrityError:
        raise ValueError("Email already exists or invalid email format")
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise

def login_user(cursor, email, password):
    query = """
        SELECT user_id, full_name, password, is_active FROM Users
        WHERE email = ?;
    """
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')) and user[3] == 1:
        return user
    return None

def book_hotel_for_user(cursor, user_id, hotel_id, date_from, date_to, number_of_guests):
    hotel = get_hotel_by_id(cursor, hotel_id)
    if not hotel:
        raise ValueError("Hotel not found")

    date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
    days = (date_to_dt - date_from_dt).days
    total_price = days * hotel['price_per_night']

    query = """
        INSERT INTO Bookings (user_id, hotel_id, date_from, date_to, total_price, status, number_of_guests)
        VALUES (?, ?, ?, ?, ?, 'Confirmed', ?);
    """
    cursor.execute(query, (user_id, hotel_id, date_from, date_to, total_price, number_of_guests))

def add_review_for_hotel(cursor, user_id, hotel_id, review_text, rating):
    query = """
        INSERT INTO Reviews (user_id, hotel_id, content, rating)
        VALUES (?, ?, ?, ?);
    """
    cursor.execute(query, (user_id, hotel_id, review_text, rating))

def get_reviews_for_hotel(cursor, hotel_id):
    query = """
        SELECT R.review_id, R.user_id, R.content, R.rating, U.full_name
        FROM Reviews R
        JOIN Users U ON R.user_id = U.user_id
        WHERE R.hotel_id = ?;
    """
    cursor.execute(query, (hotel_id,))
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
def search_hotels(cursor, keyword):
    query = """
        SELECT 
            h.hotel_id, h.name, h.description, h.location, h.price_per_night, h.image_url,
            h.star_rating, h.total_rooms, h.average_rating,
            STUFF((
                SELECT ', ' + a2.name
                FROM Amenities a2
                JOIN Hotel_Amenities ha2 ON a2.amenity_id = ha2.amenity_id
                WHERE ha2.hotel_id = h.hotel_id
                FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS amenities
        FROM Hotels h
        WHERE h.name LIKE ? OR h.description LIKE ?;
    """
    pattern = f"%{keyword}%"
    cursor.execute(query, (pattern, pattern))
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_random_hotels(cursor):
    query = """
        SELECT TOP 3 
            h.hotel_id, h.name, h.location, h.description, h.price_per_night, h.image_url,
            h.star_rating, h.total_rooms, h.average_rating,
            STUFF((
                SELECT ', ' + a2.name
                FROM Amenities a2
                JOIN Hotel_Amenities ha2 ON a2.amenity_id = ha2.amenity_id
                WHERE ha2.hotel_id = h.hotel_id
                FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS amenities
        FROM Hotels h
        ORDER BY NEWID();
    """
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_user_bookings(cursor, user_id):
    query = """
        SELECT B.booking_id, B.date_from, B.date_to, B.total_price, B.status, B.number_of_guests,
               H.name, H.price_per_night, H.image_url
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
            phone_number = request.form.get("phone_number", None)
            create_user(cursor, name, email, password, phone_number)
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

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = login_user(cursor, email, password)
        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("home"))
        else:
            return render_template("auth/login.html", error="Invalid credentials or account is inactive")
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
    number_of_guests = int(request.form.get("number_of_guests", 1))

    try:
        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
        if date_to_dt <= date_from_dt:
            return render_template("hotel/hotel_detail.html", 
                                 hotel=get_hotel_by_id(cursor, hotel_id), 
                                 reviews=get_reviews_for_hotel(cursor, hotel_id), 
                                 error="Check-out date must be after check-in date")
        book_hotel_for_user(cursor, user_id, hotel_id, date_from, date_to, number_of_guests)
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
    rating = int(request.form.get("rating", 5))
    try:
        add_review_for_hotel(cursor, user_id, hotel_id, content, rating)
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
        query = "UPDATE Bookings SET status = 'Cancelled' WHERE booking_id = ? AND user_id = ? AND status != 'Cancelled'"
        cursor.execute(query, (booking_id, user_id))
        conn.commit()
        return redirect(url_for("my_bookings"))
    except Exception as e:
        logging.error(f"Cancel booking error: {e}")
        return render_template("booking/my_bookings.html", 
                             bookings=get_user_bookings(cursor, user_id), 
                             error="An error occurred while canceling booking")
def get_all_bookings(cursor):
    query = """
        SELECT B.booking_id, B.date_from, B.date_to, B.total_price, B.status, B.number_of_guests,
               H.name AS hotel_name, U.full_name AS user_name
        FROM Bookings B
        JOIN Hotels H ON B.hotel_id = H.hotel_id
        JOIN Users U ON B.user_id = U.user_id;
    """
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def add_hotel(cursor, name, location, description, price_per_night, image_url, star_rating, total_rooms, contact_number, email, amenities=None):
    query = """
        INSERT INTO Hotels (name, location, description, price_per_night, image_url, star_rating, total_rooms, contact_number, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    cursor.execute(query, (name, location, description, price_per_night, image_url, star_rating, total_rooms, contact_number, email))
    cursor.execute("SELECT @@IDENTITY AS id;")
    hotel_id = int(cursor.fetchone()[0])

    # إذا كانت هناك مرافق (amenities)، أضفها إلى جدول Hotel_Amenities
    if amenities:
        for amenity_id in amenities:
            cursor.execute("INSERT INTO Hotel_Amenities (hotel_id, amenity_id) VALUES (?, ?);", (hotel_id, amenity_id))

def get_all_amenities(cursor):
    query = "SELECT amenity_id, name FROM Amenities;"
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def delete_review_for_hotel(cursor, review_id, user_id):
    query = """
        DELETE FROM Reviews
        WHERE review_id = ? AND user_id = ?;
    """
    cursor.execute(query, (review_id, user_id))
    if cursor.rowcount == 0:
        raise ValueError("Review not found or you do not have permission to delete it")

    # تحديث متوسط التقييم بعد الحذف
    query_avg = """
        UPDATE Hotels
        SET average_rating = (
            SELECT AVG(CAST(rating AS FLOAT))
            FROM Reviews
            WHERE hotel_id = (SELECT hotel_id FROM Reviews WHERE review_id = ?)
        )
        WHERE hotel_id = (SELECT hotel_id FROM Reviews WHERE review_id = ?);
    """
    cursor.execute(query_avg, (review_id, review_id))

def edit_review_for_hotel(cursor, review_id, user_id, review_text, rating):
    query = """
        UPDATE Reviews
        SET content = ?, rating = ?
        WHERE review_id = ? AND user_id = ?;
    """
    cursor.execute(query, (review_text, rating, review_id, user_id))
    if cursor.rowcount == 0:
        raise ValueError("Review not found or you do not have permission to edit it")

    # تحديث متوسط التقييم بعد التعديل
    query_avg = """
        UPDATE Hotels
        SET average_rating = (
            SELECT AVG(CAST(rating AS FLOAT))
            FROM Reviews
            WHERE hotel_id = (SELECT hotel_id FROM Reviews WHERE review_id = ?)
        )
        WHERE hotel_id = (SELECT hotel_id FROM Reviews WHERE review_id = ?);
    """
    cursor.execute(query_avg, (review_id, review_id))
@app.route("/review/<int:hotel_id>/delete/<int:review_id>", methods=["POST"])
def delete_review(hotel_id, review_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    try:
        delete_review_for_hotel(cursor, review_id, user_id)
        conn.commit()
        return redirect(url_for("hotel_detail", hotel_id=hotel_id))
    except ValueError as e:
        return render_template("hotel/hotel_detail.html", 
                             hotel=get_hotel_by_id(cursor, hotel_id), 
                             reviews=get_reviews_for_hotel(cursor, hotel_id), 
                             error=str(e))
    except Exception as e:
        logging.error(f"Delete review error: {e}")
        return render_template("hotel/hotel_detail.html", 
                             hotel=get_hotel_by_id(cursor, hotel_id), 
                             reviews=get_reviews_for_hotel(cursor, hotel_id), 
                             error="An error occurred while deleting the review")

@app.route("/review/<int:hotel_id>/edit/<int:review_id>", methods=["POST"])
def edit_review(hotel_id, review_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    content = request.form["review"]
    rating = int(request.form.get("rating", 5))
    try:
        edit_review_for_hotel(cursor, review_id, user_id, content, rating)
        conn.commit()
        return redirect(url_for("hotel_detail", hotel_id=hotel_id))
    except ValueError as e:
        return render_template("hotel/hotel_detail.html", 
                             hotel=get_hotel_by_id(cursor, hotel_id), 
                             reviews=get_reviews_for_hotel(cursor, hotel_id), 
                             error=str(e))
    except Exception as e:
        logging.error(f"Edit review error: {e}")
        return render_template("hotel/hotel_detail.html", 
                             hotel=get_hotel_by_id(cursor, hotel_id), 
                             reviews=get_reviews_for_hotel(cursor, hotel_id), 
                             error="An error occurred while editing the review")
# ---------- App Run ----------
if __name__ == "__main__":
    app.run(debug=True)