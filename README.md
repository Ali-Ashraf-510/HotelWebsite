# 🏨 HotelHub – Hotel Booking System

![HotelHub Logo](static/images/logo.png)  
<sub><i>*(Optional: Add a logo for branding)*</i></sub>

**HotelHub** is a modern, web-based hotel booking platform built with **Flask**. It allows users to browse hotels, view details, make reservations, leave reviews, and manage their bookings — all through a responsive and user-friendly interface.

---

## 🚀 Features

- 🔍 **Browse Hotels** – View hotel listings with price, amenities, and star ratings.  
- 🏨 **Hotel Details** – Get in-depth hotel info including descriptions, images, and reviews.  
- 📅 **Booking System** – Book your stay (max 5 days) starting from the current date.  
- 💳 **Payment Simulation** – Simulated checkout with test card input.  
- 🔐 **User Authentication** – Secure login and registration with password hashing.  
- ✍️ **Hotel Reviews** – Add, update, and delete reviews (only for logged-in users).  
- 📂 **Manage Bookings** – Track or cancel your reservations.  
- 📱 **Responsive Design** – Fully mobile-friendly UI using **Bootstrap** and custom CSS.

---

## 🧰 Tech Stack

| Layer         | Tools / Libraries                     |
|---------------|----------------------------------------|
| Backend       | `Flask` (Python)                       |
| Frontend      | HTML, CSS (Bootstrap), JavaScript      |
| Database      | SQL Server via `pyodbc` (can switch to SQLite/PostgreSQL) |
| Auth & Security | `bcrypt`, `python-dotenv`            |
| Deployment    | `gunicorn` (optional for production)   |

---

## 🗂 Project Structure

hotelhub/ │ 
   ├── app.py # Main Flask application 
   ├── requirements.txt # List of Python dependencies 
   ├── services.py # Helper functions (e.g., DB connection) │ 
   ├── static/ # Static assets │ 
      ├── css/ │ │
         ├── navbar.css │ │ 
         ├── hotel_detail.css │ 
         │ └── my_bookings.css │
      ├── js/ │
      └── images/ │
   ├── templates/ # HTML templates │ 
   ├── navbar/ │ 
      │ └── navbar.html │
   ├── hotel/ │ │
      └── hotel_detail.html │ 
         ├── my_bookings.html │ ├── home.html │ ├── login.html │ └── register.html │ ├── SQL queries/ # SQL scripts for DB setup (optional) ├── .gitignore # Files to ignore in Git └── README.md # Project documentation


---

## 🛠 Prerequisites

Before you begin, make sure you have the following installed:

- 🐍 **Python 3.7+** (Python 3.9+ recommended)
- 📦 **pip** – Python package manager
- 🗃 **SQL Server** (or modify code to use SQLite/PostgreSQL)
- 🧪 **Git** – To clone the repository
- 💻 Code editor – VS Code or PyCharm recommended

---

## ⚙️ Installation & Setup

Follow these steps to run the project locally:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hotelhub.git
cd hotelhub
```
### 2. Create a Virtual Environment

   - Windows
     - python -m venv venv
      -venv\Scripts\activate

  -  macOS/Linux
      -python3 -m venv venv
      -source venv/bin/activate

### 3. Install Dependencies
-pip install -r requirements.txt

### 4. Set Up the Database
-Run the provided SQL scripts inside the SQL queries/ folder to create and configure the database schema.

### 5. Run the Application
- python app.py

