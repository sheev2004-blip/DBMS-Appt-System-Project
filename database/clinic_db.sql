CREATE DATABASE clinic_db;
USE clinic_db;


CREATE TABLE Patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    date_of_birth DATE,
    phone VARCHAR(15),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO Patients 
(first_name, last_name, phone, email, date_of_birth)
VALUES
('Emma', 'Taylor', '6155551234', 'emma.taylor@gmail.com', '1998-04-12'),
('Liam', 'Harris', '6295555678', 'liam.harris@gmail.com', '1995-09-23'),
('Olivia', 'Clark', '4235558899', 'olivia.clark@gmail.com', '2001-01-30'),
('Noah', 'Walker', '9015553344', 'noah.walker@gmail.com', '1992-06-15'),
('Ava', 'Martin', '7315557788', 'ava.martin@gmail.com', '1999-11-08');


CREATE TABLE Doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100),
    available_from TIME,
    available_to TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO Doctors 
(first_name, last_name, specialization, phone, email, available_from, available_to)
VALUES
('John', 'Smith', 'Cardiology', '4155551023', 'john.smith@clinicusa.com', '09:00:00', '17:00:00'),

('Emily', 'Johnson', 'Dermatology', '2125553344', 'emily.johnson@clinicusa.com', '10:00:00', '18:00:00'),

('Michael', 'Brown', 'Orthopedics', '3125557788', 'michael.brown@clinicusa.com', '08:00:00', '16:00:00'),

('Sarah', 'Davis', 'Neurology', '6175558899', 'sarah.davis@clinicusa.com', '09:30:00', '17:30:00'),

('David', 'Wilson', 'Pediatrics', '4085552233', 'david.wilson@clinicusa.com', '09:00:00', '15:00:00'),

('Laura', 'Martinez', 'Gynecology', '3055556677', 'laura.martinez@clinicusa.com', '10:00:00', '18:00:00'),

('James', 'Anderson', 'General Medicine', '2145559900', 'james.anderson@clinicusa.com', '08:30:00', '16:30:00');




CREATE TABLE Appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
);


ALTER TABLE Appointments
ADD CONSTRAINT unique_doctor_time
UNIQUE (doctor_id, appointment_date, appointment_time);


CREATE TABLE MedicalRecords (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT NOT NULL,
    diagnosis TEXT,
    treatment_notes TEXT,
    blood_pressure VARCHAR(20),
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id),
    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id)
);


CREATE TABLE Prescriptions (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT NOT NULL,
    medicine_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100),
    duration VARCHAR(100),
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (record_id) REFERENCES MedicalRecords(record_id)
);

CREATE TABLE Billing (
    bill_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    consultation_fee DECIMAL(10,2) NOT NULL,
    medicine_charges DECIMAL(10,2) DEFAULT 0.00,
    lab_charges DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) GENERATED ALWAYS AS 
        (consultation_fee + medicine_charges + lab_charges) STORED,
    payment_status VARCHAR(20) DEFAULT 'Pending',
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id),
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL
);

SELECT patient_id, first_name, last_name FROM Patients;
SELECT doctor_id, first_name, last_name, specialization FROM Doctors;


INSERT INTO Appointments
(patient_id, doctor_id, appointment_date, appointment_time)
VALUES
(1, 1, '2026-02-01', '10:00:00');

INSERT INTO Appointments
(patient_id, doctor_id, appointment_date, appointment_time)
VALUES
(2, 2, '2026-02-01', '14:30:00');

INSERT INTO Appointments
(patient_id, doctor_id, appointment_date, appointment_time)
VALUES
(3, 3, '2026-02-02', '11:00:00');


SELECT 
    a.appointment_id,
    p.first_name AS patient,
    d.first_name AS doctor,
    d.specialization,
    a.appointment_date,
    a.appointment_time,
    a.status
FROM Appointments a
JOIN Patients p ON a.patient_id = p.patient_id
JOIN Doctors d ON a.doctor_id = d.doctor_id;


INSERT INTO Appointments
(patient_id, doctor_id, appointment_date, appointment_time)
VALUES
(2, 1, '2026-02-01', '10:00:00');

SELECT appointment_id, patient_id, doctor_id, appointment_date, appointment_time, status
FROM Appointments
ORDER BY appointment_date, appointment_time;

UPDATE Appointments
SET status = 'Completed'
WHERE appointment_id = 1;

SELECT appointment_id, status
FROM Appointments
WHERE appointment_id = 1;

UPDATE Appointments
SET status = 'Cancelled'
WHERE appointment_id = 2;

SELECT appointment_id, status
FROM Appointments
WHERE appointment_id = 2;



SELECT doctor_id, COUNT(*) AS total_appointments
FROM Appointments
GROUP BY doctor_id
ORDER BY total_appointments DESC;

SELECT appointment_date, COUNT(*) AS total
FROM Appointments
GROUP BY appointment_date
ORDER BY appointment_date;


SELECT d.specialization, COUNT(*) AS total
FROM Appointments a
JOIN Doctors d ON a.doctor_id = d.doctor_id
GROUP BY d.specialization
ORDER BY total DESC;


SELECT status, COUNT(*) AS total
FROM Appointments
GROUP BY status;

SELECT 
  CONCAT(d.first_name,' ',d.last_name) AS doctor_name,
  d.specialization,
  COUNT(*) AS total
FROM Appointments a
JOIN Doctors d ON a.doctor_id = d.doctor_id
GROUP BY doctor_name, d.specialization
ORDER BY total DESC;

