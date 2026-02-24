CREATE TABLE `PATIENT` (
  `Patient_ID` integer PRIMARY KEY,
  `Name` varchar(255),
  `Date_of_Birth` timestamp,
  `Gender` varchar(255),
  `Phone_Number` varchar(255),
  `Email` varchar(255)
);

CREATE TABLE `DOCTOR` (
  `Doctor_ID` integer PRIMARY KEY,
  `Name` varchar(255),
  `Specialization` varchar(255),
  `Phone_Number` varchar(255),
  `Email` varchar(255),
  `Available_Time` timestamp
);

CREATE TABLE `APPOINTMENT` (
  `Appointment_ID` integer PRIMARY KEY,
  `Patient_ID` integer,
  `Doctor_ID` integer,
  `Date` timestamp,
  `Time` timestamp,
  `Status` varchar(255)
);

CREATE TABLE `MEDICAL_RECORDS` (
  `Record_ID` integer PRIMARY KEY,
  `Appointment_ID` integer,
  `Doctor_ID` integer,
  `Patient_ID` integer,
  `Diagnoses` text,
  `Notes` text,
  `Weight` integer,
  `Height` integer,
  `Blood_Pressure` integer
);

CREATE TABLE `BILLING` (
  `Bill_ID` integer PRIMARY KEY,
  `Patient_ID` integer,
  `Appointment_ID` integer,
  `Consultation_Fee` integer,
  `Medicine_Charges` integer,
  `Lab_Charges` integer,
  `Total_Amount` integer,
  `Payment_Status` integer,
  `Payment_Method` varchar(255)
);

CREATE TABLE `PRESCRIPTION` (
  `Prescription_ID` integer PRIMARY KEY,
  `Record_ID` integer,
  `Medication_Name` varchar(255),
  `Dosage` varchar(255),
  `Duration` varchar(255)
);

ALTER TABLE `APPOINTMENT` ADD FOREIGN KEY (`Patient_ID`) REFERENCES `PATIENT` (`Patient_ID`);

ALTER TABLE `APPOINTMENT` ADD FOREIGN KEY (`Doctor_ID`) REFERENCES `DOCTOR` (`Doctor_ID`);

ALTER TABLE `MEDICAL_RECORDS` ADD FOREIGN KEY (`Appointment_ID`) REFERENCES `APPOINTMENT` (`Appointment_ID`);

ALTER TABLE `MEDICAL_RECORDS` ADD FOREIGN KEY (`Doctor_ID`) REFERENCES `DOCTOR` (`Doctor_ID`);

ALTER TABLE `MEDICAL_RECORDS` ADD FOREIGN KEY (`Patient_ID`) REFERENCES `PATIENT` (`Patient_ID`);

ALTER TABLE `BILLING` ADD FOREIGN KEY (`Patient_ID`) REFERENCES `PATIENT` (`Patient_ID`);

ALTER TABLE `BILLING` ADD FOREIGN KEY (`Appointment_ID`) REFERENCES `APPOINTMENT` (`Appointment_ID`);

ALTER TABLE `PRESCRIPTION` ADD FOREIGN KEY (`Record_ID`) REFERENCES `MEDICAL_RECORDS` (`Record_ID`);
