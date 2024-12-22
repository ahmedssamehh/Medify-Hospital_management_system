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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS phone_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            phone_number TEXT,
            FOREIGN KEY (email) REFERENCES admins (email)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            salary REAL NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications  (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            suggestion TEXT NOT NULL,
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
        admin_email = session.get('user_email')
        
        # Extract the part before '@' from the email
        admin_name = admin_email.split('@')[0]
        
        return render_template('home.html', admin_name=admin_name)
    
    return redirect(url_for('login'))




@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_type' in session and session['user_type'] in ['admin', 'user']:
        user_email = session.get('user_email')
        if not user_email:
            return redirect(url_for('login'))

        user_name = user_email.split('@')[0]

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT phone_number FROM phone_numbers WHERE email = ?", (user_email,))
            phone_data = cursor.fetchone()
            phone_number = phone_data[0] if phone_data else ""

        if request.method == 'POST':
            new_phone = request.form.get('phone')
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO phone_numbers (email, phone_number)
                VALUES (?, ?)
                ON CONFLICT(email) DO UPDATE SET phone_number=excluded.phone_number
                """, (user_email, new_phone))
                conn.commit()
            return redirect(url_for('profile'))

        return render_template('indexuser.html', user_name=user_name, phone_number=phone_number)

    return redirect(url_for('login'))





@app.route('/manage_doctors')
def manage_doctors():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, id, specialization, salary FROM doctors")
            doctors = cursor.fetchall()
        return render_template('manage_doctors.html', doctors=doctors)
    return redirect(url_for('login'))

@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    if 'user_type' in session and session['user_type'] == 'admin':
        doctor_name = request.form.get('doctor_name')
        specialization = request.form.get('specialization')
        salary = request.form.get('salary')
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO doctors (name, specialization, salary) VALUES (?, ?, ?)", (doctor_name, specialization, salary))
            conn.commit()
        return redirect(url_for('manage_doctors'))
    return redirect(url_for('login'))


@app.route('/delete_doctor', methods=['POST'])
def delete_doctor():
    if 'user_type' in session and session['user_type'] == 'admin':
        doctor_id = request.form.get('doctor_id')
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
            conn.commit()
        return redirect(url_for('manage_doctors'))
    return redirect(url_for('login'))


@app.route('/send_notification', methods=['POST'])
def send_notification():
    user_email = request.form.get('user_email')
    message = request.form.get('message')

    if '@user.com' not in user_email:
        return {"success": False, "message": "Invalid user email"}, 400

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (user_email, message)
            VALUES (?, ?)
        """, (user_email, message))
        conn.commit()
    return {"success": True, "message": "Notification sent successfully"}



@app.route('/manage_appointments')
def manage_appointments():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT appointments.doctor_name, users.email, appointments.time_slot 
                FROM appointments
                INNER JOIN users ON appointments.user_email = users.email
            """)
            appointments = cursor.fetchall()
        return render_template('manage_appointments.html', appointments=appointments)
    return redirect(url_for('login'))


@app.route('/notifications')
def notifications():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE email LIKE '%@user.com%'")
            users = cursor.fetchall()

            cursor.execute("SELECT user_email, message FROM notifications")
            notifications = cursor.fetchall()

        return render_template('notifications.html', users=users, notifications=notifications)
    return redirect(url_for('login'))


@app.route('/feedback')
def feedback():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_email, suggestion FROM suggestions")
            suggestions = cursor.fetchall()
        return render_template('feedback.html', suggestions=suggestions)
    return redirect(url_for('login'))





@app.route('/manage_users')
def manage_users():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            # Fetch all users along with their phone numbers (if available)
            cursor.execute("""
                SELECT u.id, u.email, pn.phone_number
                FROM users u
                LEFT JOIN phone_numbers pn ON u.email = pn.email
            """)
            users = cursor.fetchall()
        return render_template('manage_users.html', users=users)
    return redirect(url_for('login'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'user_type' in session and session['user_type'] == 'admin':
        user_id = request.form.get('user_id')
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        return redirect(url_for('manage_users'))
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
        if not user_email:  
            return redirect(url_for('login'))

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doctor_name, specialty, time_slot FROM appointments WHERE user_email = ?", (user_email,))
            appointments = cursor.fetchall()
            cursor.execute("SELECT message FROM notifications WHERE user_email = ?", (user_email,))
            notifications = cursor.fetchall()
            cursor.execute("SELECT name, specialization FROM doctors")
            doctors = cursor.fetchall()

        return render_template(
            'indexuser.html',
            appointments=appointments,
            notifications=notifications,
            doctors=doctors
        )
    return redirect(url_for('login'))

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user_type' in session and session['user_type'] == 'user':
        data = request.get_json()
        doctor_name = data.get('doctor')
        specialty = data.get('specialty')
        time_slot = data.get('time')
        user_email = session.get('user_email')

        if not doctor_name or not specialty or not time_slot:
            return {"success": False, "message": "Missing appointment details"}, 400

        # Insert appointment into the database
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO appointments (user_email, doctor_name, specialty, time_slot)
                VALUES (?, ?, ?, ?)
            """, (user_email, doctor_name, specialty, time_slot))
            conn.commit()

        return {"success": True, "message": "Appointment booked successfully!"}
    return {"success": False, "message": "User not authenticated"}, 403




@app.route('/submit_suggestions', methods=['POST'])
def submit_suggestions():
    if 'user_email' not in session:
        return {"success": False, "message": "User not logged in"}, 401

    suggestion = request.form.get('suggestions')
    user_email = session.get('user_email')

    if not suggestion.strip():
        return {"success": False, "message": "Suggestion cannot be empty!"}, 400

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO suggestions (user_email, suggestion) VALUES (?, ?)
        """, (user_email, suggestion))
        conn.commit()

    return {"success": True, "message": "Thank you for your suggestion!"}



def get_appointments(user_email):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_name, specialty, time_slot FROM appointments WHERE user_email = ?", (user_email,))
        appointments = cursor.fetchall()
    return appointments

@app.route('/get_doctors')
def get_doctors():
    if 'user_type' in session and session['user_type'] == 'user':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, specialization FROM doctors")
            doctors = cursor.fetchall()
        return render_template('indexuser.html', doctors=doctors)
    return redirect(url_for('login'))

@app.route('/get_notifications')
def get_notifications():
    if 'user_type' in session and session['user_type'] == 'user':
        user_email = session.get('user_email')
        if not user_email:  
            return redirect(url_for('login'))

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT message FROM notifications WHERE user_email = ?", (user_email,))
            notifications = cursor.fetchall()

        return render_template('indexuser.html', notifications=notifications)
    return redirect(url_for('login'))

@app.route('/submit_suggestions', methods=['POST'])
def submit_suggestions():
    if 'user_email' not in session:
        return {"success": False, "message": "User not logged in"}, 401

    suggestion = request.form.get('suggestions')
    user_email = session.get('user_email')

    if not suggestion.strip():
        return {"success": False, "message": "Suggestion cannot be empty!"}, 400

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO suggestions (user_email, suggestion) VALUES (?, ?)
        """, (user_email, suggestion))
        conn.commit()

    return {"success": True, "message": "Thank you for your suggestion!"}


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
