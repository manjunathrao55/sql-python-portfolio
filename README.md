# 🗄️ SQL + Python Portfolio Projects
###  By [Manjunath Rao A]

---

## 📦 Setup (Run Once)
```bash
pip install pandas openpyxl
```

---

## 🏥 Project 1 — Hospital Patient Analytics System
**Field:** Life Science / Healthcare  
**File:** `hospital_analytics.py`

### What It Does
- Manages patients, doctors, diagnoses, medications and prescriptions
- Runs 8 real-world analytics queries hospitals actually use
- Exports a multi-sheet Excel report automatically

### Tables
| Table | Purpose |
|-------|---------|
| doctors | Doctor info, specialization |
| patients | Patient records, admission/discharge |
| diagnoses | Disease, severity per patient |
| medications | Drug catalogue |
| prescriptions | Which patient gets which drug |

### SQL Concepts Demonstrated
- INNER JOIN / LEFT JOIN across 4 tables
- GROUP BY + COUNT + AVG + SUM
- CASE WHEN for conditional columns
- WHERE IS NULL / IS NOT NULL
- Subqueries inside SELECT
- Date arithmetic with julianday()

### How to Run
```bash
python hospital_analytics.py
```
**Output:** `hospital_analytics_report.xlsx` (8 sheets)

---

## 📦 Project 2 — Sales Performance Dashboard
**Field:** Retail / E-Commerce / Business Analytics  
**File:** `sales_dashboard.py`

### What It Does
- Tracks products, customers, orders and order items
- Calculates revenue after discounts
- Shows top products, top customers, monthly trends
- Identifies low-stock products automatically

### Tables
| Table | Purpose |
|-------|---------|
| categories | Product categories |
| products | Product catalogue with stock |
| customers | Customer details |
| orders | Order header (date, status) |
| order_items | Line items per order |

### SQL Concepts Demonstrated
- 4-table JOIN in a single query
- CTE (WITH clause) for readable complex queries
- Window function (SUM OVER()) for percentage
- HAVING for filtering aggregated results
- strftime() for monthly grouping
- Calculated columns (revenue after discount)

### How to Run
```bash
python sales_dashboard.py
```
**Output:** `sales_dashboard_report.xlsx` (8 sheets)

---

## 👥 Project 3 — Employee Attendance & HR Tracker
**Field:** Corporate HR / People Analytics  
**File:** `hr_tracker.py`

### What It Does
- Tracks employees, departments, daily attendance, leaves
- Calculates attendance % per employee and department
- Flags high-absenteeism employees automatically
- Generates salary analysis and leave balance report

### Tables
| Table | Purpose |
|-------|---------|
| departments | Department info |
| employees | Employee directory |
| attendance | Daily check-in/check-out records |
| leaves | Leave applications |

### SQL Concepts Demonstrated
- Multi-column GROUP BY
- HAVING clause for business rules
- LEFT JOIN for employees with no leaves
- CASE WHEN inside SUM (pivot-style)
- Calculated columns (attendance %, absence rate)
- strftime() for monthly trends

### How to Run
```bash
python hr_tracker.py
```
**Output:** `hr_analytics_report.xlsx` (7 sheets)

---

## 💡 Key Skills Shown Across All Projects

| Skill | Where Used |
|-------|-----------|
| Database Design | All 3 projects — 4-5 tables each with FK |
| SQL JOINs | All queries across 2–4 tables |
| GROUP BY + HAVING | Projects 2 & 3 |
| Window Functions | Project 2 |
| CTEs (WITH clause) | Project 2 |
| Python + SQLite | All 3 |
| Pandas DataFrames | All 3 |
| Excel Automation | All 3 (openpyxl) |
| CASE WHEN logic | All 3 |
| Date Functions | Projects 1, 2, 3 |
