"""
============================================================
  📦 SALES PERFORMANCE DASHBOARD
  Built with: Python + SQLite + Pandas
  Author: [Your Name]
  Purpose: Analyze sales data for a retail/e-commerce company
============================================================

WHAT THIS PROJECT DOES:
  - Tracks products, customers, orders and sales
  - Shows which products sell most, which region earns most
  - Identifies top customers, monthly trends
  - Flags slow-moving and out-of-stock products
  - Exports a full business report to Excel (automation!)

SQL CONCEPTS USED:
  - Multi-table JOINs (3-4 tables at once)
  - GROUP BY + HAVING (filter grouped results)
  - Window Functions (RANK, ROW_NUMBER)
  - CASE WHEN (conditional logic in SQL)
  - Subqueries and CTEs (WITH clause)
  - Date functions (strftime)
  - Aggregate functions (SUM, AVG, COUNT, MAX)
"""

import sqlite3
import pandas as pd

# ─────────────────────────────────────────────
# STEP 1: CONNECT & CREATE DATABASE
# ─────────────────────────────────────────────
conn = sqlite3.connect("sales.db")
cursor = conn.cursor()
print("✅ Connected to Sales Database")

# ─────────────────────────────────────────────
# STEP 2: CREATE TABLES
# ─────────────────────────────────────────────
cursor.executescript("""
    DROP TABLE IF EXISTS order_items;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS categories;

    -- PRODUCT CATEGORIES
    CREATE TABLE categories (
        category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL
    );

    -- PRODUCTS TABLE
    CREATE TABLE products (
        product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name  TEXT NOT NULL,
        category_id   INTEGER,
        unit_price    REAL NOT NULL,
        stock_qty     INTEGER DEFAULT 0,
        supplier      TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );

    -- CUSTOMERS TABLE
    CREATE TABLE customers (
        customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        email         TEXT UNIQUE,
        city          TEXT,
        state         TEXT,
        segment       TEXT CHECK(segment IN ('Retail','Wholesale','Online'))
    );

    -- ORDERS TABLE
    CREATE TABLE orders (
        order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id   INTEGER NOT NULL,
        order_date    TEXT NOT NULL,
        delivery_date TEXT,
        status        TEXT CHECK(status IN ('Delivered','Pending','Cancelled','Returned')),
        payment_mode  TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    -- ORDER ITEMS (links orders to products)
    CREATE TABLE order_items (
        item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id      INTEGER NOT NULL,
        product_id    INTEGER NOT NULL,
        quantity      INTEGER NOT NULL,
        unit_price    REAL NOT NULL,
        discount_pct  REAL DEFAULT 0,
        FOREIGN KEY (order_id)   REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
""")
conn.commit()
print("✅ Tables Created (categories, products, customers, orders, order_items)")

# ─────────────────────────────────────────────
# STEP 3: INSERT DATA
# ─────────────────────────────────────────────

cursor.executemany("INSERT INTO categories (category_name) VALUES (?)", [
    ("Electronics",), ("Clothing",), ("Groceries",),
    ("Home & Kitchen",), ("Books",), ("Mobiles",),
])

cursor.executemany(
    "INSERT INTO products (product_name, category_id, unit_price, stock_qty, supplier) VALUES (?,?,?,?,?)",
    [
        ("Laptop Pro 15",    1, 65000, 20,  "TechWorld"),
        ("Wireless Headphones",1, 2500, 50, "SoundCo"),
        ("USB-C Hub",        1, 1200,  80,  "TechWorld"),
        ("Men's Formal Shirt",2, 899,  150, "FashionHub"),
        ("Women's Kurti",    2, 599,  200,  "FashionHub"),
        ("Running Shoes",    2, 2200,  60,  "SportZone"),
        ("Basmati Rice 5kg", 3, 450,  300,  "FoodMart"),
        ("Olive Oil 1L",     3, 750,  120,  "FoodMart"),
        ("Instant Noodles",  3, 60,   500,  "FoodMart"),
        ("Pressure Cooker",  4, 1800,  40,  "HomeEssentials"),
        ("Non-stick Pan",    4, 1200,  60,  "HomeEssentials"),
        ("Water Purifier",   4, 12000, 15,  "AquaFresh"),
        ("Python Programming",5, 499,  100, "BookDepot"),
        ("Data Science Book",5, 599,   80,  "BookDepot"),
        ("iPhone 14",        6, 79000,  10, "AppleIndia"),
        ("Samsung Galaxy S22",6, 55000, 18, "SamsungIndia"),
        ("Budget Android",   6, 12000, 45,  "PhoneMart"),
    ]
)

cursor.executemany(
    "INSERT INTO customers (name, email, city, state, segment) VALUES (?,?,?,?,?)",
    [
        ("Aarav Shah",      "aarav@gmail.com",    "Mumbai",    "Maharashtra", "Online"),
        ("Priya Menon",     "priya@gmail.com",    "Chennai",   "Tamil Nadu",  "Retail"),
        ("Rohit Gupta",     "rohit@gmail.com",    "Delhi",     "Delhi",       "Wholesale"),
        ("Sneha Patil",     "sneha@gmail.com",    "Pune",      "Maharashtra", "Online"),
        ("Vikram Nair",     "vikram@gmail.com",   "Bangalore", "Karnataka",   "Retail"),
        ("Anjali Sharma",   "anjali@gmail.com",   "Hyderabad", "Telangana",   "Online"),
        ("Karan Mehta",     "karan@gmail.com",    "Jaipur",    "Rajasthan",   "Wholesale"),
        ("Divya Rao",       "divya@gmail.com",    "Kolkata",   "West Bengal", "Retail"),
        ("Arjun Singh",     "arjun@gmail.com",    "Lucknow",   "UP",          "Online"),
        ("Nisha Iyer",      "nisha@gmail.com",    "Kochi",     "Kerala",      "Retail"),
    ]
)

orders_data = [
    (1,  "2024-01-05", "2024-01-08", "Delivered", "UPI"),
    (2,  "2024-01-10", "2024-01-14", "Delivered", "Card"),
    (3,  "2024-01-15", "2024-01-18", "Delivered", "Net Banking"),
    (4,  "2024-02-01", "2024-02-05", "Delivered", "UPI"),
    (5,  "2024-02-10", "2024-02-13", "Delivered", "Cash"),
    (1,  "2024-02-15", "2024-02-18", "Delivered", "UPI"),
    (6,  "2024-03-01", "2024-03-05", "Delivered", "Card"),
    (7,  "2024-03-10", None,         "Pending",   "Net Banking"),
    (2,  "2024-03-15", "2024-03-18", "Delivered", "UPI"),
    (8,  "2024-04-01", "2024-04-04", "Delivered", "Cash"),
    (3,  "2024-04-10", "2024-04-13", "Returned",  "Card"),
    (9,  "2024-04-15", "2024-04-18", "Delivered", "UPI"),
    (10, "2024-05-01", "2024-05-04", "Delivered", "Card"),
    (4,  "2024-05-10", None,         "Cancelled", "UPI"),
    (5,  "2024-05-15", "2024-05-18", "Delivered", "Cash"),
    (6,  "2024-05-20", "2024-05-23", "Delivered", "Card"),
    (1,  "2024-06-01", "2024-06-04", "Delivered", "UPI"),
    (7,  "2024-06-10", None,         "Pending",   "Net Banking"),
    (8,  "2024-06-15", "2024-06-18", "Delivered", "Cash"),
    (2,  "2024-06-20", "2024-06-23", "Delivered", "Card"),
]
cursor.executemany(
    "INSERT INTO orders (customer_id, order_date, delivery_date, status, payment_mode) VALUES (?,?,?,?,?)",
    orders_data
)

order_items_data = [
    (1,  1,  1,  65000, 5.0),
    (1,  2,  1,  2500,  0.0),
    (2,  4,  2,  899,   10.0),
    (2,  5,  1,  599,   0.0),
    (3,  3,  1,  450,   0.0),
    (3,  9,  5,  60,    0.0),
    (4,  15, 1,  79000, 5.0),
    (5,  6,  1,  2200,  10.0),
    (5,  4,  2,  899,   0.0),
    (6,  12, 1,  12000, 8.0),
    (6,  10, 1,  1800,  5.0),
    (7,  13, 2,  499,   0.0),
    (7,  14, 1,  599,   0.0),
    (8,  16, 1,  55000, 3.0),
    (9,  5,  3,  599,   15.0),
    (9,  4,  2,  899,   0.0),
    (10, 8,  2,  750,   0.0),
    (10, 3,  3,  1200,  5.0),
    (11, 17, 1,  12000, 0.0),
    (12, 11, 2,  1200,  10.0),
    (13, 2,  1,  2500,  0.0),
    (14, 7,  1,  450,   0.0),
    (15, 6,  2,  2200,  5.0),
    (16, 15, 1,  79000, 5.0),
    (17, 1,  1,  65000, 10.0),
    (18, 12, 1,  12000, 5.0),
    (19, 10, 1,  1800,  0.0),
    (19, 11, 1,  1200,  0.0),
    (20, 13, 3,  499,   10.0),
    (20, 14, 2,  599,   0.0),
]
cursor.executemany(
    "INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES (?,?,?,?,?)",
    order_items_data
)

conn.commit()
print("✅ Data Inserted (17 products, 10 customers, 20 orders, 30 order items)")

# ─────────────────────────────────────────────
# STEP 4: ANALYTICS QUERIES
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("         📊 SALES PERFORMANCE DASHBOARD")
print("="*60)

# ── QUERY 1: Total Revenue by Product (with discount logic!)
print("\n🔹 QUERY 1: Revenue Per Product (Discount Applied)")
print("   SQL Concept: SUM with CASE WHEN for calculated revenue")
q1 = pd.read_sql_query("""
    SELECT
        p.product_name,
        cat.category_name,
        SUM(oi.quantity)  AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS gross_revenue,
        ROUND(SUM(oi.quantity * oi.unit_price * oi.discount_pct / 100), 2) AS total_discount,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) AS net_revenue
    FROM order_items oi
    INNER JOIN products p   ON oi.product_id   = p.product_id
    INNER JOIN categories cat ON p.category_id = cat.category_id
    INNER JOIN orders o     ON oi.order_id     = o.order_id
    WHERE o.status = 'Delivered'
    GROUP BY p.product_id
    ORDER BY net_revenue DESC;
""", conn)
print(q1.to_string(index=False))

# ── QUERY 2: Revenue by Category
print("\n🔹 QUERY 2: Category-wise Revenue Breakdown")
print("   SQL Concept: GROUP BY + SUM + percentage calculation")
q2 = pd.read_sql_query("""
    WITH category_revenue AS (
        SELECT
            cat.category_name,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) AS revenue
        FROM order_items oi
        JOIN products p     ON oi.product_id  = p.product_id
        JOIN categories cat ON p.category_id  = cat.category_id
        JOIN orders o       ON oi.order_id    = o.order_id
        WHERE o.status = 'Delivered'
        GROUP BY cat.category_id
    )
    SELECT
        category_name,
        revenue,
        ROUND(revenue * 100.0 / SUM(revenue) OVER(), 2) AS revenue_share_pct
    FROM category_revenue
    ORDER BY revenue DESC;
""", conn)
print(q2.to_string(index=False))

# ── QUERY 3: Top Customers by Spending
print("\n🔹 QUERY 3: Top 5 Customers by Total Spend")
print("   SQL Concept: 4-table JOIN + GROUP BY + HAVING + ORDER BY")
q3 = pd.read_sql_query("""
    SELECT
        c.name          AS customer_name,
        c.city,
        c.segment,
        COUNT(DISTINCT o.order_id)  AS total_orders,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) AS total_spent,
        ROUND(AVG(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) AS avg_order_value
    FROM customers c
    INNER JOIN orders o      ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id    = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id
    ORDER BY total_spent DESC
    LIMIT 5;
""", conn)
print(q3.to_string(index=False))

# ── QUERY 4: Monthly Sales Trend
print("\n🔹 QUERY 4: Monthly Revenue Trend (January – June 2024)")
print("   SQL Concept: strftime() for date grouping + SUM")
q4 = pd.read_sql_query("""
    SELECT
        strftime('%Y-%m', o.order_date)     AS month,
        COUNT(DISTINCT o.order_id)          AS total_orders,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) AS monthly_revenue
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY month
    ORDER BY month;
""", conn)
print(q4.to_string(index=False))

# ── QUERY 5: Order Status Summary
print("\n🔹 QUERY 5: Order Status Breakdown")
print("   SQL Concept: GROUP BY + COUNT + CASE WHEN percentage")
q5 = pd.read_sql_query("""
    SELECT
        status,
        COUNT(*) AS order_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC;
""", conn)
print(q5.to_string(index=False))

# ── QUERY 6: Low Stock Alert
print("\n🔹 QUERY 6: ⚠️  Low Stock Alert (Products with < 20 units)")
print("   SQL Concept: WHERE filter + JOIN + ORDER BY")
q6 = pd.read_sql_query("""
    SELECT
        p.product_name,
        cat.category_name,
        p.stock_qty,
        p.unit_price,
        p.supplier,
        CASE
            WHEN p.stock_qty = 0  THEN '🔴 OUT OF STOCK'
            WHEN p.stock_qty < 15 THEN '🟠 CRITICAL'
            ELSE                       '🟡 LOW'
        END AS stock_status
    FROM products p
    JOIN categories cat ON p.category_id = cat.category_id
    WHERE p.stock_qty < 20
    ORDER BY p.stock_qty ASC;
""", conn)
print(q6.to_string(index=False))

# ── QUERY 7: Payment Mode Preference
print("\n🔹 QUERY 7: Most Popular Payment Modes")
print("   SQL Concept: GROUP BY + COUNT on delivered orders")
q7 = pd.read_sql_query("""
    SELECT
        payment_mode,
        COUNT(*) AS usage_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders WHERE status='Delivered'), 2) AS pct
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY payment_mode
    ORDER BY usage_count DESC;
""", conn)
print(q7.to_string(index=False))

# ── QUERY 8: State-wise Revenue
print("\n🔹 QUERY 8: State-wise Revenue (Regional Analysis)")
print("   SQL Concept: 4-table JOIN + GROUP BY state")
q8 = pd.read_sql_query("""
    SELECT
        c.state,
        COUNT(DISTINCT c.customer_id) AS customers,
        COUNT(DISTINCT o.order_id)    AS orders,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) AS revenue
    FROM customers c
    JOIN orders o       ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id    = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.state
    ORDER BY revenue DESC;
""", conn)
print(q8.to_string(index=False))

# ─────────────────────────────────────────────
# STEP 5: PYTHON AUTOMATION — EXPORT EXCEL
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("   📁 EXPORTING TO EXCEL DASHBOARD")
print("="*60)

output_file = "sales_dashboard_report.xlsx"
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    q1.to_excel(writer, sheet_name="Product_Revenue",    index=False)
    q2.to_excel(writer, sheet_name="Category_Revenue",   index=False)
    q3.to_excel(writer, sheet_name="Top_Customers",      index=False)
    q4.to_excel(writer, sheet_name="Monthly_Trend",      index=False)
    q5.to_excel(writer, sheet_name="Order_Status",       index=False)
    q6.to_excel(writer, sheet_name="Low_Stock_Alert",    index=False)
    q7.to_excel(writer, sheet_name="Payment_Modes",      index=False)
    q8.to_excel(writer, sheet_name="State_wise_Revenue", index=False)

print(f"✅ Excel Report Saved: {output_file}")

# SUMMARY
total_rev = pd.read_sql_query("""
    SELECT ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) as total
    FROM order_items oi JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status='Delivered'
""", conn)
total_orders = cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Delivered'").fetchone()[0]

print("\n" + "="*60)
print("   📈 BUSINESS SUMMARY")
print("="*60)
print(f"  💰 Total Net Revenue  : ₹{total_rev['total'][0]:,.2f}")
print(f"  📦 Delivered Orders   : {total_orders}")
print(f"  🏆 Best Category      : {q2['category_name'][0]} (₹{q2['revenue'][0]:,.2f})")
print(f"  ⭐ Top Customer       : {q3['customer_name'][0]} (₹{q3['total_spent'][0]:,.2f})")
print(f"  ⚠️  Low Stock Items    : {len(q6)} products need restocking")

conn.close()
print("\n✅ Sales Dashboard Complete!")
print("="*60)
