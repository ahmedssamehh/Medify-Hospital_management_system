from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "6e6b4e033bb676a25a94401745a7f1deab85c8e1b2b1424e6e92847b528373cb"

def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            full_name TEXT,
            address TEXT,
            date_of_birth TEXT
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
            phone_number TEXT
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
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            message TEXT NOT NULL,
            title TEXT DEFAULT 'Notification',
            is_read INTEGER DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
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

def update_db_schema():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        # Check if full_name column exists in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns to users table if they don't exist
        if 'full_name' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            print("Added full_name column to users table")
            
        if 'address' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
            print("Added address column to users table")
            
        if 'date_of_birth' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth TEXT")
            print("Added date_of_birth column to users table")
            
        if 'profile_image' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT DEFAULT '/static/images/avatar.jpg'")
            print("Added profile_image column to users table")
        
        # Check if admin_full_name and admin_phone columns exist in admins table
        cursor.execute("PRAGMA table_info(admins)")
        admin_columns = [column[1] for column in cursor.fetchall()]
        
        if 'admin_full_name' not in admin_columns:
            cursor.execute("ALTER TABLE admins ADD COLUMN admin_full_name TEXT")
            print("Added admin_full_name column to admins table")
            
        if 'admin_phone' not in admin_columns:
            cursor.execute("ALTER TABLE admins ADD COLUMN admin_phone TEXT")
            print("Added admin_phone column to admins table")
        
        # Check if profile_image column exists in admins table
        if 'profile_image' not in admin_columns:
            cursor.execute("ALTER TABLE admins ADD COLUMN profile_image TEXT DEFAULT '/static/images/avatar.jpg'")
            print("Added profile_image column to admins table")
        
        # Check if phone_numbers table has a foreign key constraint
        cursor.execute("PRAGMA foreign_key_list(phone_numbers)")
        foreign_keys = cursor.fetchall()
        
        if foreign_keys:
            # Backup current phone numbers
            cursor.execute("SELECT email, phone_number FROM phone_numbers")
            phone_data = cursor.fetchall()
            
            # Drop and recreate the table without foreign key constraint
            cursor.execute("DROP TABLE phone_numbers")
            cursor.execute("""
            CREATE TABLE phone_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                phone_number TEXT
            )
            """)
            
            # Restore phone numbers
            for email, phone in phone_data:
                cursor.execute("INSERT INTO phone_numbers (email, phone_number) VALUES (?, ?)", 
                              (email, phone))
            
            print("Updated phone_numbers table to remove foreign key constraint")
        
        # Check if appointments table has the needed columns
        cursor.execute("PRAGMA table_info(appointments)")
        app_columns = [column[1] for column in cursor.fetchall()]
        
        if 'date' not in app_columns:
            cursor.execute("ALTER TABLE appointments ADD COLUMN date TEXT")
            print("Added date column to appointments table")
            
        if 'status' not in app_columns:
            cursor.execute("ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'pending'")
            print("Added status column to appointments table")
        
        # Check if doctors table has all needed columns
        cursor.execute("PRAGMA table_info(doctors)")
        doc_columns = [column[1] for column in cursor.fetchall()]
        
        if 'specialty' not in doc_columns:
            cursor.execute("ALTER TABLE doctors ADD COLUMN specialty TEXT")
            print("Added specialty column to doctors table")
            
        if 'rating' not in doc_columns:
            cursor.execute("ALTER TABLE doctors ADD COLUMN rating INTEGER DEFAULT 5")
            print("Added rating column to doctors table")
            
        if 'img' not in doc_columns:
            cursor.execute("ALTER TABLE doctors ADD COLUMN img TEXT DEFAULT '/static/images/doctor.jpg'")
            print("Added img column to doctors table")
            
        if 'description' not in doc_columns:
            cursor.execute("ALTER TABLE doctors ADD COLUMN description TEXT")
            print("Added description column to doctors table")
            
        if 'availability' not in doc_columns:
            cursor.execute("ALTER TABLE doctors ADD COLUMN availability TEXT DEFAULT 'yes'")
            print("Added availability column to doctors table")
            
        if 'phone' not in doc_columns:
            cursor.execute("ALTER TABLE doctors ADD COLUMN phone TEXT")
            print("Added phone column to doctors table")
            
        if 'experience' not in doc_columns:
            cursor.execute("ALTER TABLE doctors ADD COLUMN experience INTEGER DEFAULT 0")
            print("Added experience column to doctors table")
            
        if 'email' not in doc_columns:
            cursor.execute("ALTER TABLE doctors ADD COLUMN email TEXT")
            print("Added email column to doctors table")
            
        # Update notifications table or create it if needed
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT DEFAULT 'Notification',
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user_email TEXT
            )
        """)
        print("Created/Updated notifications table")
        
        # Create feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                rating INTEGER DEFAULT 3,
                date TEXT DEFAULT CURRENT_DATE,
                comment TEXT NOT NULL
            )
        """)
        print("Created/Updated feedback table")
        
        # Add some sample feedback if the table is empty
        cursor.execute("SELECT COUNT(*) FROM feedback")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO feedback (user_email, rating, comment)
                VALUES 
                ('user1@user.com', 5, 'Great experience with the doctors!'),
                ('user2@user.com', 4, 'The hospital is well maintained and clean.'),
                ('user3@user.com', 2, 'Had to wait too long for my appointment.')
            """)
            print("Added sample feedback data")
        
        conn.commit()
    
    print("Database schema updated!")

init_db()
update_db_schema()  # Run schema update on startup

@app.route('/debug_notification')
def debug_notification():
    try:
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(notifications)")
            columns_info = cursor.fetchall()
            columns = [column[1] for column in columns_info]
            
            cursor.execute("SELECT * FROM notifications LIMIT 5")
            notifications = cursor.fetchall()
            
            return {
                "columns": columns,
                "data": [list(n) for n in notifications]
            }
    except Exception as e:
        return {"error": str(e)}
        
@app.route('/')
def login():
    return render_template('index.html')

@app.route('/indexadmin')
def index_admin():
    if 'user_type' in session and session['user_type'] == 'admin':
        # Get current date info for the footer
        now = datetime.now()
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            try:
                # Get admin username from email
                admin_email = session.get('user_email')
                admin_name = admin_email.split('@')[0] if admin_email else 'Admin'
                
                # Get statistics for dashboard
                # Count total doctors
                total_doctors = 0
                total_appointments = 0
                total_users = 0
                total_feedback = 0
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM doctors")
                    total_doctors = cursor.fetchone()[0]
                except Exception as e:
                    print(f"Error counting doctors: {e}")
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM appointments")
                    total_appointments = cursor.fetchone()[0]
                except Exception as e:
                    print(f"Error counting appointments: {e}")
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM users")
                    total_users = cursor.fetchone()[0]
                except Exception as e:
                    print(f"Error counting users: {e}")
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM feedback")
                    total_feedback = cursor.fetchone()[0]
                except Exception as e:
                    print(f"Error counting feedback: {e}")
                
                # Get recent appointments for dashboard
                recent_appointments = []
                try:
                    cursor.execute("""
                        SELECT users.email, appointments.doctor_name, 
                                appointments.date, appointments.status
                        FROM appointments 
                        JOIN users ON appointments.user_email = users.email
                        ORDER BY appointments.date DESC, appointments.time_slot DESC
                        LIMIT 5
                    """)
                    recent_appointments = cursor.fetchall()
                except Exception as e:
                    print(f"Error fetching recent appointments: {e}")
                
                return render_template('home.html', 
                                     session=session,
                                     admin_name=admin_name,
                                     now=now,
                                     total_doctors=total_doctors,
                                     total_appointments=total_appointments,
                                     total_users=total_users,
                                     total_feedback=total_feedback,
                                     recent_appointments=recent_appointments)
            except Exception as e:
                print(f"Error in indexadmin route: {e}")
                return f"An error occurred: {e}"
    
    return redirect(url_for('login'))




@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_type' in session and session['user_type'] in ['admin', 'user']:
        user_email = session.get('user_email')
        if not user_email:
            return redirect(url_for('login'))

        user_name = user_email.split('@')[0]
        user_table = 'admins' if session['user_type'] == 'admin' else 'users'

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            # Get phone number
            cursor.execute("SELECT phone_number FROM phone_numbers WHERE email = ?", (user_email,))
            phone_data = cursor.fetchone()
            phone_number = phone_data[0] if phone_data else ""
            
            # Get additional profile info if user
            full_name = ""
            address = ""
            date_of_birth = ""
            
            if session['user_type'] == 'user':
                cursor.execute("SELECT full_name, address, date_of_birth FROM users WHERE email = ?", (user_email,))
                user_data = cursor.fetchone()
                if user_data:
                    full_name = user_data[0] or ""
                    address = user_data[1] or ""
                    date_of_birth = user_data[2] or ""
            else:
                # For admin users
                cursor.execute("SELECT admin_full_name, admin_phone FROM admins WHERE email = ?", (user_email,))
                admin_data = cursor.fetchone()
                if admin_data:
                    full_name = admin_data[0] or ""
                    # Update phone_number if admin has a specific phone field
                    if admin_data[1]:
                        phone_number = admin_data[1]

        if request.method == 'POST':
            new_phone = request.form.get('phone')
            
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                # Update phone number
                cursor.execute("""
                INSERT INTO phone_numbers (email, phone_number)
                VALUES (?, ?)
                ON CONFLICT(email) DO UPDATE SET phone_number=excluded.phone_number
                """, (user_email, new_phone))
                
                # Update additional profile info if user
                if session['user_type'] == 'user':
                    new_full_name = request.form.get('full_name')
                    new_address = request.form.get('address')
                    new_date_of_birth = request.form.get('date_of_birth')
                    
                    cursor.execute("""
                    UPDATE users 
                    SET full_name = ?, address = ?, date_of_birth = ?
                    WHERE email = ?
                    """, (new_full_name, new_address, new_date_of_birth, user_email))
                else:
                    # For admin users, update their data too
                    new_full_name = request.form.get('full_name', '')
                    cursor.execute("""
                    UPDATE admins 
                    SET admin_full_name = ?, admin_phone = ?
                    WHERE email = ?
                    """, (new_full_name, new_phone, user_email))
                
                conn.commit()
            
            return redirect(url_for('profile'))

        return render_template('profile.html', 
                             user_name=user_name,
                             phone_number=phone_number,
                             full_name=full_name,
                             address=address,
                             date_of_birth=date_of_birth,
                             user_type=session['user_type'])

    return redirect(url_for('login'))





@app.route('/manage_doctors')
def manage_doctors():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            # Fetch all doctors with detailed information
            cursor.execute("""
                SELECT id, name, specialization, rating, img, description, 
                       availability, phone, experience, email, salary
                FROM doctors
                ORDER BY id
            """)
            doctors = cursor.fetchall()
            
            # Calculate available doctors
            available_now = sum(1 for doctor in doctors if doctor[6] == 'yes')
            
            # Extract unique specialties
            specialties = sorted(set(doctor[2] for doctor in doctors if doctor[2]))
            
        return render_template('manage_doctors.html', 
                              doctors=doctors,
                              available_now=available_now,
                              specialties=specialties)
    return redirect(url_for('login'))

@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    if 'user_type' in session and session['user_type'] == 'admin':
        name = request.form.get('name')
        specialty = request.form.get('specialty')
        rating = request.form.get('rating', 5)
        img = request.form.get('img', '/static/images/doctor.jpg')
        description = request.form.get('desc', '')
        availability = request.form.get('available', 'yes')
        phone = request.form.get('phone', '')
        experience = request.form.get('experience', 0)
        email = request.form.get('email', '')
        salary = request.form.get('salary', 0)
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO doctors (name, specialization, rating, img, description, 
                                    availability, phone, experience, email, salary) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, specialty, rating, img, description, availability, phone, experience, email, salary))
            conn.commit()
        return redirect(url_for('manage_doctors'))
    return redirect(url_for('login'))

@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    if 'user_type' in session and session['user_type'] == 'admin':
        doctor_id = request.form.get('id')
        name = request.form.get('name')
        specialty = request.form.get('specialty')
        rating = request.form.get('rating')
        img = request.form.get('img')
        description = request.form.get('desc')
        availability = request.form.get('available')
        phone = request.form.get('phone')
        experience = request.form.get('experience')
        email = request.form.get('email')
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE doctors 
                SET name=?, specialty=?, rating=?, img=?, description=?, 
                    availability=?, phone=?, experience=?, email=?
                WHERE id=?
            """, (name, specialty, rating, img, description, availability, phone, experience, email, doctor_id))
            conn.commit()
        return redirect(url_for('manage_doctors'))
    return redirect(url_for('login'))

@app.route('/delete_doctor/<int:id>', methods=['GET', 'POST'])
def delete_doctor(id):
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM doctors WHERE id = ?", (id,))
            conn.commit()
        return redirect(url_for('manage_doctors'))
    return redirect(url_for('login'))


@app.route('/send_notification', methods=['POST'])
def send_notification():
    if 'user_type' in session and session['user_type'] == 'admin':
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            user_email = data.get('user_email')
            title = data.get('title', 'Notification')
            message = data.get('message')
            send_to_all = data.get('send_to_all', False)
        else:
            user_email = request.form.get('user_email')
            title = request.form.get('title', 'Notification')
            message = request.form.get('message')
            send_to_all = request.form.get('send_to_all') == 'true'

        if (not user_email and not send_to_all) or not message:
            return {"success": False, "message": "Missing required fields"}, 400

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            if send_to_all:
                # Get all user emails
                cursor.execute("SELECT email FROM users")
                users = cursor.fetchall()
                
                # Insert notifications for all users
                for user in users:
                    cursor.execute("""
                        INSERT INTO notifications (user_email, title, message)
                        VALUES (?, ?, ?)
                    """, (user[0], title, message))
            else:
                # Insert notification for single user
                cursor.execute("""
                    INSERT INTO notifications (user_email, title, message)
                    VALUES (?, ?, ?)
                """, (user_email, title, message))
            
            conn.commit()
            
        return {"success": True, "message": "Notification sent successfully"}
    return {"success": False, "message": "Unauthorized access"}, 401



@app.route('/manage_appointments')
def manage_appointments():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            # Get appointments with detailed info
            cursor.execute("""
                SELECT appointments.id, users.email, appointments.doctor_name, 
                       appointments.date, appointments.time_slot, appointments.status
                FROM appointments
                INNER JOIN users ON appointments.user_email = users.email
                ORDER BY appointments.date DESC, appointments.time_slot ASC
            """)
            appointments = cursor.fetchall()
            
        return render_template('manage_appointments.html', 
                              appointments=appointments)
    return redirect(url_for('login'))

@app.route('/update_appointment_status/<int:id>/<string:status>')
def update_appointment_status(id, status):
    if 'user_type' in session and session['user_type'] == 'admin':
        if status in ['pending', 'confirmed', 'cancelled', 'completed']:
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, id))
                conn.commit()
        return redirect(url_for('manage_appointments'))
    return redirect(url_for('login'))

@app.route('/send_notifications')
def send_notifications():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            # Get all users for sending notifications
            cursor.execute("SELECT id, email, full_name FROM users")
            all_users = cursor.fetchall()
            
            # Format user data for display
            formatted_users = []
            for user in all_users:
                user_id = user[0]
                email = user[1]
                full_name = user[2] or email.split('@')[0]
                # Format as username@user.com
                display_name = f"{full_name}...{email}"
                formatted_users.append((user_id, email, display_name))
            
            # Check if notifications table has title column
            cursor.execute("PRAGMA table_info(notifications)")
            columns = [column[1] for column in cursor.fetchall()]
            has_title_column = 'title' in columns
            
            # Get recent notifications to display
            if has_title_column:
                cursor.execute("""
                    SELECT id, user_email, title, message, is_read, timestamp 
                    FROM notifications 
                    ORDER BY timestamp DESC LIMIT 10
                """)
            else:
                cursor.execute("""
                    SELECT id, user_email, 'Notification' as title, message, is_read, timestamp 
                    FROM notifications 
                    ORDER BY timestamp DESC LIMIT 10
                """)
            
            recent_notifications = cursor.fetchall()
            
            # Current date for footer
            now = datetime.now()
            
        return render_template('notifications.html', 
                              all_users=formatted_users,
                              recent_notifications=recent_notifications,
                              now=now)
    return redirect(url_for('login'))

@app.route('/mark_as_read/<int:id>')
def mark_as_read(id):
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (id,))
            conn.commit()
        return redirect(url_for('send_notifications'))
    return redirect(url_for('login'))

@app.route('/mark_all_as_read')
def mark_all_as_read():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = 1")
            conn.commit()
        return redirect(url_for('send_notifications'))
    return redirect(url_for('login'))

@app.route('/delete_notification/<int:id>')
def delete_notification(id):
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications WHERE id = ?", (id,))
            conn.commit()
        return redirect(url_for('send_notifications'))
    return redirect(url_for('login'))

@app.route('/clear_all_notifications')
def clear_all_notifications():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications")
            conn.commit()
        return redirect(url_for('send_notifications'))
    return redirect(url_for('login'))

@app.route('/feedback')
def feedback():
    if 'user_type' in session and session['user_type'] == 'admin':
        now = datetime.now()
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            # Get all feedback with user email, rating, date, and comment
            cursor.execute("""
                SELECT f.id, f.user_email, f.rating, f.date, f.comment, u.full_name
                FROM feedback f
                LEFT JOIN users u ON f.user_email = u.email
                ORDER BY f.date DESC
            """)
            feedback_entries = cursor.fetchall()
            
            # Also get suggestions from users (another form of feedback)
            cursor.execute("""
                SELECT s.id, s.user_email, 3 as rating, CURRENT_DATE as date, s.suggestion as comment, u.full_name
                FROM suggestions s
                LEFT JOIN users u ON s.user_email = u.email
                ORDER BY s.id DESC
            """)
            suggestions = cursor.fetchall()
            
            # Combine both types of feedback
            combined_feedback = feedback_entries + suggestions
            
            # Sort by date (newest first)
            combined_feedback.sort(key=lambda x: x[3] if x[3] else "", reverse=True)
            
            # Count positive (rating >= 3) and negative feedback
            positive_count = sum(1 for fb in combined_feedback if fb[2] >= 3)
            negative_count = len(combined_feedback) - positive_count
            
        return render_template('feedback.html', 
                             feedback=combined_feedback,
                             positive_count=positive_count,
                             negative_count=negative_count,
                             now=now)
    return redirect(url_for('login'))

@app.route('/delete_feedback/<int:id>', methods=['GET'])
def delete_feedback(id):
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback WHERE id = ?", (id,))
            conn.commit()
        return redirect(url_for('feedback'))
    return redirect(url_for('login'))

@app.route('/send_feedback_reply', methods=['POST'])
def send_feedback_reply():
    data = request.json
    user_email = data.get('user_email')
    reply_message = data.get('reply_message')

    if not user_email or not reply_message:
        return {"success": False, "message": "Invalid data"}, 400

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (user_email, message)
            VALUES (?, ?)
        """, (user_email, reply_message))
        conn.commit()

    return {"success": True, "message": "Reply sent successfully"}





@app.route('/manage_users')
def manage_users():
    if 'user_type' in session and session['user_type'] == 'admin':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            
            # Fetch all users with detailed information
            cursor.execute("""
                SELECT u.id, u.email, u.full_name, u.address, u.date_of_birth, pn.phone_number
                FROM users u
                LEFT JOIN phone_numbers pn ON u.email = pn.email
                ORDER BY u.id DESC
            """)
            users = cursor.fetchall()
            
            # Current date for footer
            now = datetime.now()
            
        return render_template('manage_users.html', 
                              users=users,
                              now=now)
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
    doctor_value = request.form.get('doctor')
    
    # Determine if admin or user based on doctor value
    if doctor_value == '2':  # Admin option
        table = 'admins'
    else:  # Normal user option
        table = 'users'
    
    # Add the appropriate suffix to the email
    if '@admin' not in email and '@user' not in email:
        email_name = email.split('@')[0]
        email_domain = email.split('@')[1] if '@' in email else 'example.com'
        
        if table == 'admins':
            email = f"{email_name}@admin.{email_domain}"
        else:
            email = f"{email_name}@user.{email_domain}"
    
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        try:
            # Get username from form
            username = request.form.get('txt')
            
            # Insert user with full name from username
            if table == 'users':
                cursor.execute(f"INSERT INTO {table} (email, password, full_name) VALUES (?, ?, ?)", 
                              (email, password, username))
            else:
                cursor.execute(f"INSERT INTO {table} (email, password, admin_full_name) VALUES (?, ?, ?)", 
                              (email, password, username))
            
            # Initialize phone number record for the new user
            cursor.execute("INSERT INTO phone_numbers (email, phone_number) VALUES (?, ?)", (email, ""))
            
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

        # Extract username from email
        user_name = user_email.split('@')[0]

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doctor_name, specialty, time_slot FROM appointments WHERE user_email = ?", (user_email,))
            appointments = cursor.fetchall()
            
            # Get notifications with ID and creation timestamp
            cursor.execute("SELECT id, message, datetime('now', '-' || (ABS(RANDOM()) % 30) || ' days') AS timestamp FROM notifications WHERE user_email = ? ORDER BY timestamp DESC", (user_email,))
            notification_data = cursor.fetchall()
            
            # Format notifications for display
            formatted_notifications = []
            for notif in notification_data:
                notif_id = notif[0]
                message = notif[1]
                timestamp = notif[2]
                
                # Determine notification type based on content
                icon_class = "fa-bell"
                bg_class = "primary"
                title = "Notification"
                
                if "appointment" in message.lower() and "scheduled" in message.lower():
                    icon_class = "fa-calendar-check"
                    bg_class = "primary"
                    title = "Appointment Confirmation"
                elif "appointment" in message.lower() and "cancelled" in message.lower():
                    icon_class = "fa-calendar-times"
                    bg_class = "danger"
                    title = "Appointment Cancelled"
                elif "test results" in message.lower():
                    icon_class = "fa-flask"
                    bg_class = "success"
                    title = "Test Results"
                elif "prescription" in message.lower():
                    icon_class = "fa-prescription-bottle-alt"
                    bg_class = "warning"
                    title = "Prescription"
                elif "reminder" in message.lower():
                    icon_class = "fa-clock"
                    bg_class = "info"
                    title = "Appointment Reminder"
                
                formatted_notifications.append({
                    'id': notif_id,
                    'title': title,
                    'message': message,
                    'time': timestamp,
                    'icon_class': icon_class,
                    'bg_class': bg_class,
                    'unread': True  # All notifications are unread by default
                })
            
            cursor.execute("SELECT name, specialization FROM doctors")
            doctors = cursor.fetchall()
            
            # Get user profile info
            cursor.execute("SELECT phone_number FROM phone_numbers WHERE email = ?", (user_email,))
            phone_data = cursor.fetchone()
            phone_number = phone_data[0] if phone_data else ""
            
            # Get full name from users table
            cursor.execute("SELECT full_name FROM users WHERE email = ?", (user_email,))
            full_name_data = cursor.fetchone()
            full_name = full_name_data[0] if full_name_data and full_name_data[0] else ""

        return render_template(
            'indexuser.html',
            appointments=appointments,
            notifications=formatted_notifications,
            notification_count=len(formatted_notifications),
            doctors=doctors,
            user_name=full_name or user_name,
            user_email=user_email,
            phone_number=phone_number,
            full_name=full_name
        )
    return redirect(url_for('login'))

@app.route('/update_profile_from_index', methods=['POST'])
def update_profile_from_index():
    if 'user_type' in session and session['user_type'] == 'user':
        user_email = session.get('user_email')
        if not user_email:
            return redirect(url_for('login'))
        
        # Get form data
        new_phone = request.form.get('phone', '')
        new_full_name = request.form.get('full_name', '')
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            # Update phone number
            cursor.execute("""
            INSERT INTO phone_numbers (email, phone_number)
            VALUES (?, ?)
            ON CONFLICT(email) DO UPDATE SET phone_number=excluded.phone_number
            """, (user_email, new_phone))
            
            # Update full name
            cursor.execute("""
            UPDATE users 
            SET full_name = ?
            WHERE email = ?
            """, (new_full_name, user_email))
            
            conn.commit()
        
        return redirect(url_for('index_user'))
    
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
            
            # Create a notification for the appointment booking
            notification_message = f"Your appointment with Dr. {doctor_name} ({specialty}) has been scheduled for {time_slot}."
            cursor.execute("""
                INSERT INTO notifications (user_email, message)
                VALUES (?, ?)
            """, (user_email, notification_message))
            
            conn.commit()

        return {"success": True, "message": "Appointment booked successfully!"}
    return {"success": False, "message": "User not authenticated"}, 403


@app.route('/cancel_appointment', methods=['POST'])
def cancel_appointment():
    if 'user_type' in session and session['user_type'] == 'user':
        data = request.get_json()
        doctor_name = data.get('doctor')
        time_slot = data.get('time')
        user_email = session.get('user_email')

        if not doctor_name or not time_slot:
            return {"success": False, "message": "Missing appointment details"}, 400

        # Delete appointment from database
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM appointments 
                WHERE user_email = ? AND doctor_name = ? AND time_slot = ?
            """, (user_email, doctor_name, time_slot))
            
            if cursor.rowcount > 0:
                # Create a notification for the appointment cancellation
                notification_message = f"Your appointment with Dr. {doctor_name} scheduled for {time_slot} has been cancelled."
                cursor.execute("""
                    INSERT INTO notifications (user_email, message)
                    VALUES (?, ?)
                """, (user_email, notification_message))
                conn.commit()
                return {"success": True, "message": "Appointment cancelled successfully"}
            else:
                conn.commit()
                return {"success": False, "message": "Appointment not found"}, 404

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

def add_to_notifications(user_email, doctor, specialty, time):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        # Create a notification message for the appointment
        notification_message = f"Your appointment with Dr. {doctor} ({specialty}) has been scheduled for {time}."
        cursor.execute("""
        INSERT INTO notifications (user_email, message, title)
        VALUES (?, ?, ?)
        """, (user_email, notification_message, "Appointment Confirmation"))
        conn.commit()

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_email' not in session:
        return {"success": False, "message": "User not logged in"}, 401

    rating = request.form.get('rating', 3) 
    comment = request.form.get('comment')
    user_email = session.get('user_email')

    if not comment or not comment.strip():
        return {"success": False, "message": "Comment cannot be empty!"}, 400

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO feedback (user_email, rating, comment) VALUES (?, ?, ?)
        """, (user_email, rating, comment))
        conn.commit()

    return {"success": True, "message": "Thank you for your feedback!"}

@app.route('/user_feedback', methods=['POST'])
def user_feedback():
    if 'user_type' in session and session['user_type'] == 'user':
        user_email = session.get('user_email')
        if not user_email:
            return {"success": False, "message": "Not logged in"}, 401
        
        rating = int(request.form.get('rating', 3))
        comment = request.form.get('comment', '')
        
        if not comment.strip():
            return {"success": False, "message": "Comment cannot be empty"}, 400
            
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (user_email, rating, comment)
                VALUES (?, ?, ?)
            """, (user_email, rating, comment))
            conn.commit()
            
        return {"success": True, "message": "Thank you for your feedback!"}
    return {"success": False, "message": "Unauthorized"}, 403

if __name__ == "__main__":
    app.run(debug=True, port=5001)
