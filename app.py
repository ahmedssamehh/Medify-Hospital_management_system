from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "6e6b4e033bb676a25a94401745a7f1deab85c8e1b2b1424e6e92847b528373cb"

def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """)
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

@app.route('/')
def login():
    return render_template('index.html')

@app.route('/indexadmin')
def index_admin():
    if 'user_type' in session and session['user_type'] == 'admin':
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_type' in session and session['user_type'] == 'admin':
        return render_template('profile.html')
    return redirect(url_for('login'))

@app.route('/manage_doctors')
def manage_doctors():
    if 'user_type' in session and session['user_type'] == 'admin':
        return render_template('manage_doctors.html')
    return redirect(url_for('login'))

@app.route('/manage_appointments')
def manage_appointments():
    if 'user_type' in session and session['user_type'] == 'admin':
        return render_template('manage_appointments.html')
    return redirect(url_for('login'))

@app.route('/notifications')
def notifications():
    if 'user_type' in session and session['user_type'] == 'admin':
        return render_template('notifications.html')
    return redirect(url_for('login'))

@app.route('/feedback')
def feedback():
    if 'user_type' in session and session['user_type'] == 'admin':
        return render_template('feedback.html')
    return redirect(url_for('login'))

@app.route('/manage_users')
def manage_users():
    if 'user_type' in session and session['user_type'] == 'admin':
        return render_template('manage_users.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form.get('email')
    password = request.form.get('pswd')

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        # Check if the user is an admin
        cursor.execute("SELECT * FROM admins WHERE email = ? AND password = ?", (email, password))
        admin = cursor.fetchone()
        
        # Check if the user is a regular user
        if not admin:
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cursor.fetchone()
    
    # Redirect based on user type
    if admin:
        session['user_type'] = 'admin'
        session['user_email'] = email
        return redirect(url_for('index_admin'))
    elif user:
        session['user_type'] = 'user'
        session['user_email'] = email
        return redirect(url_for('index_user'))
    else:
        return "Invalid login. Please try again."

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

@app.route('/logout')
def logout():
    session.pop('user_type', None)
    session.pop('user_email', None)
    return redirect(url_for('login'))

@app.route('/indexuser')
def index_user():
    if 'user_type' in session and session['user_type'] == 'user':
        user_email = session.get('user_email')
        appointments = get_appointments(user_email)
        notifications = get_notifications(user_email)
        return render_template('indexuser.html', appointments=appointments, notifications=notifications)
    return redirect(url_for('login'))

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    data = request.get_json()
    doctor = data.get('doctor')
    specialty = data.get('specialty')
    time = data.get('time')
    user_email = session.get('user_email')
    if not user_email:
        return {"success": False, "message": "User not logged in"}, 400
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO appointments (user_email, doctor_name, specialty, time_slot)
        VALUES (?, ?, ?, ?)
        """, (user_email, doctor, specialty, time))
        conn.commit()
    add_to_notifications(user_email, doctor, specialty, time)
    return {"success": True}

def get_appointments(user_email):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_name, specialty, time_slot FROM appointments WHERE user_email = ?", (user_email,))
        appointments = cursor.fetchall()
    return appointments

def get_notifications(user_email):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_name, specialty, time_slot FROM appointments WHERE user_email = ?", (user_email,))
        appointments = cursor.fetchall()
    return [{"message": f"Appointment with Dr. {row[0]} ({row[1]}) at {row[2]}"} for row in appointments]

def add_to_notifications(user_email, doctor, specialty, time):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO appointments (user_email, doctor_name, specialty, time_slot)
        VALUES (?, ?, ?, ?)
        """, (user_email, doctor, specialty, time))
        conn.commit()

if __name__ == "__main__":
    app.run(debug=True)
