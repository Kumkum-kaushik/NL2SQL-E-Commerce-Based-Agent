import sqlite3
import os
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent.parent / "ecommerce.db"

def init_database():
    """Initialize SQLite database with schema and seed data."""
    
    # Remove existing database if it exists
    if DB_PATH.exists():
        os.remove(DB_PATH)
    
    # Create connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        country TEXT NOT NULL,
        created_at DATE DEFAULT CURRENT_DATE
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER DEFAULT 0
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date DATE DEFAULT CURRENT_DATE,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );

    CREATE TABLE payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_date DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );
    """)
    
    # Insert seed data
    cursor.executescript("""
    -- Insert customers
    INSERT INTO customers (name, email, country) VALUES
    ('John Smith', 'john.smith@email.com', 'USA'),
    ('Emma Johnson', 'emma.j@email.com', 'UK'),
    ('Michael Chen', 'mchen@email.com', 'Canada'),
    ('Sarah Williams', 'sarah.w@email.com', 'USA'),
    ('David Brown', 'dbrown@email.com', 'Australia'),
    ('Lisa Anderson', 'landerson@email.com', 'USA'),
    ('James Wilson', 'jwilson@email.com', 'UK'),
    ('Maria Garcia', 'mgarcia@email.com', 'Spain'),
    ('Robert Taylor', 'rtaylor@email.com', 'USA'),
    ('Jennifer Lee', 'jlee@email.com', 'Canada'),
    ('William Martinez', 'wmartinez@email.com', 'Mexico'),
    ('Linda Davis', 'ldavis@email.com', 'USA'),
    ('Richard Moore', 'rmoore@email.com', 'UK'),
    ('Patricia Jackson', 'pjackson@email.com', 'USA'),
    ('Christopher White', 'cwhite@email.com', 'Australia');

    -- Insert products
    INSERT INTO products (name, category, price, stock_quantity) VALUES
    ('Laptop Pro 15', 'Electronics', 1299.99, 50),
    ('Wireless Mouse', 'Electronics', 29.99, 200),
    ('USB-C Cable', 'Electronics', 12.99, 500),
    ('Desk Chair', 'Furniture', 249.99, 75),
    ('Standing Desk', 'Furniture', 599.99, 30),
    ('Coffee Maker', 'Appliances', 89.99, 100),
    ('Blender', 'Appliances', 59.99, 80),
    ('Running Shoes', 'Sports', 119.99, 150),
    ('Yoga Mat', 'Sports', 34.99, 200),
    ('Water Bottle', 'Sports', 19.99, 300),
    ('Backpack', 'Accessories', 79.99, 120),
    ('Sunglasses', 'Accessories', 149.99, 90),
    ('Watch', 'Accessories', 299.99, 60),
    ('Headphones', 'Electronics', 199.99, 100),
    ('Keyboard', 'Electronics', 89.99, 150),
    ('Monitor 27"', 'Electronics', 399.99, 45),
    ('Office Lamp', 'Furniture', 49.99, 180),
    ('Notebook Set', 'Stationery', 24.99, 250),
    ('Pen Pack', 'Stationery', 9.99, 400),
    ('Desk Organizer', 'Stationery', 34.99, 160);

    -- Insert orders
    INSERT INTO orders (customer_id, order_date, status) VALUES
    (1, '2024-01-15', 'completed'),
    (2, '2024-01-16', 'completed'),
    (3, '2024-01-17', 'completed'),
    (1, '2024-01-18', 'completed'),
    (4, '2024-01-19', 'completed'),
    (5, '2024-01-20', 'completed'),
    (6, '2024-01-21', 'completed'),
    (2, '2024-01-22', 'completed'),
    (7, '2024-01-23', 'completed'),
    (8, '2024-01-24', 'completed'),
    (9, '2024-01-25', 'pending'),
    (10, '2024-01-26', 'pending'),
    (11, '2024-01-27', 'shipped'),
    (12, '2024-01-28', 'shipped'),
    (13, '2024-01-29', 'completed'),
    (14, '2024-01-30', 'completed'),
    (15, '2024-01-31', 'pending'),
    (1, '2024-02-01', 'completed'),
    (3, '2024-02-02', 'shipped'),
    (5, '2024-02-03', 'completed');

    -- Insert order items
    INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 1299.99),
    (1, 2, 2, 29.99),
    (2, 4, 1, 249.99),
    (3, 8, 2, 119.99),
    (3, 9, 1, 34.99),
    (4, 14, 1, 199.99),
    (4, 3, 3, 12.99),
    (5, 5, 1, 599.99),
    (6, 6, 1, 89.99),
    (6, 7, 1, 59.99),
    (7, 11, 1, 79.99),
    (7, 12, 1, 149.99),
    (8, 16, 1, 399.99),
    (9, 15, 1, 89.99),
    (9, 18, 2, 24.99),
    (10, 13, 1, 299.99),
    (11, 1, 1, 1299.99),
    (12, 8, 3, 119.99),
    (13, 10, 5, 19.99),
    (14, 17, 2, 49.99),
    (15, 19, 10, 9.99),
    (16, 20, 3, 34.99),
    (17, 2, 1, 29.99),
    (18, 14, 2, 199.99),
    (19, 4, 1, 249.99),
    (20, 6, 1, 89.99);

    -- Insert payments
    INSERT INTO payments (order_id, amount, payment_method, payment_date) VALUES
    (1, 1359.97, 'credit_card', '2024-01-15'),
    (2, 249.99, 'paypal', '2024-01-16'),
    (3, 274.97, 'credit_card', '2024-01-17'),
    (4, 238.96, 'debit_card', '2024-01-18'),
    (5, 599.99, 'credit_card', '2024-01-20'),
    (6, 149.98, 'paypal', '2024-01-20'),
    (7, 229.98, 'credit_card', '2024-01-21'),
    (8, 399.99, 'debit_card', '2024-01-22'),
    (9, 139.97, 'credit_card', '2024-01-23'),
    (10, 299.99, 'paypal', '2024-01-24'),
    (13, 99.95, 'credit_card', '2024-01-27'),
    (14, 99.98, 'debit_card', '2024-01-28'),
    (15, 99.90, 'paypal', '2024-01-29'),
    (16, 104.97, 'credit_card', '2024-01-30'),
    (18, 399.98, 'credit_card', '2024-02-01'),
    (20, 89.99, 'paypal', '2024-02-03');
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized successfully at {DB_PATH}")
    print(f"   - 15 customers")
    print(f"   - 20 products")
    print(f"   - 20 orders")
    print(f"   - 26 order items")
    print(f"   - 16 payments")

def get_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)

def get_schema_info():
    """Get schema information for all tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    schema_info = {}
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for (table_name,) in tables:
        # Get column info for each table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema_info[table_name] = [
            {"name": col[1], "type": col[2], "nullable": not col[3], "pk": bool(col[5])}
            for col in columns
        ]
    
    conn.close()
    return schema_info

if __name__ == "__main__":
    init_database()
