from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-only-key")

db = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME", "clinic_db")
)

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

        cursor.execute("SELECT * FROM Users WHERE username=%s", (username,))
        if cursor.fetchone():
            return "Username already exists."

        # Insert into Users
        cursor.execute(
            "INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )

        user_id = cursor.lastrowid

        # Insert based on role
        if role == 'Patient':
            cursor.execute("""
                INSERT INTO Patients (user_id, first_name, last_name, email, phone)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, first_name, last_name, email, phone))

        elif role == 'Doctor':
            cursor.execute("""
                INSERT INTO Doctors (user_id, first_name, last_name, specialization, phone, email)
                VALUES (%s, %s, %s, 'General', %s, %s)
            """, (user_id, first_name, last_name, phone, email))

        db.commit()

        return "Registration Successful!"


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login_form.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            role = user['role']
            session['username'] = username
            session['user_id'] = user['user_id']
            session['role'] = role
            if role == 'Admin':
                return redirect('/admin')
            elif role == 'Doctor':
                return redirect('/doctor')
            elif role == 'Patient':
                return redirect('/patient')

        return "Invalid Credentials"


# Dashboards
@app.route('/doctor')
def doctor():

    cursor = db.cursor(dictionary=True)

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

    return render_template(
        'doctor_dashboard.html',
        doctor=doctor_info,
        total=total,
        completed=completed,
        scheduled=scheduled,
        patients=patients,
        today_count=today_count,
        appointments=appointments
    )
@app.route('/complete/<int:appointment_id>')
def complete(appointment_id):

    cursor = db.cursor()
    cursor.execute("""
        UPDATE Appointments
        SET status = 'Completed'
        WHERE appointment_id = %s
    """, (appointment_id,))
    db.commit()

    return redirect('/doctor')


@app.route('/cancel/<int:appointment_id>')
def cancel(appointment_id):

    cursor = db.cursor()
    cursor.execute("""
        UPDATE Appointments
        SET status = 'Cancelled'
        WHERE appointment_id = %s
    """, (appointment_id,))
    db.commit()

    return redirect('/doctor')

@app.route('/add_record/<int:appointment_id>', methods=['GET', 'POST'])
def add_record(appointment_id):

    if request.method == 'POST':

        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        blood_pressure = request.form['blood_pressure']
        weight = request.form['weight']
        height = request.form['height']

        cursor = db.cursor()

        # Get patient + doctor from appointment
        cursor.execute("""
            SELECT patient_id, doctor_id
            FROM Appointments
            WHERE appointment_id = %s
        """, (appointment_id,))
        data = cursor.fetchone()

        patient_id = data[0]
        doctor_id = data[1]

        cursor.execute("""
            INSERT INTO MedicalRecords
            (patient_id, doctor_id, appointment_id,
             diagnosis, treatment_notes, blood_pressure, weight, height)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (patient_id, doctor_id, appointment_id,
              diagnosis, treatment, blood_pressure, weight, height))

        db.commit()

        return redirect('/doctor')

    return render_template('add_record.html', appointment_id=appointment_id)

@app.route('/admin')
def admin():

    cursor = db.cursor(dictionary=True)

    # Get all doctors
    cursor.execute("""
        SELECT doctor_id, first_name, last_name, specialization, phone, email
        FROM Doctors
    """)
    doctors = cursor.fetchall()

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
        doctors=doctors,
        patients=patients,
        revenue=revenue
    )


@app.route('/patient')
def patient():

    cursor = db.cursor(dictionary=True)

    # Get patient_id from logged-in user
    cursor.execute(
        "SELECT patient_id FROM Patients WHERE user_id = %s",
        (session['user_id'],)
    )
    patient_data = cursor.fetchone()
    patient_id = patient_data['patient_id']

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
        SELECT appointment_date, appointment_time, status
        FROM Appointments
        WHERE patient_id = %s
        ORDER BY appointment_date
    """, (patient_id,))
    appointments = cursor.fetchall()

    return render_template(
        'patient_dashboard.html',
        total=total,
        completed=completed,
        upcoming=upcoming,
        appointments=appointments
    )
# Logout Route (ADD HERE)
@app.route('/logout')
def logout():
    session.clear()   # clears logged in user
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)



