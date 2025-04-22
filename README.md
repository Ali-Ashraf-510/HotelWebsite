# HotelHub - Hotel Booking System



HotelHub is a web-based hotel booking system built with Flask. It allows users to browse hotels, view details, book stays, leave reviews, and manage their bookings. The project includes features like user authentication, payment simulation, and a responsive UI.

## Features
- **Browse Hotels**: View a list of hotels with details like price, amenities, and star ratings.
- **Hotel Details**: See detailed information about each hotel, including descriptions, images, and guest reviews.
- **Booking System**: Book a hotel stay with a maximum duration of 5 days, starting from the current date.
- **Payment Simulation**: Simulated payment process using card details (for testing purposes).
- **User Authentication**: Register, log in, and manage your account.
- **Reviews**: Add, edit, and delete reviews for hotels (for logged-in users).
- **Manage Bookings**: View and cancel your bookings.
- **Responsive Design**: A mobile-friendly interface using Bootstrap and custom CSS.

## Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Database**: SQL Server (using `pyodbc`); can be modified to use SQLite or other databases
- **Authentication**: bcrypt for password hashing
- **Environment Variables**: Managed using `python-dotenv`

## Prerequisites
To run this project locally, you need to have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- SQL Server (or modify the code to use SQLite/PostgreSQL)
- A code editor (like VS Code)

## Installation
Follow these steps to set up and run the project locally:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/hotelhub.git
   cd hotelhub
