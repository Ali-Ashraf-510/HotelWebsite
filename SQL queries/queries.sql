CREATE DATABASE HotelBooking;
GO

-- استخدام قاعدة البيانات
USE HotelBooking;
GO

-- جدول المستخدمين
CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    full_name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    password NVARCHAR(100) NOT NULL CHECK (LEN(password) >= 8),
    phone_number NVARCHAR(20) NULL,
    created_at DATETIME DEFAULT GETDATE(),
    is_active BIT DEFAULT 1, -- 1: نشط، 0: غير نشط
    CONSTRAINT CHK_Email_Format CHECK (email LIKE '%_@__%.__%')
);
GO

-- جدول وسائل الراحة
CREATE TABLE Amenities (
    amenity_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL UNIQUE, -- مثل "WiFi", "Pool", "Gym"
    description NVARCHAR(255) NULL
);
GO

-- جدول الفنادق
CREATE TABLE Hotels (
    hotel_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    location NVARCHAR(100) NOT NULL,
    description NVARCHAR(MAX) NULL,
    price_per_night DECIMAL(10, 2) NOT NULL CHECK (price_per_night >= 0),
    image_url NVARCHAR(MAX) NULL,
    star_rating INT CHECK (star_rating BETWEEN 1 AND 5),
    total_rooms INT NOT NULL CHECK (total_rooms > 0),
    contact_number NVARCHAR(20) NULL,
    email NVARCHAR(100) NULL,
    average_rating DECIMAL(3, 2) DEFAULT 0 CHECK (average_rating BETWEEN 0 AND 5),
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT CHK_Hotel_Email CHECK (email IS NULL OR email LIKE '%_@__%.__%')
);
GO

-- جدول ربط وسائل الراحة بالفنادق (علاقة متعدد إلى متعدد)
CREATE TABLE Hotel_Amenities (
    hotel_id INT NOT NULL,
    amenity_id INT NOT NULL,
    PRIMARY KEY (hotel_id, amenity_id),
    CONSTRAINT FK_HotelAmenities_Hotels FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id) ON DELETE CASCADE,
    CONSTRAINT FK_HotelAmenities_Amenities FOREIGN KEY (amenity_id) REFERENCES Amenities(amenity_id) ON DELETE CASCADE
);
GO

-- جدول الحجوزات
CREATE TABLE Bookings (
    booking_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    hotel_id INT NOT NULL,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL CHECK (total_price >= 0),
    status NVARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Confirmed', 'Cancelled', 'Completed')),
    created_at DATETIME DEFAULT GETDATE(),
    number_of_guests INT NOT NULL CHECK (number_of_guests > 0),
    CONSTRAINT FK_Bookings_Users FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FK_Bookings_Hotels FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id) ON DELETE CASCADE,
    CONSTRAINT CHK_Dates CHECK (date_to > date_from)
);
GO

-- جدول المراجعات
CREATE TABLE Reviews (
    review_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    hotel_id INT NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    created_at DATETIME DEFAULT GETDATE(),
    is_approved BIT DEFAULT 0, -- 0: غير معتمد، 1: معتمد
    CONSTRAINT FK_Reviews_Users FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FK_Reviews_Hotels FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id) ON DELETE CASCADE
);
GO

-- إنشاء فهرس لتحسين الأداء
CREATE INDEX IDX_Bookings_UserId ON Bookings(user_id);
CREATE INDEX IDX_Bookings_HotelId ON Bookings(hotel_id);
CREATE INDEX IDX_Reviews_HotelId ON Reviews(hotel_id);
GO

-- Trigger لحساب متوسط التقييمات لكل فندق عند إضافة أو تحديث مراجعة
CREATE TRIGGER UpdateHotelAverageRating
ON Reviews
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    UPDATE Hotels
    SET average_rating = (
        SELECT AVG(CAST(R.rating AS DECIMAL(3, 2)))
        FROM Reviews R
        WHERE R.hotel_id = Hotels.hotel_id AND R.is_approved = 1
    )
    FROM Hotels
    WHERE hotel_id IN (
        SELECT hotel_id FROM inserted
        UNION
        SELECT hotel_id FROM deleted
    );
END;
GO