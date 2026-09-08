import os
import sqlite3
import json
import datetime
from typing import Dict, Any
from playwright.sync_api import sync_playwright

DB_PATH = "report.db"

def get_report_data(db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Executes aggregation queries against SQLite to produce summary metrics for the PDF report.
    Returns:
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

def generate_html(data: Dict[str, Any]) -> str:
    """
    Constructs a clean, executive HTML document from report metrics.
    Includes print CSS rules to prevent row clipping and repeat table headers on page breaks.
    """
    today_str = datetime.date.today().strftime("%B %d, %Y")
    totals = data["totals"]
    top_products = data["top_products"]
    daily_trends = data["daily_trends"]
    all_orders = data["all_orders"]

    # Build Top Products Table Rows
    top_products_rows = ""
    for rank, p in enumerate(top_products, start=1):
        revenue_formatted = f"${p['revenue']:,.2f}"
        top_products_rows += f"""
        <tr>
            <td style="font-weight: 600; color: #4a5568;">#{rank}</td>
            <td style="font-weight: 600;">{p['product']}</td>
            <td style="text-align: right;">{p['orders_count']}</td>
            <td style="text-align: right; font-weight: 600; color: #2b6cb0;">{revenue_formatted}</td>
        </tr>
        """

    # Build Daily Trends Table Rows
    daily_rows = ""
    for d in daily_trends:
        daily_revenue_formatted = f"${d['daily_revenue']:,.2f}"
        daily_rows += f"""
        <tr>
            <td>{d['day']}</td>
            <td style="text-align: right;">{d['orders_count']}</td>
            <td style="text-align: right; font-weight: 600;">{daily_revenue_formatted}</td>
        </tr>
        """

    # Build All Orders Appendix Table Rows
    all_orders_rows = ""
    for o in all_orders:
        amount_formatted = f"${o['amount']:,.2f}"
        all_orders_rows += f"""
        <tr>
            <td style="color: #718096; font-family: monospace;">#{o['id']}</td>
            <td>{o['customer']}</td>
            <td>{o['product']}</td>
            <td style="text-align: right; font-weight: 500;">{amount_formatted}</td>
            <td style="color: #718096; font-size: 0.85rem;">{o['created_at']}</td>
        </tr>
        """

    total_revenue_formatted = f"${totals['total_revenue']:,.2f}"
    avg_order_value_formatted = f"${totals['avg_order_value']:,.2f}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Executive Sales Report</title>
    <style>
        /* Base Screen & Print Typography */
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #2d3748;
            background-color: #ffffff;
            padding: 24px;
            font-size: 13px;
            line-height: 1.5;
        }}

        /* Print-specific layout controls */
        @media print {{
            @page {{
                size: A4;
                margin: 15mm 15mm 15mm 15mm;
            }}
            body {{
                padding: 0;
            }}
        }}

        /* Clean page-break rules: avoids slicing table rows in half */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
            page-break-inside: auto;
        }}
        thead {{
            display: table-header-group; /* Repeats table header across every page break */
        }}
        tr {{
            break-inside: avoid;
            page-break-inside: avoid;   /* Prevents row clipping across page boundaries */
        }}
        th {{
            background-color: #f7fafc;
            color: #4a5568;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 8px 12px;
            border-bottom: 2px solid #cbd5e0;
            text-align: left;
        }}
        td {{
            padding: 8px 12px;
            border-bottom: 1px solid #e2e8f0;
        }}

        /* Header Header */
        .report-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .report-title {{
            font-size: 24px;
            font-weight: 700;
            color: #1a202c;
        }}
        .report-subtitle {{
            color: #718096;
            font-size: 12px;
            margin-top: 4px;
        }}
        .report-badge {{
            background-color: #ebf8ff;
            color: #2b6cb0;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 12px;
            border: 1px solid #bee3f8;
        }}

        /* Metric Cards */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 28px;
            break-inside: avoid;
        }}
        .metric-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
        }}
        .metric-label {{
            font-size: 11px;
            text-transform: uppercase;
            color: #718096;
            font-weight: 600;
            letter-spacing: 0.05em;
        }}
        .metric-value {{
            font-size: 22px;
            font-weight: 700;
            color: #2b6cb0;
            margin-top: 4px;
        }}

        /* Section Headings */
        .section-title {{
            font-size: 15px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 12px;
            border-left: 4px solid #3182ce;
            padding-left: 8px;
        }}

        .two-column {{
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
            break-inside: avoid;
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <div>
            <h1 class="report-title">Executive Sales & Revenue Report</h1>
            <div class="report-subtitle">Generated automatically by FlyRank PDF Pipeline on {today_str}</div>
        </div>
        <div class="report-badge">Official Store Audit</div>
    </div>

    <!-- 3 Key Metric Cards -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Total Volume</div>
            <div class="metric-value">{totals['total_orders']:,} Orders</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Gross Revenue</div>
            <div class="metric-value">{total_revenue_formatted}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Average Order Value</div>
            <div class="metric-value">{avg_order_value_formatted}</div>
        </div>
    </div>

    <!-- Two-column tables: Top 5 Products & Daily Trends -->
    <div class="two-column">
        <div>
            <h2 class="section-title">Top 5 Products by Revenue</h2>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Rank</th>
                        <th>Product</th>
                        <th style="text-align: right; width: 20%;">Orders</th>
                        <th style="text-align: right; width: 25%;">Revenue</th>
                    </tr>
                </thead>
                <tbody>
                    {top_products_rows}
                </tbody>
            </table>
        </div>

        <div>
            <h2 class="section-title">Recent 7-Day Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th style="text-align: right;">Orders</th>
                        <th style="text-align: right;">Revenue</th>
                    </tr>
                </thead>
                <tbody>
                    {daily_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Full Orders Appendix (Long Table: 200 Rows across Multiple Pages) -->
    <div>
        <h2 class="section-title">Comprehensive Orders Appendix ({len(all_orders)} Records)</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 12%;">Order ID</th>
                    <th style="width: 25%;">Customer</th>
                    <th style="width: 33%;">Product Name</th>
                    <th style="width: 15%; text-align: right;">Amount</th>
                    <th style="width: 15%;">Date Placed</th>
                </tr>
            </thead>
            <tbody>
                {all_orders_rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    return html

def render_pdf(html: str, output_path: str = "reports/test.pdf") -> str:
    """
    Launches headless Chromium via Playwright and renders HTML into a print-ready A4 PDF.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={
                "top": "15mm",
                "bottom": "15mm",
                "left": "15mm",
                "right": "15mm"
            }
        )
        browser.close()

    return output_path

if __name__ == "__main__":
    print("1. Querying SQL data from report.db...")
    data = get_report_data()
    print(f"   Loaded totals: {data['totals']['total_orders']} orders, ${data['totals']['total_revenue']:,.2f} revenue.")

    print("2. Generating HTML template...")
    html_content = generate_html(data)

    print("3. Rendering PDF via Playwright Chromium...")
    pdf_path = render_pdf(html_content, "reports/test.pdf")
    file_size_kb = os.path.getsize(pdf_path) / 1024
    print(f"   PDF successfully created: {pdf_path} ({file_size_kb:.1f} KB)")
