import sqlite3
import json
from typing import Dict, Any

DB_PATH = "report.db"

def get_report_data(db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Executes aggregation queries against SQLite to produce summary metrics for the PDF report.
    Returns four key sections:
    1. Totals (total orders, total revenue, average order value)
    2. Top 5 products by revenue
    3. Daily breakdown for the last 7 days
    4. Full orders list (for the detailed appendix table)
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Totals: COUNT, SUM, AVG
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_orders,
            ROUND(SUM(amount), 2) AS total_revenue,
            ROUND(AVG(amount), 2) AS avg_order_value
        FROM orders
    """)
    totals_row = cursor.fetchone()
    totals = {
        "total_orders": totals_row["total_orders"],
        "total_revenue": totals_row["total_revenue"],
        "avg_order_value": totals_row["avg_order_value"]
    }

    # 2. Top 5 products by revenue (GROUP BY product)
    cursor.execute("""
        SELECT 
            product,
            ROUND(SUM(amount), 2) AS revenue,
            COUNT(*) AS orders_count
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
    """)
    top_products = [
        {
            "product": row["product"],
            "revenue": row["revenue"],
            "orders_count": row["orders_count"]
        }
        for row in cursor.fetchall()
    ]

    # 3. Orders per day for the last 7 days (GROUP BY day)
    cursor.execute("""
        SELECT 
            date(created_at) AS day,
            COUNT(*) AS orders_count,
            ROUND(SUM(amount), 2) AS daily_revenue
        FROM orders
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    """)
    daily_trends = [
        {
            "day": row["day"],
            "orders_count": row["orders_count"],
            "daily_revenue": row["daily_revenue"]
        }
        for row in cursor.fetchall()
    ]

    # 4. All orders (for the full report table in Stage 3)
    cursor.execute("""
        SELECT id, customer, product, amount, created_at
        FROM orders
        ORDER BY created_at DESC
    """)
    all_orders = [
        {
            "id": row["id"],
            "customer": row["customer"],
            "product": row["product"],
            "amount": row["amount"],
            "created_at": row["created_at"]
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "totals": totals,
        "top_products": top_products,
        "daily_trends": daily_trends,
        "all_orders": all_orders
    }

if __name__ == "__main__":
    data = get_report_data()
    # Print clean JSON with the 4 sections
    summary_preview = {
        "totals": data["totals"],
        "top_products": data["top_products"],
        "daily_trends": data["daily_trends"],
        "all_orders_count": len(data["all_orders"])
    }
    print(json.dumps(summary_preview, indent=2))
