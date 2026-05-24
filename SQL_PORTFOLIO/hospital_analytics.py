"""
============================================================
  🏥 HOSPITAL PATIENT ANALYTICS SYSTEM
  Built with: Python + SQLite
  Author: [Your Name]
  Purpose: Manage and analyze patient data for a hospital
============================================================

WHAT THIS PROJECT DOES:
  - Stores patient records, doctor info, diagnoses, and medications
  - Runs real-world analytics that hospitals actually need
  - Generates a CSV report automatically (Python Automation!)

SQL CONCEPTS USED:
  - CREATE TABLE, INSERT, SELECT
  - JOINs (INNER JOIN, LEFT JOIN)
  - GROUP BY, ORDER BY, HAVING
  - Aggregate functions (COUNT, AVG, MAX, MIN)
  - Subqueries
  - WHERE with multiple conditions
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

# ─────────────────────────────────────────────
# STEP 1: CONNECT TO DATABASE
# ─────────────────────────────────────────────
# SQLite creates a local .db file — no server needed!
conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()
print("✅ Connected to Hospital Database")

# ─────────────────────────────────────────────
# STEP 2: CREATE TABLES
# ─────────────────────────────────────────────
# This is our DATABASE DESIGN — the most important skill to show!
# 4 tables, all connected through foreign keys

cursor.executescript("""
    -- Drop tables if they exist (for clean re-run)
    DROP TABLE IF EXISTS prescriptions;
    DROP TABLE IF EXISTS diagnoses;
    DROP TABLE IF EXISTS patients;
    DROP TABLE IF EXISTS doctors;
    DROP TABLE IF EXISTS medications;

    -- DOCTORS TABLE
    CREATE TABLE doctors (
        doctor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        specialization TEXT NOT NULL,
        department  TEXT NOT NULL,
        experience_years INTEGER
    );

    -- PATIENTS TABLE
    CREATE TABLE patients (
        patient_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        age         INTEGER NOT NULL,
        gender      TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
        blood_group TEXT,
        city        TEXT,
        admission_date TEXT,
        discharge_date TEXT,
        doctor_id   INTEGER,
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    );

    -- DIAGNOSES TABLE
    CREATE TABLE diagnoses (
        diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id   INTEGER NOT NULL,
        disease_name TEXT NOT NULL,
        severity     TEXT CHECK(severity IN ('Mild', 'Moderate', 'Severe')),
        diagnosed_date TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    );

    -- MEDICATIONS TABLE
    CREATE TABLE medications (
        medication_id INTEGER PRIMARY KEY AUTOINCREMENT,
        drug_name   TEXT NOT NULL,
        category    TEXT NOT NULL,
        manufacturer TEXT
    );

    -- PRESCRIPTIONS TABLE (links patients to medications)
    CREATE TABLE prescriptions (
        prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id  INTEGER NOT NULL,
        medication_id INTEGER NOT NULL,
        dosage      TEXT,
        duration_days INTEGER,
        prescribed_date TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (medication_id) REFERENCES medications(medication_id)
    );
""")
conn.commit()
print("✅ All Tables Created (doctors, patients, diagnoses, medications, prescriptions)")

# ─────────────────────────────────────────────
# STEP 3: INSERT SAMPLE DATA
# ─────────────────────────────────────────────

# Insert Doctors
doctors_data = [
    ("Dr. Ramesh Sharma",    "Cardiology",     "Heart & Vascular",  15),
    ("Dr. Priya Nair",       "Endocrinology",  "Diabetes & Hormones", 10),
    ("Dr. Arjun Mehta",      "Neurology",      "Brain & Nerves",    12),
    ("Dr. Sunita Rao",       "Oncology",       "Cancer Care",       20),
    ("Dr. Vikram Patel",     "General Medicine","General Ward",      8),
    ("Dr. Kavitha Iyer",     "Pulmonology",    "Respiratory",        7),
]
cursor.executemany(
    "INSERT INTO doctors (name, specialization, department, experience_years) VALUES (?,?,?,?)",
    doctors_data
)

# Insert Patients
patients_data = [
    ("Anita Desai",     55, "Female", "B+", "Mumbai",    "2024-01-10", "2024-01-20", 1),
    ("Ramkumar S",      63, "Male",   "O+", "Chennai",   "2024-01-12", "2024-01-25", 2),
    ("Meena Joshi",     45, "Female", "A+", "Pune",      "2024-02-01", "2024-02-10", 2),
    ("Suresh Patil",    70, "Male",   "AB+","Bangalore",  "2024-02-05", None,         1),
    ("Deepa Krishnan",  38, "Female", "O-", "Hyderabad", "2024-02-14", "2024-02-20", 3),
    ("Ajay Kumar",      50, "Male",   "B-", "Delhi",     "2024-03-01", "2024-03-10", 4),
    ("Shalini Verma",   42, "Female", "A-", "Jaipur",    "2024-03-05", "2024-03-15", 5),
    ("Mohan Das",       68, "Male",   "O+", "Kolkata",   "2024-03-10", None,         6),
    ("Radha Iyengar",   57, "Female", "B+", "Chennai",   "2024-03-20", "2024-03-30", 1),
    ("Kiran Shah",      35, "Male",   "A+", "Mumbai",    "2024-04-01", "2024-04-07", 5),
    ("Nalini Reddy",    60, "Female", "O+", "Bangalore", "2024-04-05", None,         2),
    ("Prakash Nair",    48, "Male",   "B+", "Kochi",     "2024-04-10", "2024-04-18", 3),
    ("Geeta Sharma",    52, "Female", "AB-","Lucknow",   "2024-04-15", "2024-04-25", 4),
    ("Harish Gupta",    44, "Male",   "A+", "Indore",    "2024-05-01", "2024-05-08", 5),
    ("Pooja Wadia",     30, "Female", "O+", "Surat",     "2024-05-05", "2024-05-10", 6),
]
cursor.executemany(
    "INSERT INTO patients (name, age, gender, blood_group, city, admission_date, discharge_date, doctor_id) VALUES (?,?,?,?,?,?,?,?)",
    patients_data
)

# Insert Diagnoses
diagnoses_data = [
    (1,  "Hypertension",       "Moderate", "2024-01-10"),
    (2,  "Type 2 Diabetes",    "Moderate", "2024-01-12"),
    (3,  "Type 2 Diabetes",    "Mild",     "2024-02-01"),
    (4,  "Coronary Artery Disease", "Severe", "2024-02-05"),
    (5,  "Migraine",           "Moderate", "2024-02-14"),
    (6,  "Lung Cancer",        "Severe",   "2024-03-01"),
    (7,  "Anemia",             "Mild",     "2024-03-05"),
    (8,  "Chronic Bronchitis", "Moderate", "2024-03-10"),
    (9,  "Hypertension",       "Severe",   "2024-03-20"),
    (10, "Viral Fever",        "Mild",     "2024-04-01"),
    (11, "Type 2 Diabetes",    "Severe",   "2024-04-05"),
    (12, "Epilepsy",           "Moderate", "2024-04-10"),
    (13, "Breast Cancer",      "Severe",   "2024-04-15"),
    (14, "Hypertension",       "Mild",     "2024-05-01"),
    (15, "Asthma",             "Moderate", "2024-05-05"),
]
cursor.executemany(
    "INSERT INTO diagnoses (patient_id, disease_name, severity, diagnosed_date) VALUES (?,?,?,?)",
    diagnoses_data
)

# Insert Medications
medications_data = [
    ("Metformin",    "Antidiabetic",   "Sun Pharma"),
    ("Amlodipine",   "Antihypertensive","Cipla"),
    ("Atorvastatin", "Statin",         "Ranbaxy"),
    ("Sumatriptan",  "Antimigraine",   "GSK"),
    ("Paracetamol",  "Analgesic",      "Himalaya"),
    ("Salbutamol",   "Bronchodilator", "Cipla"),
    ("Levetiracetam","Antiepileptic",  "Sun Pharma"),
    ("Iron Sucrose", "Iron Supplement","Glenmark"),
    ("Lisinopril",   "Antihypertensive","Lupin"),
    ("Docetaxel",    "Chemotherapy",   "Sanofi"),
]
cursor.executemany(
    "INSERT INTO medications (drug_name, category, manufacturer) VALUES (?,?,?)",
    medications_data
)

# Insert Prescriptions
prescriptions_data = [
    (1,  2,  "5mg daily",    30,  "2024-01-10"),
    (2,  1,  "500mg twice",  90,  "2024-01-12"),
    (3,  1,  "500mg once",   60,  "2024-02-01"),
    (4,  9,  "10mg daily",   30,  "2024-02-05"),
    (4,  3,  "20mg daily",   60,  "2024-02-05"),
    (5,  4,  "50mg as needed",10, "2024-02-14"),
    (6,  10, "75mg/m2",      21,  "2024-03-01"),
    (7,  8,  "200mg daily",  30,  "2024-03-05"),
    (8,  6,  "2 puffs TDS",  14,  "2024-03-10"),
    (9,  2,  "10mg daily",   30,  "2024-03-20"),
    (9,  9,  "10mg daily",   30,  "2024-03-20"),
    (10, 5,  "500mg TDS",    5,   "2024-04-01"),
    (11, 1,  "1000mg twice", 90,  "2024-04-05"),
    (12, 7,  "500mg twice",  180, "2024-04-10"),
    (13, 10, "100mg/m2",     21,  "2024-04-15"),
    (14, 2,  "5mg daily",    30,  "2024-05-01"),
    (15, 6,  "100mcg TDS",   30,  "2024-05-05"),
]
cursor.executemany(
    "INSERT INTO prescriptions (patient_id, medication_id, dosage, duration_days, prescribed_date) VALUES (?,?,?,?,?)",
    prescriptions_data
)

conn.commit()
print("✅ Sample Data Inserted (15 patients, 6 doctors, 15 diagnoses, 10 medications, 17 prescriptions)")

# ─────────────────────────────────────────────
# STEP 4: RUN ANALYTICS QUERIES
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("         📊 HOSPITAL ANALYTICS REPORT")
print("="*60)

# ── QUERY 1: Patient + Doctor Overview (INNER JOIN)
print("\n🔹 QUERY 1: All Patients with Their Assigned Doctor")
print("   SQL Concept: INNER JOIN between patients and doctors")
q1 = pd.read_sql_query("""
    SELECT
        p.patient_id,
        p.name          AS patient_name,
        p.age,
        p.gender,
        p.city,
        d.name          AS doctor_name,
        d.specialization,
        p.admission_date,
        CASE
            WHEN p.discharge_date IS NULL THEN '🟡 Still Admitted'
            ELSE '✅ Discharged'
        END             AS status
    FROM patients p
    INNER JOIN doctors d ON p.doctor_id = d.doctor_id
    ORDER BY p.admission_date;
""", conn)
print(q1.to_string(index=False))

# ── QUERY 2: Most Common Diseases (GROUP BY + COUNT)
print("\n🔹 QUERY 2: Most Common Diseases in the Hospital")
print("   SQL Concept: GROUP BY + COUNT + ORDER BY")
q2 = pd.read_sql_query("""
    SELECT
        disease_name,
        COUNT(*)        AS total_cases,
        SUM(CASE WHEN severity = 'Severe'   THEN 1 ELSE 0 END) AS severe_cases,
        SUM(CASE WHEN severity = 'Moderate' THEN 1 ELSE 0 END) AS moderate_cases,
        SUM(CASE WHEN severity = 'Mild'     THEN 1 ELSE 0 END) AS mild_cases
    FROM diagnoses
    GROUP BY disease_name
    ORDER BY total_cases DESC;
""", conn)
print(q2.to_string(index=False))

# ── QUERY 3: Doctor Performance (JOIN + GROUP BY + HAVING)
print("\n🔹 QUERY 3: Doctor Workload & Performance")
print("   SQL Concept: JOIN + GROUP BY + AVG + HAVING")
q3 = pd.read_sql_query("""
    SELECT
        d.name              AS doctor_name,
        d.specialization,
        d.department,
        COUNT(p.patient_id) AS total_patients,
        ROUND(AVG(p.age), 1) AS avg_patient_age,
        SUM(CASE WHEN p.discharge_date IS NULL THEN 1 ELSE 0 END) AS current_inpatients
    FROM doctors d
    LEFT JOIN patients p ON d.doctor_id = p.doctor_id
    GROUP BY d.doctor_id
    ORDER BY total_patients DESC;
""", conn)
print(q3.to_string(index=False))

# ── QUERY 4: Average Age by Disease (real life science insight!)
print("\n🔹 QUERY 4: Average Patient Age Per Disease")
print("   SQL Concept: JOIN across 3 tables + AVG + GROUP BY")
q4 = pd.read_sql_query("""
    SELECT
        diag.disease_name,
        ROUND(AVG(p.age), 1)    AS avg_age,
        MIN(p.age)              AS youngest_patient,
        MAX(p.age)              AS oldest_patient,
        COUNT(*)                AS patient_count
    FROM diagnoses diag
    INNER JOIN patients p ON diag.patient_id = p.patient_id
    GROUP BY diag.disease_name
    ORDER BY avg_age DESC;
""", conn)
print(q4.to_string(index=False))

# ── QUERY 5: Most Prescribed Medications (JOIN 3 tables)
print("\n🔹 QUERY 5: Most Prescribed Drugs")
print("   SQL Concept: 3-table JOIN + GROUP BY + ORDER BY")
q5 = pd.read_sql_query("""
    SELECT
        m.drug_name,
        m.category,
        m.manufacturer,
        COUNT(pr.prescription_id) AS times_prescribed,
        ROUND(AVG(pr.duration_days), 0) AS avg_duration_days
    FROM medications m
    LEFT JOIN prescriptions pr ON m.medication_id = pr.medication_id
    GROUP BY m.medication_id
    ORDER BY times_prescribed DESC;
""", conn)
print(q5.to_string(index=False))

# ── QUERY 6: Currently Admitted Patients (Subquery)
print("\n🔹 QUERY 6: Patients Currently Admitted (No Discharge Yet)")
print("   SQL Concept: WHERE with NULL check + Subquery")
q6 = pd.read_sql_query("""
    SELECT
        p.name          AS patient_name,
        p.age,
        p.gender,
        d.name          AS doctor_name,
        diag.disease_name,
        diag.severity,
        p.admission_date,
        (julianday('now') - julianday(p.admission_date)) AS days_admitted
    FROM patients p
    INNER JOIN doctors d    ON p.doctor_id    = d.doctor_id
    INNER JOIN diagnoses diag ON p.patient_id = diag.patient_id
    WHERE p.discharge_date IS NULL
    ORDER BY days_admitted DESC;
""", conn)
print(q6.to_string(index=False))

# ── QUERY 7: Gender-wise Disease Summary
print("\n🔹 QUERY 7: Gender-wise Disease Summary")
print("   SQL Concept: Multi-table JOIN + GROUP BY multiple columns")
q7 = pd.read_sql_query("""
    SELECT
        p.gender,
        diag.disease_name,
        COUNT(*) AS cases,
        ROUND(AVG(p.age), 1) AS avg_age
    FROM patients p
    INNER JOIN diagnoses diag ON p.patient_id = diag.patient_id
    GROUP BY p.gender, diag.disease_name
    ORDER BY p.gender, cases DESC;
""", conn)
print(q7.to_string(index=False))

# ── QUERY 8: Severe Cases Report
print("\n🔹 QUERY 8: All Severe Cases with Full Details")
print("   SQL Concept: WHERE filter + multi-table JOIN")
q8 = pd.read_sql_query("""
    SELECT
        p.name          AS patient_name,
        p.age,
        p.city,
        diag.disease_name,
        d.name          AS treating_doctor,
        d.specialization,
        p.admission_date
    FROM patients p
    INNER JOIN diagnoses diag ON p.patient_id = diag.patient_id
    INNER JOIN doctors d      ON p.doctor_id  = d.doctor_id
    WHERE diag.severity = 'Severe'
    ORDER BY p.admission_date;
""", conn)
print(q8.to_string(index=False))

# ─────────────────────────────────────────────
# STEP 5: PYTHON AUTOMATION — EXPORT TO EXCEL
# This is the "automation" part that impresses HR!
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("   📁 EXPORTING REPORTS TO EXCEL (Python Automation)")
print("="*60)

output_file = "hospital_analytics_report.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    q1.to_excel(writer, sheet_name="Patient_Doctor_Overview",  index=False)
    q2.to_excel(writer, sheet_name="Disease_Statistics",       index=False)
    q3.to_excel(writer, sheet_name="Doctor_Workload",          index=False)
    q4.to_excel(writer, sheet_name="Age_By_Disease",           index=False)
    q5.to_excel(writer, sheet_name="Drug_Prescriptions",       index=False)
    q6.to_excel(writer, sheet_name="Current_Inpatients",       index=False)
    q7.to_excel(writer, sheet_name="Gender_Disease_Summary",   index=False)
    q8.to_excel(writer, sheet_name="Severe_Cases",             index=False)

print(f"\n✅ Excel Report Generated: {output_file}")
print("   📋 Sheets: Patient Overview, Disease Stats, Doctor Workload,")
print("            Age by Disease, Drug Usage, Current Inpatients,")
print("            Gender Summary, Severe Cases")

# ─────────────────────────────────────────────
# STEP 6: SUMMARY STATS (the "wow" moment!)
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("   📈 QUICK SUMMARY STATS")
print("="*60)

stats = pd.read_sql_query("""
    SELECT
        (SELECT COUNT(*) FROM patients)                         AS total_patients,
        (SELECT COUNT(*) FROM patients WHERE discharge_date IS NULL) AS current_inpatients,
        (SELECT COUNT(*) FROM doctors)                          AS total_doctors,
        (SELECT COUNT(*) FROM medications)                      AS total_medications,
        (SELECT ROUND(AVG(age),1) FROM patients)                AS avg_patient_age,
        (SELECT disease_name FROM diagnoses
         GROUP BY disease_name ORDER BY COUNT(*) DESC LIMIT 1)  AS most_common_disease,
        (SELECT doctors.name FROM doctors
         JOIN patients ON patients.doctor_id = doctors.doctor_id
         GROUP BY doctors.doctor_id ORDER BY COUNT(*) DESC LIMIT 1) AS busiest_doctor
""", conn)

print(f"\n  🏥 Total Patients      : {stats['total_patients'][0]}")
print(f"  🛏️  Current Inpatients  : {stats['current_inpatients'][0]}")
print(f"  👨‍⚕️  Total Doctors        : {stats['total_doctors'][0]}")
print(f"  💊 Total Medications   : {stats['total_medications'][0]}")
print(f"  📊 Avg Patient Age     : {stats['avg_patient_age'][0]} years")
print(f"  🦠 Most Common Disease : {stats['most_common_disease'][0]}")
print(f"  ⭐ Busiest Doctor      : {stats['busiest_doctor'][0]}")

conn.close()
print("\n✅ Database connection closed. Project Complete!")
print("="*60)
