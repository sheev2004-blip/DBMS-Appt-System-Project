# Clinic Appointment Management System
DBMS-Appt-System-Project

A database-driven appointment management system designed for medical clinics.  
Developed for CSCI 4560-5560: Database Management Systems.

---

## 📌 Project Overview

The Clinic Appointment Management System is designed to help medical clinics efficiently manage:

- Patient records
- Doctor schedules
- Appointments
- Billing information

This system demonstrates core database design principles including relational modeling, normalization, SQL querying, indexing, and data integrity enforcement.

---

## 🚀 Features

- Create, update, and delete patient records
- Schedule and cancel appointments
- Assign doctors to appointments
- Prevent double-booking
- Track appointment status (Scheduled, Completed, Cancelled, No-Show)
- Search functionality (by patient name, date, doctor, etc.)
- Reporting queries for clinic insights

---

## 🛠 Technologies Used

- SQL (MySQL)
- Python Flask Framework
- HTML, CSS, and Bootstrap

---

## 🗄 Database Design

### Main Entities

- PATIENT
- DOCTOR
- APPOINTMENT
- BILLING
- MEDICAL RECORDS
- PRESCRIPTION

### Relationships

- A patient can have many appointments.
- A doctor can have many appointments.
- An appointment belongs to one patient and one doctor.

---

## ⚙️ Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DBMS-Appt-System-Project.git
