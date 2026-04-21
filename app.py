from flask import Flask, render_template, request, redirect, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import secrets
from datetime import datetime, time

app = Flask(__name__)

def get_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']

app.jinja_env.globals['csrf_token'] = get_csrf_token

app.secret_key = os.environ.get("SECRET_KEY", "dev-only-key")

db = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME", "clinic_db")
)

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = request.form.get("csrf_token")
        if not token or token != session.get("csrf_token"):
            abort(400)

# Homepage
@app.route('/')
def home():
    return render_template('index.html')


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cursor = db.cursor()

        user_IP = request.remote_addr
        #cursor.execute("SELECT ip_address FROM AccessLogs " "WHERE action_type = 'LOGIN' " "AND status = 'FAILED' " 
                           #"AND created_at >= NOW() - INTERVAL 10 MINUTE " "AND ip_address = %s " "GROUP BY ip_address " "HAVING COUNT(*) >= 5", 
                          # (user_IP,) )
        #result_IP = cursor.fetchone()
        #if result_IP:
                #cursor.execute("SELECT ip_address FROM BlockedIPs WHERE is_active = 1 AND ip_address = %s", 
                              #(user_IP,))
                #result = cursor.fetchone()

                #if (result is None): 
                    #cursor.execute("INSERT INTO BlockedIPs (ip_address, reason, is_active, blocked_by, notes) VALUES (%s, %s, %s, %s, %s)",
                                   #(user_IP, "Repeated failed logins",  1, None, None))
                    #db.commit()


        # remove this after demo
        cursor.execute(
            "SELECT ip_address FROM BlockedIPs WHERE is_active = 1 AND ip_address = %s",
            (user_IP,))

        IP_is_blocked = cursor.fetchone()

        if IP_is_blocked: 
            cursor.execute(
                    "INSERT INTO AccessLogs (user_id, action_type, status, ip_address) VALUES (%s, %s, %s, %s)" ,
                    (None, 'REGISTER', 'BLOCKED', request.remote_addr)
                )
            db.commit()
            return render_template("register.html", error = "Access denied. Please contact an administrator.")

        cursor.execute("SELECT * FROM Users WHERE username=%s", (username,))
        if cursor.fetchone():
             return render_template("register.html", error = "Username already exists")

        # Generate password hash

        hashed_password = generate_password_hash(password)

        # Insert into Users
        cursor.execute(
            "INSERT INTO Users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hashed_password, role)
        )

        user_id = cursor.lastrowid

        # Insert based on role
        if role == 'Patient':
            cursor.execute("""
                INSERT INTO Patients (user_id, first_name, last_name, email, phone)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, first_name, last_name, email, phone))
            
            patient_id = cursor.lastrowid
            mrn = f"MRN-{patient_id:05d}"

            cursor.execute("""
                UPDATE Patients
                SET mrn = %s
                WHERE patient_id = %s
                """, (mrn, patient_id))
        elif role == 'Doctor':
            cursor.execute("""
                INSERT INTO Doctors (user_id, first_name, last_name, specialization, phone, email)
                VALUES (%s, %s, %s, 'General', %s, %s)
            """, (user_id, first_name, last_name, phone, email))

        db.commit()
        flash("Account created successfully. Please log in.", "success")
        return redirect("/login")

    


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login_form.html')

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)

        # Check if IP is blocked
        cursor.execute("SELECT * FROM BlockedIPs WHERE ip_address = %s AND is_active = 1", 
                       (request.remote_addr,))
        IP_is_blocked = cursor.fetchone()

        if IP_is_blocked: 
            cursor.execute(
                    "INSERT INTO AccessLogs (user_id, action_type, status, ip_address) VALUES (%s, %s, %s, %s)" ,
                    (None, 'LOGIN', 'BLOCKED', request.remote_addr)
                )
            db.commit()
            return render_template("login_form.html", error = "Access denied. Please contact an administrator.")
        # Search for user by username
        cursor.execute(
            "SELECT * FROM Users WHERE username=%s",
            (username,)
        )
        user = cursor.fetchone()
        # If user lookup is successful, check if they are blocked before looking for password
        if user:
            cursor.execute("SELECT * FROM BlockedUsers WHERE user_id = %s AND is_active = 1",
                           (user['user_id'],))
            result = cursor.fetchone()
            if result:
                cursor.execute(
                    "INSERT INTO AccessLogs (user_id, action_type, status, ip_address) VALUES (%s, %s, %s, %s)" ,
                    (user['user_id'], 'LOGIN', 'BLOCKED', request.remote_addr)
                )
                db.commit()
                return render_template("login_form.html", error = "Access denied. Please contact an administrator.")
        
        # Non-blocked login path with hashed password
        if user and check_password_hash(user['password_hash'], password):
            role = user['role']
            session['username'] = username
            session['user_id'] = user['user_id']
            session['role'] = role
            cursor.execute(
            "INSERT INTO AccessLogs (user_id, action_type, status, ip_address) VALUES (%s, %s, %s, %s)",
            (user['user_id'], 'LOGIN', 'SUCCESS', request.remote_addr)
            )
            db.commit()
            if role == 'Admin':
                return redirect('/admin')
            elif role == 'Doctor':
                return redirect('/doctor')
            elif role == 'Patient':
                return redirect('/patient')
            
        # Path if username is valid but password is not
        if (user):
            cursor.execute(
            "INSERT INTO AccessLogs (user_id, action_type, status, ip_address) VALUES (%s, %s, %s, %s)",
            (user['user_id'], 'LOGIN', 'FAILED', request.remote_addr)
            )
            db.commit()

            #user_id = user['user_id'] 
            
            # Check for blocking requirements
            #cursor.execute( "SELECT user_id FROM AccessLogs " "WHERE action_type = 'LOGIN' " "AND status = 'FAILED' " 
                           #"AND created_at >= NOW() - INTERVAL 10 MINUTE " "AND user_id = %s " "GROUP BY user_id " "HAVING COUNT(*) >= 5", 
                           #(user_id,) ) 
            #result_user = cursor.fetchone()
            
            # If requirements met, check if user is not blocked already 
            #if result_user: 
                #cursor.execute("SELECT user_id FROM BlockedUsers WHERE is_active = 1 AND user_id = %s", (user_id,) )
                #result2 = cursor.fetchone()
                # Only block if not admin
                #if (result2 is None and user['role'] != 'Admin'):
                    #cursor.execute("INSERT INTO BlockedUsers (user_id, reason, is_active, blocked_by, notes) VALUES (%s, %s, %s, %s, %s)",
                                   #(user_id, "Repeated failed logins",  1, None, None))
                    #db.commit()

        # Incorrect username path   
        else:
            cursor.execute(
            "INSERT INTO AccessLogs (user_id, action_type, status, ip_address) VALUES (%s, %s, %s, %s)",
            (None, 'LOGIN', 'FAILED', request.remote_addr)
            )
            db.commit()

        
        #user_IP = request.remote_addr
        # Check if IP needs to be blocked
        #cursor.execute("SELECT ip_address FROM AccessLogs " "WHERE action_type = 'LOGIN' " "AND status = 'FAILED' " 
                           #"AND created_at >= NOW() - INTERVAL 10 MINUTE " "AND ip_address = %s " "GROUP BY ip_address " "HAVING COUNT(*) >= 5", 
                           #(user_IP,) )
        #result_IP = cursor.fetchone()
        # Check if IP is already blocked
        #if result_IP:
                #cursor.execute("SELECT ip_address FROM BlockedIPs WHERE is_active = 1 AND ip_address = %s", 
                               #(user_IP,))
                #result3 = cursor.fetchone()
        # If IP is not blocked and role is not Admin, auto block IP
                #if((user) and user['role'] == 'Admin'):
                    #return render_template("login_form.html", error = "Invalid Username/Password")
                #else:
                    #if (result3 is None): 
                        #cursor.execute("INSERT INTO BlockedIPs (ip_address, reason, is_active, blocked_by, notes) VALUES (%s, %s, %s, %s, %s)",
                                   #(user_IP, "Repeated failed logins",  1, None, None))
                        #db.commit()
            
        return render_template("login_form.html", error = "Invalid Username/Password")                
        


# Dashboards
@app.route('/doctor')
def doctor():

    cursor = db.cursor(dictionary=True)
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Doctor':
        return redirect('/login')

    cursor.execute("SELECT doctor_id FROM Doctors WHERE user_id = %s", (session['user_id'],))
    doctor_id = cursor.fetchone()['doctor_id']

    # Doctor Info
    cursor.execute("""
        SELECT first_name, last_name, specialization
        FROM Doctors
        WHERE doctor_id = %s
    """, (doctor_id,))
    doctor_info = cursor.fetchone()

    # Total Appointments
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Appointments
        WHERE doctor_id = %s
    """, (doctor_id,))
    total = cursor.fetchone()['total']

    # Completed
    cursor.execute("""
        SELECT COUNT(*) AS completed
        FROM Appointments
        WHERE doctor_id = %s AND status = 'Completed'
    """, (doctor_id,))
    completed = cursor.fetchone()['completed']

    # Scheduled
    cursor.execute("""
        SELECT COUNT(*) AS scheduled
        FROM Appointments
        WHERE doctor_id = %s AND status = 'Scheduled'
    """, (doctor_id,))
    scheduled = cursor.fetchone()['scheduled']

    # Unique Patients Treated
    cursor.execute("""
        SELECT COUNT(DISTINCT patient_id) AS patients
        FROM Appointments
        WHERE doctor_id = %s
    """, (doctor_id,))
    patients = cursor.fetchone()['patients']

    #  Today's Appointments
    cursor.execute("""
        SELECT COUNT(*) AS today_count
        FROM Appointments
        WHERE doctor_id = %s AND appointment_date = CURDATE()
    """, (doctor_id,))
    today_count = cursor.fetchone()['today_count']

    #  Appointment List
    cursor.execute("""
        SELECT 
            a.appointment_id,
            p.first_name,
            p.last_name,
            a.appointment_date,
            a.appointment_time,
            a.status
            
        FROM Appointments a
        JOIN Patients p ON a.patient_id = p.patient_id
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date
    """, (doctor_id,))
    appointments = cursor.fetchall()

    # My Patients List

    cursor.execute("""
        SELECT p.patient_id, 
                   CONCAT(p.first_name, ' ', p.last_name) AS patient_name, 
                   p.mrn,
                   MAX(a.appointment_date) AS last_visit
                   FROM Appointments a
                   JOIN Patients p ON a.patient_id = p.patient_id
                   WHERE a.doctor_id = %s
                   GROUP BY p.patient_id, p.first_name, p.last_name, p.mrn
                   ORDER BY last_visit DESC""",
                   (doctor_id,))
    my_patients = cursor.fetchall()

    return render_template(
        'doctor_dashboard.html',
        doctor=doctor_info,
        total=total,
        completed=completed,
        scheduled=scheduled,
        patients=patients,
        today_count=today_count,
        appointments=appointments,
        my_patients=my_patients
    )
@app.route('/complete/<int:appointment_id>', methods=['POST'])
def complete(appointment_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Doctor':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute(
    "SELECT doctor_id FROM Doctors WHERE user_id = %s",
    (session['user_id'],)
    )
    result = cursor.fetchone()
    if result is None:
        return redirect("/doctor")
    doctor_id = result['doctor_id']

    cursor.execute(
    "SELECT doctor_id FROM Appointments WHERE appointment_id = %s",
    (appointment_id,)
    )
    appt = cursor.fetchone()

    
    if appt is None:
        return redirect('/doctor')
    
    appointment_doctor_id = appt['doctor_id']

    if doctor_id != appointment_doctor_id:
        return redirect('/doctor')
    

    cursor.execute("""
        UPDATE Appointments
        SET status = 'Completed'
        WHERE appointment_id = %s
    """, (appointment_id,))

    cursor.execute("""SELECT a.patient_id, d.specialization
FROM Appointments a
JOIN Doctors d ON a.doctor_id = d.doctor_id
WHERE a.appointment_id = %s""",
(appointment_id,))
    appt_info = cursor.fetchone()

    specialization = appt_info['specialization']

    if specialization == 'Cardiology':
        consultation_fee = 150
    elif specialization == 'Dermatology':
        consultation_fee = 120
    elif specialization == 'Pediatrics':
        consultation_fee = 110
    elif specialization == 'Gynecology':
        consultation_fee = 130
    elif specialization == 'Orthopedics':
        consultation_fee = 140
    elif specialization == 'Neurology':
        consultation_fee = 160
    else:
        consultation_fee = 100

    medicine_charges = 0
    lab_charges = 0

    cursor.execute("""SELECT bill_id
FROM Billing
WHERE appointment_id = %s""",(appointment_id,))
    exists = cursor.fetchone()
    
    if exists:
        return redirect('/doctor')
    
    cursor.execute("""
    INSERT INTO Billing
    (patient_id, appointment_id, consultation_fee, medicine_charges, lab_charges, payment_status)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (appt_info['patient_id'], appointment_id, consultation_fee, medicine_charges, lab_charges, 'Pending'))

    db.commit()
    return redirect('/doctor')


@app.route('/cancel/<int:appointment_id>', methods=['POST'])
def cancel(appointment_id):

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Doctor':
        return redirect('/login')
    
    cursor = db.cursor(dictionary=True)

    cursor.execute(
    "SELECT doctor_id FROM Doctors WHERE user_id = %s",
    (session['user_id'],)
    )
    result = cursor.fetchone()
    if result is None:
        return redirect("/doctor")
    doctor_id = result['doctor_id']

    cursor.execute(
    "SELECT doctor_id FROM Appointments WHERE appointment_id = %s",
    (appointment_id,)
    )
    appt = cursor.fetchone()
    if appt is None:
        return redirect('/doctor')
    
    appointment_doctor_id = appt['doctor_id']

    if doctor_id != appointment_doctor_id:
        return redirect('/doctor')
  
    cursor.execute("""
        UPDATE Appointments
        SET status = 'Cancelled'
        WHERE appointment_id = %s
    """, (appointment_id,))
    db.commit()

    return redirect('/doctor')

@app.route('/add_record/<int:appointment_id>', methods=['GET', 'POST'])
def add_record(appointment_id):
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Doctor':
        return redirect('/login')
    
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT doctor_id FROM Doctors WHERE user_id = %s",
        (session['user_id'],)
            )
    result = cursor.fetchone()
    if result is None:
        return redirect("/doctor")
    doctor_id = result['doctor_id']

    cursor.execute(
        "SELECT doctor_id FROM Appointments WHERE appointment_id = %s",
        (appointment_id,)
        )
    appt = cursor.fetchone()
    if appt is None:
        return redirect('/doctor')
    appointment_doctor_id = appt['doctor_id']
    if doctor_id != appointment_doctor_id:
        return redirect('/doctor')
    

    
    if request.method == 'POST':

        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        blood_pressure = request.form['blood_pressure']
        weight = request.form['weight']
        height = request.form['height']
        medicine_name = request.form['medicine_name']
        dosage = request.form['dosage']
        frequency = request.form['frequency']
        duration = request.form['duration']


        if not frequency.strip():
            frequency = ''

        if weight == '':
            weight = None

        if height == '':
            height = None
        
        # Get patient + doctor from appointment
        cursor.execute("""
            SELECT patient_id, doctor_id
            FROM Appointments
            WHERE appointment_id = %s
        """, (appointment_id,))
        data = cursor.fetchone()

        patient_id = data["patient_id"]
        doctor_id = data["doctor_id"]

        cursor.execute("""
            INSERT INTO MedicalRecords
            (patient_id, doctor_id, appointment_id,
             diagnosis, treatment_notes, blood_pressure, weight, height)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (patient_id, doctor_id, appointment_id,
              diagnosis, treatment, blood_pressure, weight, height))
        
        record_id = cursor.lastrowid
        if medicine_name.strip() != '':
            cursor.execute("""
            INSERT INTO Prescriptions (record_id, medicine_name, dosage, frequency, duration)
            VALUES (%s, %s, %s, %s, %s)
            """, (record_id, medicine_name, dosage, frequency, duration))

        db.commit()

        return redirect('/doctor')
    cursor.execute("""SELECT
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.mrn,
    p.date_of_birth,
    p.sex,
    p.allergies,
    a.reason_for_visit,
    a.appointment_date,
    a.appointment_time
FROM Appointments a
JOIN Patients p ON a.patient_id = p.patient_id
WHERE a.appointment_id = %s""",
(appointment_id,))
    
    patient_context = cursor.fetchone()
    appointment_time_td = patient_context['appointment_time']

    if appointment_time_td is not None:
        total_seconds = appointment_time_td.seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        display_time = datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M").strftime("%I:%M %p")
    else:
        display_time = None

    patient_context['display_time'] = display_time

    return render_template('add_record.html', appointment_id=appointment_id, patient_context=patient_context)



@app.route('/admin')
def admin():

    cursor = db.cursor(dictionary=True)

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Admin':
        return redirect('/login')
    
    # Get all currently blocked users

    cursor.execute("""
                   SELECT u.username, b.reason, b.blocked_at, b.block_id
                   FROM BlockedUsers b
                   JOIN Users u ON b.user_id = u.user_id
                   WHERE b.is_active = 1
                    """)
    blocked_users = cursor.fetchall()
    
    # Get all currently blocked IP addresses

    cursor.execute("""
                   SELECT ip_address, reason, blocked_at, block_id
                   FROM BlockedIPs
                   WHERE is_active = 1
                    """)
    blocked_IPs = cursor.fetchall()

    # Get all suspicious users

    cursor.execute("""
                    SELECT u.username, u.user_id, l.ip_address, COUNT(*) AS failed_attempts, MAX(l.created_at) AS last_attempt
                    FROM AccessLogs l
                    JOIN Users u ON u.user_id = l.user_id
                    LEFT JOIN BlockedUsers b ON b.user_id = l.user_id AND b.is_active = 1
                    WHERE b.user_id IS NULL
                        AND l.action_type = 'LOGIN'
                        AND l.status = 'FAILED'
                        AND l.created_at >= NOW() - INTERVAL 1 DAY
                    GROUP BY l.user_id, u.username, l.ip_address
                    HAVING COUNT(*) >= 3;
                   """)
    suspicious_users = cursor.fetchall()

    # Get all suspicious IPs

    cursor.execute("""
                    SELECT l.ip_address, COUNT(*) AS failed_attempts, MAX(l.created_at) AS last_attempt
                    FROM AccessLogs l
                    LEFT JOIN BlockedIPs b ON b.ip_address = l.ip_address AND b.is_active = 1
                    WHERE b.ip_address IS NULL 
                        AND l.action_type = 'LOGIN'
                        AND l.status = 'FAILED'
                        AND l.created_at >= NOW() - INTERVAL 1 DAY
                    GROUP BY l.ip_address
                    HAVING COUNT(*) >= 3;
                    """)
    suspicious_IPs = cursor.fetchall()
    print("Suspicious IPs:", suspicious_IPs)

    # Get all doctors
    cursor.execute("""
        SELECT doctor_id, first_name, last_name, specialization, phone, email, available_from, available_to
        FROM Doctors
    """)
    doctor = cursor.fetchall()

    # Get all patients
    cursor.execute("""
        SELECT patient_id, first_name, last_name, email, phone
        FROM Patients
    """)
    patients = cursor.fetchall()

    # Revenue statistics
    cursor.execute("""
        SELECT SUM(total_amount) AS revenue
        FROM Billing
    """)
    revenue = cursor.fetchone()['revenue']

    return render_template(
        'admin_dashboard.html',
        doctor=doctor,
        patients=patients,
        revenue=revenue,
        blocked_users=blocked_users,
        blocked_IPs=blocked_IPs,
        suspicious_users=suspicious_users,
        suspicious_IPs=suspicious_IPs
    )

@app.route('/unblock_user/<int:block_id>', methods=['POST'])
def unblock_user(block_id):
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Admin':
        return redirect('/login')
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM BlockedUsers WHERE block_id = %s",
                   (block_id,))
    result = cursor.fetchone()

    if (result and result["is_active"] == 1):
        cursor.execute("UPDATE BlockedUsers SET is_active = 0 WHERE block_id = %s",
        (block_id,))

        cursor.execute("UPDATE Blockedusers SET unblocked_at = CURRENT_TIMESTAMP")
        db.commit()

    return redirect("/admin")

@app.route('/unblock_IP/<int:block_id>', methods=['POST'])
def unblock_IP(block_id):
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Admin':
        return redirect('/login')
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM BlockedIPs WHERE block_id = %s",
                   (block_id,))
    result = cursor.fetchone()

    if (result and result["is_active"] == 1):
        cursor.execute("UPDATE BlockedIPs SET is_active = 0 WHERE block_id = %s",
        (block_id,))

        cursor.execute("UPDATE BlockedIPs SET unblocked_at = CURRENT_TIMESTAMP")
        db.commit()

    return redirect("/admin")

@app.route('/block_user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Admin':
        return redirect('/login')
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE user_id = %s",
                   (user_id,))
    exists = cursor.fetchone()

    if exists is None:
        return redirect("/admin")

    cursor.execute("SELECT * FROM BlockedUsers WHERE is_active = 1 AND user_id = %s",
                   (user_id,))
    is_blocked = cursor.fetchone()

    if is_blocked:
        return redirect("/admin")
    
    cursor.execute("INSERT INTO BlockedUsers (user_id, reason, is_active, blocked_at, blocked_by, unblocked_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s)",
    (exists['user_id'], 'Suspicious activity', 1, session.get('user_id'), None))

    db.commit()

    return redirect("/admin")


@app.route('/block_IP/<ip_address>', methods=['POST'])
def block_IP(ip_address):
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Admin':
        return redirect('/login')
    
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM BlockedIPs WHERE is_active = 1 AND ip_address = %s",
                   (ip_address,))
    is_blocked = cursor.fetchone()

    if is_blocked:
        return redirect("/admin")
    
    cursor.execute("INSERT INTO BlockedIPs (ip_address, reason, is_active, blocked_at, blocked_by, unblocked_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s)",
    (ip_address, 'Suspicious activity', 1, session.get('user_id'), None))

    db.commit()

    return redirect("/admin")


@app.route('/patient')
def patient():

    cursor = db.cursor(dictionary=True)

    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Patient':
        return redirect('/login')

    # Get patient_id from logged-in user
    cursor.execute(
        "SELECT patient_id FROM Patients WHERE user_id = %s",
        (session['user_id'],)
    )
    patient_data = cursor.fetchone()
    patient_id = patient_data['patient_id']

    cursor.execute("""SELECT appointment_id, total_amount, payment_status
FROM Billing
WHERE patient_id = %s
ORDER BY appointment_id DESC""",
(patient_data['patient_id'],))

    billing_records = cursor.fetchall()
    # Total appointments
    cursor.execute(
        "SELECT COUNT(*) AS total FROM Appointments WHERE patient_id = %s",
        (patient_id,)
    )
    total = cursor.fetchone()['total']

    # Completed visits
    cursor.execute("""
        SELECT COUNT(*) AS completed
        FROM Appointments
        WHERE patient_id = %s AND status = 'Completed'
    """, (patient_id,))
    completed = cursor.fetchone()['completed']

    # Upcoming appointments
    cursor.execute("""
        SELECT COUNT(*) AS upcoming
        FROM Appointments
        WHERE patient_id = %s AND status = 'Scheduled'
    """, (patient_id,))
    upcoming = cursor.fetchone()['upcoming']

    # Fetch appointment list
    cursor.execute("""
        SELECT appointment_date, appointment_time, status, appointment_id
        FROM Appointments
        WHERE patient_id = %s
        ORDER BY appointment_date
    """, (patient_id,))
    appointments = cursor.fetchall()


    #Get all patient info

    cursor.execute("""SELECT CONCAT(first_name, ' ', last_name) AS patient_name, mrn, date_of_birth, sex, address, smoking_status, alcohol_use, emergency_contact_name,
                   emergency_contact_phone, allergies FROM Patients WHERE patient_id = %s""",
                   (patient_id,))
    patient_info = cursor.fetchone()

    if patient_info is None:
        return redirect('/patient')  # or /patient, whichever fits your flow

    mrn = patient_info['mrn']
    name = patient_info['patient_name']
    dob = patient_info['date_of_birth']
    sex = patient_info['sex']
    address = patient_info['address']
    smoking_status = patient_info['smoking_status']
    alcohol_use = patient_info['alcohol_use']
    emergency_contact_name = patient_info['emergency_contact_name']
    emergency_contact_phone = patient_info['emergency_contact_phone']

    return render_template(
        'patient_dashboard.html',
        total=total,
        completed=completed,
        upcoming=upcoming,
        appointments=appointments,
        billing_records=billing_records,
        mrn=mrn,
        name=name,
        dob=dob,
        sex=sex,
        address=address,
        smoking_status=smoking_status,
        alcohol_use=alcohol_use,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_phone=emergency_contact_phone
    )

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Patient':
        return redirect('/login')
     
    if request.method == 'GET':
    
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Doctors")

        doctors = cursor.fetchall()

        return render_template(
            'book_appt.html',
            doctors=doctors
        )

    if request.method == 'POST':
        cursor = db.cursor(dictionary=True)

        doctor_id = request.form['doctor_id']
        appt_date = request.form['appointment_date']
        appt_time = request.form['appointment_time']
        reason_for_visit = request.form.get('reason_for_visit', '').strip()


        cursor.execute("SELECT * FROM Doctors")
        doctors = cursor.fetchall()

        cursor.execute("""
            SELECT doctor_id, available_from, available_to
            FROM Doctors
            WHERE doctor_id = %s
        """, (doctor_id,))
        doctor = cursor.fetchone()

        selected_date = datetime.strptime(appt_date, "%Y-%m-%d").date()
        today = datetime.today().date()

        if selected_date < today:
            return render_template('book_appt.html', doctors=doctors, error="Cannot book an appointment in the past.")
        
        selected_time = datetime.strptime(appt_time, "%H:%M").time()
        current_time = datetime.now().time()

        if selected_date == today and selected_time <= current_time:
            return render_template('book_appt.html', doctors=doctors, error="Cannot book an appointment earlier than the current time.")
        
        if selected_time.minute not in (0, 30):
            return render_template('book_appt.html', doctors=doctors, error="Appointments must be booked in 30-minute intervals.")
        
        available_from_td = doctor['available_from']
        available_to_td = doctor['available_to']

        available_from = time(
            hour=available_from_td.seconds // 3600,
            minute=(available_from_td.seconds % 3600) // 60
        )

        available_to = time(
            hour=available_to_td.seconds // 3600,
            minute=(available_to_td.seconds % 3600) // 60
        )

        if available_from and available_to:
            if selected_time < available_from or selected_time >= available_to:
                return render_template('book_appt.html', doctors=doctors, error="Selected time is outside this doctor's availability.")
            
        if selected_date.weekday() in (5, 6):
            return render_template('book_appt.html', doctors=doctors, error="Appointments cannot be booked on weekends.")

        cursor.execute(
        "SELECT patient_id FROM Patients WHERE user_id = %s",
        (session['user_id'],)
        )
        result = cursor.fetchone()

        if result is None:
            return redirect('/patient')

        patient_id = result['patient_id']

        cursor.execute(
        "SELECT doctor_id, available_from, available_to FROM Doctors WHERE doctor_id = %s",
        (doctor_id,)
        )
        doctor = cursor.fetchone()

        if doctor is None:
            return redirect('/patient')
        if (doctor['available_from'] is not None and doctor['available_to'] is not None):
            if time < str(doctor['available_from']) or time > str(doctor['available_to']):
                return redirect('/book_appointment')
        
        cursor.execute(
        "SELECT appointment_id FROM Appointments WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s AND status = 'Scheduled'",
        (doctor_id, date, time)
        )
        result = cursor.fetchone()

        if result:
            return render_template('book_appt.html', error='Error: Time slot already taken')
        
        cursor.execute("""
        INSERT INTO Appointments
        (patient_id, doctor_id, appointment_date, appointment_time, status, reason_for_visit)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (patient_id, doctor_id, date, time, 'Scheduled', reason_for_visit))
        db.commit()

        return redirect('/patient')
    
    
@app.route('/cancel_patient/<int:appointment_id>', methods=['POST'])
def cancel_patient(appointment_id):
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Patient':
        return redirect('/login')
    
    if request.method == 'POST':
        cursor = db.cursor(dictionary=True)
        cursor.execute(
        "SELECT patient_id FROM Patients WHERE user_id = %s",
        (session['user_id'],)
        )
        result = cursor.fetchone()

        if result is None:
            return redirect('/patient')

        patient_id = result['patient_id']
        cursor.execute("SELECT patient_id FROM Appointments WHERE appointment_id = %s",
                       (appointment_id,))
        result = cursor.fetchone()

        if (patient_id != result['patient_id']):
            return redirect('/patient')
        
        cursor.execute("UPDATE Appointments SET status = 'Cancelled' WHERE appointment_id = %s",
                       (appointment_id,))
        db.commit()

    return redirect("/patient")

@app.route('/update_patient', methods=['POST'])
def update_patient():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Patient':
        return redirect('/login')

    cursor = db.cursor()

    date_of_birth = request.form['date_of_birth']
    sex = request.form['sex']
    address = request.form['address']
    smoking_status = request.form['smoking_status']
    alcohol_use = request.form['alcohol_use']
    emergency_contact_name = request.form['emergency_contact_name']
    emergency_contact_phone = request.form['emergency_contact_phone']
    allergies = request.form['allergies']

    cursor.execute("""
        UPDATE Patients
        SET date_of_birth = %s,
            sex = %s,
            address = %s,
            smoking_status = %s,
            alcohol_use = %s,
            emergency_contact_name = %s,
            emergency_contact_phone = %s,
            allergies = %s
        WHERE user_id = %s
    """, (
        date_of_birth if date_of_birth else None,
        sex if sex else None,
        address if address else None,
        smoking_status if smoking_status else None,
        alcohol_use if alcohol_use else None,
        emergency_contact_name if emergency_contact_name else None,
        emergency_contact_phone if emergency_contact_phone else None,
        allergies if allergies else None,
        session['user_id']
    ))

    db.commit()
    return redirect('/patient')

@app.route('/medical_records')
def medical_records():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Patient':
        return redirect('/login')
    
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT patient_id, first_name, last_name, mrn
FROM Patients
WHERE user_id = %s""",
        (session['user_id'],)
        )
    result = cursor.fetchone()
    if result is None:
        return redirect('/patient')

    patient_id = result['patient_id']
    name = f"{result['first_name']} {result['last_name']}"
    mrn = result['mrn']

    cursor.execute("""SELECT
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    a.appointment_date,
    a.reason_for_visit,
    m.diagnosis,
    m.treatment_notes,
    m.blood_pressure,
    m.weight,
    m.height,
    p.medicine_name,
    p.dosage,
    p.frequency,
    p.duration
FROM MedicalRecords m
JOIN Doctors d ON m.doctor_id = d.doctor_id
LEFT JOIN Prescriptions p ON m.record_id = p.record_id
JOIN Appointments a ON m.appointment_id = a.appointment_id
WHERE m.patient_id = %s
ORDER BY a.appointment_date DESC""",
                   (patient_id,))
    records = cursor.fetchall()

    return render_template('medical_records.html',
                           records=records,
                           mrn=mrn,
                           name=name,

                           )

@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role') != 'Admin':
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT doctor_id, first_name, last_name, specialization, available_from, available_to
        FROM Doctors
        WHERE doctor_id = %s
    """, (doctor_id,))
    doctor = cursor.fetchone()

    if doctor is None:
        return redirect('/admin')

    if request.method == 'GET':
        return render_template('edit_doctor.html', doctor=doctor)

    if request.method == 'POST':
        available_from = request.form['available_from']
        available_to = request.form['available_to']

        if not available_from or not available_to:
            return render_template('edit_doctor.html', doctor=doctor, error="Both times are required")

        if available_from >= available_to:
            return render_template('edit_doctor.html', doctor=doctor, error="Available from must be earlier than available to")

        cursor.execute("""
            UPDATE Doctors
            SET available_from = %s,
                available_to = %s
            WHERE doctor_id = %s
        """, (available_from, available_to, doctor_id))
        db.commit()

        return redirect('/admin')

# Logout Route (ADD HERE)
@app.route('/logout')
def logout():
    session.clear()   # clears logged in user
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)



       
    

