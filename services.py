# جلب كل الفنادق
def get_all_hotels(cursor):
    query = """
        SELECT hotel_id, name, description, location, price_per_night, image_url
        FROM Hotels;
    """
    cursor.execute(query)
    return cursor.fetchall()


# جلب تفاصيل فندق معيّن
def get_hotel_by_id(cursor, hotel_id):
    query = """
        SELECT hotel_id, name, description, location, price_per_night
        FROM Hotels
        WHERE hotel_id = ?;
    """
    cursor.execute(query, hotel_id)
    return cursor.fetchone()

# تسجيل مستخدم جديد
def create_user(cursor, full_name, email, password):
    query = """
        INSERT INTO Users (full_name, email, password)
        VALUES (?, ?, ?);
    """
    cursor.execute(query, (full_name, email, password))

# تسجيل الدخول
def login_user(cursor, email, password):
    query = """
        SELECT user_id, full_name FROM Users
        WHERE email = ? AND password = ?;
    """
    cursor.execute(query, (email, password))
    return cursor.fetchone()

# حجز فندق
def book_hotel_for_user(cursor, user_id, hotel_id, date_from, date_to):
    query = """
        INSERT INTO Bookings (user_id, hotel_id, date_from, date_to)
        VALUES (?, ?, ?, ?);
    """
    cursor.execute(query, (user_id, hotel_id, date_from, date_to))

# إضافة مراجعة
def add_review_for_hotel(cursor, user_id, hotel_id, review_text):
    query = """
        INSERT INTO Reviews (user_id, hotel_id, content)
        VALUES (?, ?, ?);
    """
    cursor.execute(query, (user_id, hotel_id, review_text))

# جلب المراجعات لفندق معيّن
def get_reviews_for_hotel(cursor, hotel_id):
    query = """
        SELECT R.content, U.full_name
        FROM Reviews R
        JOIN Users U ON R.user_id = U.user_id
        WHERE R.hotel_id = ?;
    """
    cursor.execute(query, hotel_id)
    return cursor.fetchall()

# بحث عن فنادق بالاسم أو الوصف
def search_hotels(cursor, keyword):
    query = """
        SELECT hotel_id, name, description, location, price_per_night, image_url
        FROM Hotels
        WHERE name LIKE ? OR description LIKE ?;
    """
    pattern = f"%{keyword}%"
    cursor.execute(query, (pattern, pattern))
    return cursor.fetchall()

# جلب فنادق عشوائية
def get_random_hotels(cursor):
    query = """
        SELECT TOP 3 hotel_id, name, location, description, price_per_night, image_url
        FROM Hotels
        ORDER BY NEWID();  -- NEWID() دي بتخلي النتائج عشوائية
    """
    cursor.execute(query)
    return cursor.fetchall()
