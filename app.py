from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
#yarb
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
        return render_template('indexuser.html')
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

    # Check if the email exists in the admins table first
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE email = ? AND password = ?", (email, password))
        admin = cursor.fetchone()

        # If not found in admins, check in users
        if not admin:
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cursor.fetchone()

    if admin:
        session['user_type'] = 'admin'
        return redirect(url_for('index_admin'))
    elif user:
        session['user_type'] = 'user'
        return redirect(url_for('index_user'))
    else:
        return "Invalid login. Please try again."

# Route: Handle Signup
@app.route('/signup', methods=['POST'])
def handle_signup():
    email = request.form.get('email')
    password = request.form.get('pswd')

    # Check if the email contains @admin or @user
    if '@admin' in email:
        table = 'admins'
    elif '@user' in email:
        table = 'users'
    else:
        return "Invalid email. Must contain @admin or @user."

    # Insert data into the appropriate table
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"INSERT INTO {table} (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already exists. Please try again."

# Route: Logout
@app.route('/logout')
def logout():
    session.pop('user_type', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
