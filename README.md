# SmartCare Clinic Management System

A full-stack clinic management system designed to streamline appointment scheduling, medical record management, and billing through a structured relational database and role-based web application.

This project was developed using Flask (Python) and MySQL, with a focus on data integrity, validation, and realistic clinical workflows.

---

## Overview

SmartCare is a role-based web application that supports three primary user types:

- **Patients** – book appointments, view medical records and billing, and update personal information  
- **Doctors** – manage appointments, view patient context, and record diagnoses and prescriptions  
- **Administrators** – oversee system activity, manage doctor availability, and view system statistics  

The system emphasizes reliability, structured workflows, and real-world usability.

---

## Key Features

### Core Functionality

- Appointment scheduling with:
  - conflict prevention (no double booking)
  - validation against past dates and times
  - enforcement of doctor availability windows
  - fixed interval time slots

- Patient management:
  - Medical Record Number (MRN) for unique identification
  - demographic and lifestyle data (allergies, smoking status, alcohol use)
  - emergency contact information

- Doctor workflow:
  - access to patient context (reason for visit, allergies, etc.)
  - ability to create medical records and prescriptions

- Medical records system:
  - diagnosis and treatment notes
  - vital signs (blood pressure, weight, height)

- Prescription management:
  - medication name, dosage, frequency, and duration
  - linked directly to medical records

- Billing system:
  - consultation, medicine, and lab charges
  - automatically calculated totals
  - payment status tracking

- Administrative tools:
  - system statistics (total patients, doctors, revenue)
  - doctor availability management
  - access logs and monitoring of suspicious activity
  - ability to block users and IP addresses

---

## Tech Stack

- **Backend:** Python (Flask)  
- **Database:** MySQL  
- **Frontend:** HTML, CSS, Bootstrap  
- **Tools:** Git, GitHub  

---

## Database Design

The system uses a relational database with structured relationships enforced through primary and foreign keys.

Core tables include:

- Users  
- Patients  
- Doctors  
- Appointments  
- MedicalRecords  
- Prescriptions  
- Billing  
- AccessLogs  
- BlockedUsers  
- BlockedIPs  

Constraints and validation logic ensure:
- data integrity (valid relationships between entities)
- data consistency (no conflicting or invalid records)

---

## System Workflow

1. Patients schedule appointments with a doctor  
2. The system validates scheduling constraints  
3. Doctors view appointments and patient context  
4. Doctors record diagnoses and prescriptions  
5. Billing is generated for completed appointments  
6. Patients view records and billing through their dashboard  

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sheev2004-blip/DBMS-Appt-System-Project.git
cd DBMS-Appt-System-Project
```

### 2. Set Up the Database

- Open MySQL
- Import the provided SQL file:

database/clinic_db.sql

### 3. Install Dependencies

```bash
pip install flask mysql-connector-python
```

### 4. Configure Environment Variables

Set the following variables:

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

- Then open:

http://127.0.0.1:5000/

## Future Improvements

- Calendar-based doctor scheduling (per-day availability)

- Automated appointment reminders

- Improved user interface and experience

- Advanced analytics and reporting tools

- Enhanced security features (e.g., multi-factor authentication)

## Notes

This project was developed as part of a Database Management Systems (DBMS) course. It demonstrates the use of relational database design, validation logic, and role-based workflows to create a realistic clinic management system.

## License

This project is for educational purposes.
