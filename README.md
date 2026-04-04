# SmartCare Clinic System

A full-stack healthcare management system designed to streamline clinic operations, including patient management, appointment scheduling, medical records, and billing.

This project was developed using Flask (Python) and MySQL, with a focus on extending the system through cybersecurity enhancements and data-driven features.

---

## Overview

SmartCare is a role-based web application that supports:

* Doctors managing appointments and patient records
* Administrators overseeing system data and revenue
* Patients booking and tracking appointments

The system was initially built as a core clinic management platform and is being actively extended with advanced security and analytical features.

---

## Key Features

### Core System

* Patient registration and management
* Doctor profiles and availability tracking
* Appointment scheduling with conflict prevention
* Medical record creation and storage
* Billing and payment tracking
* Role-based dashboards (Admin, Doctor, Patient)

### Cybersecurity Enhancements (In Progress)

* Secure authentication using password hashing
* Access logging for user activity tracking
* Detection of suspicious behavior (e.g., repeated failed login attempts)

### Data-Driven Features (In Progress)

* Anomaly detection system for identifying unusual activity patterns
* Smart scheduling recommendations based on system usage
* Patient health risk indicators based on medical data

---

## Tech Stack

* Backend: Python (Flask)
* Database: MySQL
* Frontend: HTML, CSS, Bootstrap
* Tools: Git, GitHub

---

## Database Design

The system uses a relational database with the following core tables:

* Patients
* Doctors
* Appointments
* MedicalRecords
* Prescriptions
* Billing
* Users

Relationships are enforced using foreign keys and constraints to ensure data integrity.

---

## Project Evolution

This project was initially developed as a clinic management system.

It is currently being extended to incorporate:

* Cybersecurity practices such as secure authentication and activity monitoring
* Data-driven features to improve system intelligence and decision-making

These additions aim to bring the system closer to real-world healthcare software standards.

---

## Contributions

* Initial system (database schema, UI, and core functionality): Developed by original team members
* System extension (cybersecurity and data-driven features): Developed by ongoing contributors

Current extension work includes:

* Implementing password hashing for secure authentication
* Designing an anomaly detection system for suspicious user activity
* Enhancing system intelligence through data-driven features

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sheev2004-blip/DBMS-Appt-System-Project.git
cd DBMS-Appt-System-Project
```

### 2. Set Up the Database

* Open MySQL
* Import the SQL file located in:

```text
database/clinic_db.sql
```

### 3. Install Dependencies

```bash
pip install flask mysql-connector-python
```

### 4. Configure Environment Variables (Recommended)

Instead of hardcoding credentials, set:

```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=clinic_db
SECRET_KEY=your_secret_key
```

### 5. Run the Application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/
```

---

## Future Improvements

* Advanced anomaly detection using statistical or machine learning techniques
* Multi-factor authentication (MFA)
* Improved UI/UX design
* API integration for external healthcare services
* Deployment to cloud platforms

---

## Notes

This project is part of a Database Management Systems (DBMS) course and is being enhanced beyond core requirements to include real-world cybersecurity and data analysis concepts.

---

## License

This project is for educational purposes.
lip/DBMS-Appt-System-Project.git
