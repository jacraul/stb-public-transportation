# STB Public Transportation Ticketing System

A web application for managing public transportation tickets, travel cards, and journeys for users and administrators.

---

## Features

### For Users
- **Register/Login/Logout**
- **Travel Card**: View balance, top-up, and see card info
- **Buy Tickets**: Single, daily (24h), or monthly (30 days)
- **Schedule Train Journeys**: Only for train routes, select origin/destination
- **View Scheduled Journeys**: See all your scheduled train journeys with departure time and stations
- **End Journey**: Mark a journey as completed
- **Route Search**: Search routes by mode, station, or time

### For Admins
- **Admin Dashboard**: Overview of users, travel cards, tickets, payments, and journeys
- **Manage Routes & Stops**: Add, edit, delete routes and stops
- **Manage Users, Travel Cards, Tickets, Payments**
- **Buy Tickets/Top-up for Users**
- **Validate Tickets**: 
  - Single tickets are deleted after validation
  - Daily/monthly tickets remain valid until expiry
  - Fancy card shows validation result with user, ticket, and travel card info

---

## Tech Stack

- **Flask** (Python)
- **Flask-SQLAlchemy** (SQLite)
- **Flask-Mail**
- **Jinja2** templates
- **Bootstrap/CSS** for styling

---

## Setup

1. **Clone the repository**
    ```sh
    git clone https://github.com/yourusername/stb-ticketing.git
    cd stb-ticketing
    ```

2. **Create a virtual environment and activate it**
    ```sh
    python -m venv venv
    venv\Scripts\activate   # On Windows
    # or
    source venv/bin/activate  # On Mac/Linux
    ```

3. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the database**
    - The database will be created automatically on first run.

5. **Configure email (optional)**
    - Edit `app.py` with your mail server settings if you want email features.

6. **Run the application**
    ```sh
    python app.py
    ```
    - Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

- **Register** as a user or log in as an admin (set `is_admin=True` in the database for admin accounts).
- **Users** can buy tickets, schedule journeys, and manage their travel card.
- **Admins** can manage all data and validate tickets from the admin dashboard.

---


## License

MIT License

---

## Credits

Developed by [Raul Jac]  
Special thanks to contributors and the open-source community.
