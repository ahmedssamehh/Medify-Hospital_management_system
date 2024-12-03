from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# kemo the egyption king

#suiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
# Set secret key for session
app.secret_key = "your_secret_key"

# Initialize database
def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        # Create the users table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """)
        # Create the admins table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """)
        # Create the appointments table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
        """)
    print("Database initialized!")

init_db()

# Route: Login Page
@app.route('/')
def login():
    return render_template('index.html')

# Route: User Dashboard
@app.route('/indexuser')
def index_user():
    if 'user_type' in session and session['user_type'] == 'user':
        # Get user email from session
        user_email = session.get('user_email')
        
        # Get user appointments
        appointments = get_appointments(user_email)
        
        # Get notifications for the user
        notifications = get_notifications(user_email)
        
        return render_template('indexuser.html', appointments=appointments, notifications=notifications)
    return redirect(url_for('login'))

# Route: Admin Dashboard
@app.route('/indexadmin')
def index_admin():
    if 'user_type' in session and session['user_type'] == 'admin':
        return render_template('indexadmin.html')
    return redirect(url_for('login'))

# Route: Handle Login
@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form.get('email')
    password = request.form.get('pswd')

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE email = ? AND password = ?", (email, password))
        admin = cursor.fetchone()

        if not admin:
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cursor.fetchone()

    if admin:
        session['user_type'] = 'admin'
        session['user_email'] = email  # Store email in session
        return redirect(url_for('index_admin'))
    elif user:
        session['user_type'] = 'user'
        session['user_email'] = email  # Store email in session
        return redirect(url_for('index_user'))
    else:
        return "Invalid login. Please try again."

# Route: Handle Signup
@app.route('/signup', methods=['POST'])
def handle_signup():
    email = request.form.get('email')
    password = request.form.get('pswd')

    if '@admin' in email:
        table = 'admins'
    elif '@user' in email:
        table = 'users'
    else:
        return "Invalid email. Must contain @admin or @user."

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"INSERT INTO {table} (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already exists. Please try again."

# Route: Handle Logout
@app.route('/logout')
def logout():
    session.pop('user_type', None)
    session.pop('user_email', None)  # Remove the email from session
    return redirect(url_for('login'))

# Route: Book Appointment
@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    data = request.get_json()
    doctor = data.get('doctor')
    specialty = data.get('specialty')
    time = data.get('time')
    user_email = session.get('user_email')  # Get user's email from session

    if not user_email:
        return {"success": False, "message": "User not logged in"}, 400

    # Insert the appointment into the database
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO appointments (user_email, doctor_name, specialty, time_slot)
        VALUES (?, ?, ?, ?)
        """, (user_email, doctor, specialty, time))
        conn.commit()

    # Add appointment to notifications
    add_to_notifications(user_email, doctor, specialty, time)

    return {"success": True}

# Route: Get Appointments
def get_appointments(user_email):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_name, specialty, time_slot FROM appointments WHERE user_email = ?", (user_email,))
        appointments = cursor.fetchall()
    return appointments

# Route: Get Notifications
def get_notifications(user_email):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_name, specialty, time_slot FROM appointments WHERE user_email = ?", (user_email,))
        appointments = cursor.fetchall()
    return [{"message": f"Appointment with Dr. {row[0]} ({row[1]}) at {row[2]}"} for row in appointments]

# Route: Add Appointment to Notifications
def add_to_notifications(user_email, doctor, specialty, time):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO appointments (user_email, doctor_name, specialty, time_slot)
        VALUES (?, ?, ?, ?)
        """, (user_email, doctor, specialty, time))
        conn.commit()

if __name__ == "_main_":
    app.run(debug=True)
