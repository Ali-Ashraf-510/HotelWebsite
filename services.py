from datetime import datetime
import logging
import pyodbc
import bcrypt

# جلب كل الفنادق
def get_all_hotels(cursor):
    try:
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
    except Exception as e:
        logging.error(f"Error fetching all hotels: {e}")
        return []

# جلب تفاصيل فندق معيّن
def get_hotel_by_id(cursor, hotel_id):
    try:
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
    except Exception as e:
        logging.error(f"Error fetching hotel {hotel_id}: {e}")
        return None

# تسجيل مستخدم جديد
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

# تسجيل الدخول
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
# حجز فندق
def book_hotel_for_user(cursor, user_id, hotel_id, date_from, date_to, number_of_guests):
    try:
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
    except Exception as e:
        logging.error(f"Error booking hotel: {e}")
        raise

# إضافة مراجعة
def add_review_for_hotel(cursor, user_id, hotel_id, review_text, rating):
    try:
        query = """
            INSERT INTO Reviews (user_id, hotel_id, content, rating)
            VALUES (?, ?, ?, ?);
        """
        cursor.execute(query, (user_id, hotel_id, review_text, rating))
    except Exception as e:
        logging.error(f"Error adding review: {e}")
        raise

# جلب المراجعات لفندق معيّن
def get_reviews_for_hotel(cursor, hotel_id):
    try:
        query = """
            SELECT R.content, R.rating, U.full_name
            FROM Reviews R
            JOIN Users U ON R.user_id = U.user_id
            WHERE R.hotel_id = ? AND R.is_approved = 1;
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
    except Exception as e:
        logging.error(f"Error searching hotels: {e}")
        return []

# جلب فنادق عشوائية
def get_random_hotels(cursor):
    try:
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
    except Exception as e:
        logging.error(f"Error fetching random hotels: {e}")
        return []

# جلب حجوزات المستخدم
def get_user_bookings(cursor, user_id):
    try:
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
    except Exception as e:
        logging.error(f"Error fetching bookings for user {user_id}: {e}")
        return []
    
