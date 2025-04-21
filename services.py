import logging
import pyodbc
import bcrypt

# جلب كل الفنادق
def get_all_hotels(cursor):
    try:
        query = """
            SELECT hotel_id, name, description, location, price_per_night, image_url
            FROM Hotels;
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching all hotels: {e}")
        return []

# جلب تفاصيل فندق معيّن
def get_hotel_by_id(cursor, hotel_id):
    try:
        query = """
            SELECT hotel_id, name, description, location, price_per_night, image_url
            FROM Hotels
            WHERE hotel_id = ?;
        """
        cursor.execute(query, (hotel_id,))
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None
    except Exception as e:
        logging.error(f"Error fetching hotel {hotel_id}: {e}")
        return None

# تسجيل مستخدم جديد
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

# تسجيل الدخول
def login_user(cursor, email, password):
    try:
        query = """
            SELECT user_id, full_name, password FROM Users
            WHERE email = ?;
        """
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return user
        return None
    except Exception as e:
        logging.error(f"Error logging in user: {e}")
        return None

# حجز فندق
def book_hotel_for_user(cursor, user_id, hotel_id, date_from, date_to):
    try:
        query = """
            INSERT INTO Bookings (user_id, hotel_id, date_from, date_to)
            VALUES (?, ?, ?, ?);
        """
        cursor.execute(query, (user_id, hotel_id, date_from, date_to))
    except Exception as e:
        logging.error(f"Error booking hotel: {e}")
        raise

# إضافة مراجعة
def add_review_for_hotel(cursor, user_id, hotel_id, review_text):
    try:
        query = """
            INSERT INTO Reviews (user_id, hotel_id, content)
            VALUES (?, ?, ?);
        """
        cursor.execute(query, (user_id, hotel_id, review_text))
    except Exception as e:
        logging.error(f"Error adding review: {e}")
        raise

# جلب المراجعات لفندق معيّن
def get_reviews_for_hotel(cursor, hotel_id):
    try:
        query = """
            SELECT R.content, U.full_name
            FROM Reviews R
            JOIN Users U ON R.user_id = U.user_id
            WHERE R.hotel_id = ?;
        """
        cursor.execute(query, (hotel_id,))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching reviews for hotel {hotel_id}: {e}")
        return []

# بحث عن فنادق بالاسم أو الوصف
def search_hotels(cursor, keyword):
    try:
        query = """
            SELECT hotel_id, name, description, location, price_per_night, image_url
            FROM Hotels
            WHERE name LIKE ? OR description LIKE ?;
        """
        pattern = f"%{keyword}%"
        cursor.execute(query, (pattern, pattern))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error searching hotels: {e}")
        return []

# جلب فنادق عشوائية
def get_random_hotels(cursor):
    try:
        query = """
            SELECT TOP 3 hotel_id, name, location, description, price_per_night, image_url
            FROM Hotels
            ORDER BY NEWID();
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching random hotels: {e}")
        return []

# جلب حجوزات المستخدم
def get_user_bookings(cursor, user_id):
    try:
        query = """
            SELECT B.booking_id, B.date_from, B.date_to, H.name, H.price_per_night, H.image_url
            FROM Bookings B
            JOIN Hotels H ON B.hotel_id = H.hotel_id
            WHERE B.user_id = ?;
        """
        cursor.execute(query, (user_id,))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching bookings for user {user_id}: {e}")
        return []