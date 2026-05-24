"""
============================================================
  👥 EMPLOYEE ATTENDANCE & HR ANALYTICS SYSTEM
  Built with: Python + SQLite + Pandas
  Author: [Your Name]
  Purpose: Track employee attendance, leaves, and performance
============================================================

WHAT THIS PROJECT DOES:
  - Tracks employee info, departments, attendance records
  - Analyzes leave patterns, late arrivals, absent days
  - Calculates monthly attendance percentage per employee
  - Identifies top performers and absenteeism risks
  - Generates an HR report automatically

SQL CONCEPTS USED:
  - Multi-table JOINs
  - CASE WHEN for conditional columns
  - GROUP BY + HAVING (filter absenteeism)
  - Subqueries inside SELECT
  - ROUND, AVG, COUNT, SUM
  - Date filtering with WHERE
  - CTEs (WITH clause) for readable queries
"""

import sqlite3
import pandas as pd

# ─────────────────────────────────────────────
# STEP 1: CONNECT
# ─────────────────────────────────────────────
conn = sqlite3.connect("hr_tracker.db")
cursor = conn.cursor()
print("✅ Connected to HR Tracker Database")

# ─────────────────────────────────────────────
# STEP 2: CREATE TABLES
# ─────────────────────────────────────────────
cursor.executescript("""
    DROP TABLE IF EXISTS attendance;
    DROP TABLE IF EXISTS leaves;
    DROP TABLE IF EXISTS employees;
    DROP TABLE IF EXISTS departments;

    CREATE TABLE departments (
        dept_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name   TEXT NOT NULL,
        manager     TEXT,
        location    TEXT
    );

    CREATE TABLE employees (
        emp_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT NOT NULL,
        designation     TEXT NOT NULL,
        dept_id         INTEGER,
        salary          REAL,
        join_date       TEXT,
        email           TEXT UNIQUE,
        employment_type TEXT CHECK(employment_type IN ('Full-time','Part-time','Contract')),
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    );

    CREATE TABLE attendance (
        att_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id      INTEGER NOT NULL,
        date        TEXT NOT NULL,
        check_in    TEXT,
        check_out   TEXT,
        status      TEXT CHECK(status IN ('Present','Absent','Half-day','Work-from-home')),
        late_arrival INTEGER DEFAULT 0,  -- 1 if late, 0 if on time
        FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
    );

    CREATE TABLE leaves (
        leave_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id      INTEGER NOT NULL,
        leave_type  TEXT CHECK(leave_type IN ('Sick','Casual','Earned','Maternity','Unpaid')),
        start_date  TEXT NOT NULL,
        end_date    TEXT NOT NULL,
        days_taken  INTEGER NOT NULL,
        status      TEXT CHECK(status IN ('Approved','Rejected','Pending')),
        FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
    );
""")
conn.commit()
print("✅ Tables Created (departments, employees, attendance, leaves)")

# ─────────────────────────────────────────────
# STEP 3: INSERT DATA
# ─────────────────────────────────────────────
cursor.executemany(
    "INSERT INTO departments (dept_name, manager, location) VALUES (?,?,?)",
    [
        ("Engineering",    "Rajesh Kumar",   "Bangalore"),
        ("Sales",          "Priya Nair",     "Mumbai"),
        ("HR",             "Sunita Sharma",  "Delhi"),
        ("Finance",        "Amit Verma",     "Mumbai"),
        ("Operations",     "Kiran Reddy",    "Hyderabad"),
    ]
)

cursor.executemany(
    "INSERT INTO employees (name, designation, dept_id, salary, join_date, email, employment_type) VALUES (?,?,?,?,?,?,?)",
    [
        ("Arjun Mehta",    "Software Engineer",    1, 75000, "2022-01-15", "arjun@co.in",   "Full-time"),
        ("Priya Sharma",   "Senior Developer",     1, 95000, "2021-03-10", "priya@co.in",   "Full-time"),
        ("Rohan Desai",    "Sales Executive",      2, 45000, "2022-06-01", "rohan@co.in",   "Full-time"),
        ("Neha Gupta",     "Sales Manager",        2, 80000, "2020-09-15", "neha@co.in",    "Full-time"),
        ("Kavitha Iyer",   "HR Executive",         3, 50000, "2023-01-10", "kavitha@co.in", "Full-time"),
        ("Suresh Patil",   "Finance Analyst",      4, 60000, "2021-11-20", "suresh@co.in",  "Full-time"),
        ("Anita Rao",      "Operations Lead",      5, 70000, "2020-05-05", "anita@co.in",   "Full-time"),
        ("Vikram Singh",   "DevOps Engineer",      1, 85000, "2022-08-12", "vikram@co.in",  "Full-time"),
        ("Meena Joshi",    "Data Analyst",         4, 65000, "2023-03-01", "meena@co.in",   "Full-time"),
        ("Deepak Kumar",   "Sales Executive",      2, 42000, "2023-06-15", "deepak@co.in",  "Contract"),
    ]
)

# Generate attendance for Jan–Mar 2024
attendance_data = []
import_dates = [
    "2024-01-02","2024-01-03","2024-01-04","2024-01-05","2024-01-08",
    "2024-01-09","2024-01-10","2024-01-11","2024-01-12","2024-01-15",
    "2024-01-16","2024-01-17","2024-01-18","2024-01-19","2024-01-22",
    "2024-02-01","2024-02-02","2024-02-05","2024-02-06","2024-02-07",
    "2024-02-08","2024-02-09","2024-02-12","2024-02-13","2024-02-14",
    "2024-03-01","2024-03-04","2024-03-05","2024-03-06","2024-03-07",
]

# Status patterns per employee (0=Present, 1=Absent, 2=Half-day, 3=WFH)
emp_patterns = {
    1: [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],  # Perfect attendance
    2: [0,0,0,0,0, 0,0,0,3,0, 0,0,0,0,0, 0,0,3,0,0, 0,0,0,0,0, 0,0,0,0,3],  # Some WFH
    3: [0,0,1,0,0, 0,0,0,0,0, 0,1,0,0,0, 0,0,0,0,1, 0,0,0,0,0, 0,0,1,0,0],  # Frequent absent
    4: [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],  # Perfect
    5: [0,0,0,0,2, 0,0,0,0,0, 0,0,0,0,0, 1,0,0,0,0, 0,0,0,0,2, 0,0,0,0,0],  # Some half-days
    6: [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],  # Perfect
    7: [0,0,0,0,0, 3,0,0,0,0, 3,0,0,0,0, 0,0,3,0,0, 0,3,0,0,0, 0,0,0,3,0],  # Lot of WFH
    8: [0,1,0,0,0, 0,0,1,0,0, 0,0,0,1,0, 0,0,0,0,0, 1,0,0,0,0, 0,0,0,0,1],  # Some absent
    9: [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],  # Perfect
    10:[0,0,1,0,1, 0,0,0,1,0, 0,0,1,0,0, 1,0,0,0,1, 0,0,0,1,0, 0,1,0,0,0],  # Most absent
}
late_map = {1:[0]*30, 2:[0]*30, 3:[0]*30, 4:[0]*30,
            5:[0,0,1,0,0, 0,0,0,0,1, 0,0,0,0,0, 0,1,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
            6:[0]*30, 7:[0]*30,
            8:[0,0,0,0,0, 0,0,0,1,0, 0,0,0,0,1, 0,0,0,0,0, 0,0,1,0,0, 0,0,0,0,0],
            9:[0]*30, 10:[0]*30}

status_map = {0:"Present", 1:"Absent", 2:"Half-day", 3:"Work-from-home"}
checkin_map = {0:"09:00", 2:"09:00", 3:"09:00"}

for emp_id, pattern in emp_patterns.items():
    for i, (date, status_code) in enumerate(zip(import_dates, pattern)):
        if status_code == 1:
            attendance_data.append((emp_id, date, None, None, "Absent", 0))
        else:
            checkin = checkin_map.get(status_code, "09:00")
            late = late_map[emp_id][i] if emp_id in late_map else 0
            if late:
                checkin = "09:35"
            checkout = "18:00" if status_code != 2 else "13:00"
            attendance_data.append((emp_id, date, checkin, checkout, status_map[status_code], late))

cursor.executemany(
    "INSERT INTO attendance (emp_id, date, check_in, check_out, status, late_arrival) VALUES (?,?,?,?,?,?)",
    attendance_data
)

cursor.executemany(
    "INSERT INTO leaves (emp_id, leave_type, start_date, end_date, days_taken, status) VALUES (?,?,?,?,?,?)",
    [
        (3,  "Sick",     "2024-01-03", "2024-01-03", 1,  "Approved"),
        (3,  "Casual",   "2024-01-12", "2024-01-12", 1,  "Approved"),
        (5,  "Earned",   "2024-01-05", "2024-01-05", 1,  "Approved"),
        (8,  "Sick",     "2024-01-02", "2024-01-02", 1,  "Approved"),
        (10, "Casual",   "2024-01-03", "2024-01-04", 2,  "Approved"),
        (10, "Sick",     "2024-01-05", "2024-01-05", 1,  "Approved"),
        (3,  "Casual",   "2024-02-06", "2024-02-06", 1,  "Approved"),
        (10, "Casual",   "2024-02-08", "2024-02-08", 1,  "Rejected"),
        (8,  "Casual",   "2024-03-01", "2024-03-01", 1,  "Pending"),
        (2,  "Maternity","2024-04-01", "2024-06-30", 90, "Approved"),
    ]
)

conn.commit()
print(f"✅ Data Inserted (10 employees, 5 departments, {len(attendance_data)} attendance records)")

# ─────────────────────────────────────────────
# STEP 4: HR ANALYTICS QUERIES
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("      📊 HR ANALYTICS DASHBOARD")
print("="*60)

# ── QUERY 1: Employee + Department Overview
print("\n🔹 QUERY 1: Full Employee Directory with Department")
print("   SQL Concept: JOIN 2 tables + CASE WHEN for experience")
q1 = pd.read_sql_query("""
    SELECT
        e.emp_id,
        e.name,
        e.designation,
        d.dept_name,
        e.salary,
        e.employment_type,
        e.join_date,
        ROUND((julianday('now') - julianday(e.join_date)) / 365.0, 1) AS years_experience
    FROM employees e
    INNER JOIN departments d ON e.dept_id = d.dept_id
    ORDER BY e.salary DESC;
""", conn)
print(q1.to_string(index=False))

# ── QUERY 2: Attendance Summary Per Employee
print("\n🔹 QUERY 2: Attendance Summary (Jan–Mar 2024)")
print("   SQL Concept: GROUP BY + COUNT + CASE + calculated attendance %")
q2 = pd.read_sql_query("""
    SELECT
        e.name,
        d.dept_name,
        COUNT(a.att_id)   AS total_working_days,
        SUM(CASE WHEN a.status = 'Present'        THEN 1 ELSE 0 END) AS present,
        SUM(CASE WHEN a.status = 'Absent'         THEN 1 ELSE 0 END) AS absent,
        SUM(CASE WHEN a.status = 'Half-day'       THEN 1 ELSE 0 END) AS half_days,
        SUM(CASE WHEN a.status = 'Work-from-home' THEN 1 ELSE 0 END) AS wfh,
        SUM(a.late_arrival) AS late_arrivals,
        ROUND(
            (SUM(CASE WHEN a.status != 'Absent' THEN 1 ELSE 0 END) * 100.0) / COUNT(a.att_id), 2
        ) AS attendance_pct
    FROM employees e
    INNER JOIN departments d ON e.dept_id = d.dept_id
    INNER JOIN attendance a   ON e.emp_id  = a.emp_id
    GROUP BY e.emp_id
    ORDER BY attendance_pct DESC;
""", conn)
print(q2.to_string(index=False))

# ── QUERY 3: Department-wise Attendance
print("\n🔹 QUERY 3: Department-wise Attendance Comparison")
print("   SQL Concept: 3-table JOIN + GROUP BY department")
q3 = pd.read_sql_query("""
    SELECT
        d.dept_name,
        COUNT(DISTINCT e.emp_id) AS headcount,
        ROUND(AVG(
            CASE WHEN a.status != 'Absent' THEN 1.0 ELSE 0.0 END
        ) * 100, 2) AS avg_attendance_pct,
        SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS total_absences,
        ROUND(AVG(e.salary), 0) AS avg_salary
    FROM departments d
    INNER JOIN employees e  ON d.dept_id  = e.dept_id
    INNER JOIN attendance a ON e.emp_id   = a.emp_id
    GROUP BY d.dept_id
    ORDER BY avg_attendance_pct DESC;
""", conn)
print(q3.to_string(index=False))

# ── QUERY 4: Absenteeism Alert
print("\n🔹 QUERY 4: ⚠️  High Absenteeism Alert (>3 absences)")
print("   SQL Concept: GROUP BY + HAVING (only show problem employees)")
q4 = pd.read_sql_query("""
    SELECT
        e.name,
        e.designation,
        d.dept_name,
        COUNT(CASE WHEN a.status = 'Absent' THEN 1 END) AS total_absences,
        COUNT(CASE WHEN a.late_arrival = 1 THEN 1 END)  AS late_arrivals,
        ROUND(
            COUNT(CASE WHEN a.status='Absent' THEN 1 END) * 100.0 / COUNT(a.att_id), 1
        ) AS absence_rate_pct
    FROM employees e
    JOIN departments d ON e.dept_id = d.dept_id
    JOIN attendance a  ON e.emp_id  = a.emp_id
    GROUP BY e.emp_id
    HAVING total_absences > 3
    ORDER BY total_absences DESC;
""", conn)
print(q4.to_string(index=False))

# ── QUERY 5: Monthly Attendance Trend
print("\n🔹 QUERY 5: Month-wise Attendance Trend")
print("   SQL Concept: strftime + GROUP BY month")
q5 = pd.read_sql_query("""
    SELECT
        strftime('%Y-%m', a.date) AS month,
        COUNT(*)          AS total_records,
        SUM(CASE WHEN a.status = 'Present'        THEN 1 ELSE 0 END) AS present,
        SUM(CASE WHEN a.status = 'Absent'         THEN 1 ELSE 0 END) AS absent,
        SUM(CASE WHEN a.status = 'Work-from-home' THEN 1 ELSE 0 END) AS wfh,
        ROUND(
            SUM(CASE WHEN a.status != 'Absent' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
        ) AS attendance_pct
    FROM attendance a
    GROUP BY month
    ORDER BY month;
""", conn)
print(q5.to_string(index=False))

# ── QUERY 6: Leave Balance Report
print("\n🔹 QUERY 6: Leave Usage by Employee")
print("   SQL Concept: LEFT JOIN + GROUP BY + SUM")
q6 = pd.read_sql_query("""
    SELECT
        e.name,
        d.dept_name,
        SUM(CASE WHEN l.leave_type='Sick'   AND l.status='Approved' THEN l.days_taken ELSE 0 END) AS sick_leaves,
        SUM(CASE WHEN l.leave_type='Casual' AND l.status='Approved' THEN l.days_taken ELSE 0 END) AS casual_leaves,
        SUM(CASE WHEN l.leave_type='Earned' AND l.status='Approved' THEN l.days_taken ELSE 0 END) AS earned_leaves,
        SUM(CASE WHEN l.status='Approved'                            THEN l.days_taken ELSE 0 END) AS total_leaves_taken,
        COUNT(CASE WHEN l.status='Pending'  THEN 1 END)                                            AS pending_approvals
    FROM employees e
    LEFT JOIN departments d ON e.dept_id = d.dept_id
    LEFT JOIN leaves l      ON e.emp_id  = l.emp_id
    GROUP BY e.emp_id
    ORDER BY total_leaves_taken DESC;
""", conn)
print(q6.to_string(index=False))

# ── QUERY 7: Salary Analysis by Department
print("\n🔹 QUERY 7: Department Salary Analysis")
print("   SQL Concept: GROUP BY + MIN/MAX/AVG + SUM")
q7 = pd.read_sql_query("""
    SELECT
        d.dept_name,
        COUNT(e.emp_id)         AS employee_count,
        ROUND(MIN(e.salary), 0) AS min_salary,
        ROUND(MAX(e.salary), 0) AS max_salary,
        ROUND(AVG(e.salary), 0) AS avg_salary,
        ROUND(SUM(e.salary), 0) AS total_payroll
    FROM departments d
    INNER JOIN employees e ON d.dept_id = e.dept_id
    GROUP BY d.dept_id
    ORDER BY total_payroll DESC;
""", conn)
print(q7.to_string(index=False))

# ─────────────────────────────────────────────
# STEP 5: EXPORT TO EXCEL
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("   📁 EXPORTING HR REPORT TO EXCEL")
print("="*60)

output_file = "hr_analytics_report.xlsx"
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    q1.to_excel(writer, sheet_name="Employee_Directory",    index=False)
    q2.to_excel(writer, sheet_name="Attendance_Summary",    index=False)
    q3.to_excel(writer, sheet_name="Dept_Attendance",       index=False)
    q4.to_excel(writer, sheet_name="Absenteeism_Alert",     index=False)
    q5.to_excel(writer, sheet_name="Monthly_Trend",         index=False)
    q6.to_excel(writer, sheet_name="Leave_Report",          index=False)
    q7.to_excel(writer, sheet_name="Salary_Analysis",       index=False)

print(f"✅ HR Report Saved: {output_file}")

# SUMMARY
total_emp = cursor.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
avg_att   = pd.read_sql_query("""
    SELECT ROUND(SUM(CASE WHEN status != 'Absent' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct
    FROM attendance
""", conn)["pct"][0]

print("\n" + "="*60)
print("   📈 HR SUMMARY")
print("="*60)
print(f"  👥 Total Employees         : {total_emp}")
print(f"  📊 Overall Attendance %    : {avg_att}%")
print(f"  ⚠️  High Absenteeism Risk   : {len(q4)} employees")
print(f"  🏆 Best Attendance Dept    : {q3['dept_name'][0]} ({q3['avg_attendance_pct'][0]}%)")
print(f"  💰 Highest Avg Salary Dept : {q7['dept_name'][0]} (₹{q7['avg_salary'][0]:,.0f}/month)")

conn.close()
print("\n✅ HR Tracker Project Complete!")
print("="*60)
