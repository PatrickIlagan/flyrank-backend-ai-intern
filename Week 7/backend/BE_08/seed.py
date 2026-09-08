import sqlite3
import random
import datetime

DB_PATH = "report.db"

CUSTOMERS = [
    "Alice Smith", "Bob Johnson", "Carol Williams", "David Brown",
    "Emma Davis", "Frank Miller", "Grace Wilson", "Henry Moore",
    "Isabella Taylor", "Jack Anderson", "Katherine Thomas", "Liam Jackson"
]

PRODUCTS = [
    "Wireless Headphones",
    "Mechanical Keyboard",
    "USB-C Docking Hub",
    "Ergonomic Mouse",
    "4K Ultra-HD Monitor",
    "Aluminum Laptop Stand"
]

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create orders table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 2. Delete existing rows so the seed is safe to run multiple times (idempotent)
    cursor.execute("DELETE FROM orders")

    # 3. Generate 200 realistic orders over the past 30 days
    now = datetime.datetime.now()
    orders = []
    
    # Ensure reproducible yet random distribution
    random.seed(42)

    for _ in range(200):
        customer = random.choice(CUSTOMERS)
        product = random.choice(PRODUCTS)
        amount = round(random.uniform(15.0, 199.99), 2)
        
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        order_date = now - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        created_at = order_date.strftime("%Y-%m-%d %H:%M:%S")

        orders.append((customer, product, amount, created_at))

    cursor.executemany("""
        INSERT INTO orders (customer, product, amount, created_at)
        VALUES (?, ?, ?, ?)
    """, orders)

    conn.commit()

    # 4. Checkpoint count query
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]

    conn.close()
    print(f"Seeding complete. Total orders in report.db: {count}")
    return count

if __name__ == "__main__":
    seed_database()
