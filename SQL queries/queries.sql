-- إنشاء قاعدة البيانات
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
    password NVARCHAR(100) NOT NULL
);
GO

-- جدول الفنادق
CREATE TABLE Hotels (
    hotel_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100),
    location NVARCHAR(100),
    description NVARCHAR(MAX),
    price_per_night DECIMAL(10, 2),
    image_url NVARCHAR(MAX)
);

GO

-- جدول الحجوزات
CREATE TABLE Bookings (
    booking_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    hotel_id INT NOT NULL,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    CONSTRAINT FK_Bookings_Users FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FK_Bookings_Hotels FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id) ON DELETE CASCADE
);
GO

-- جدول المراجعات
CREATE TABLE Reviews (
    review_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    hotel_id INT NOT NULL,
    content NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Reviews_Users FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FK_Reviews_Hotels FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id) ON DELETE CASCADE
);
GO


