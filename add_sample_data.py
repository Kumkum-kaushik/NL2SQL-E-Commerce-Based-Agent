from nl2sql.database import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()

with db.get_connection() as conn:
    # Add sample data
    conn.execute(text("INSERT INTO customers (customer_id, name, email, country) VALUES (1, 'John Doe', 'john@email.com', 'USA')"))
    conn.execute(text("INSERT INTO customers (customer_id, name, email, country) VALUES (2, 'Jane Smith', 'jane@email.com', 'Canada')"))
    
    conn.execute(text("INSERT INTO products (product_id, name, category, price) VALUES (1, 'Laptop', 'Electronics', 999.99)"))
    conn.execute(text("INSERT INTO products (product_id, name, category, price) VALUES (2, 'Mouse', 'Electronics', 29.99)"))
    
    conn.execute(text("INSERT INTO orders (order_id, customer_id, order_date) VALUES (1, 1, '2024-01-15')"))
    conn.execute(text("INSERT INTO orders (order_id, customer_id, order_date) VALUES (2, 2, '2024-01-16')"))
    
    conn.execute(text("INSERT INTO order_items (order_item_id, order_id, product_id, quantity) VALUES (1, 1, 1, 1)"))
    conn.execute(text("INSERT INTO order_items (order_item_id, order_id, product_id, quantity) VALUES (2, 1, 2, 2)"))
    conn.execute(text("INSERT INTO order_items (order_item_id, order_id, product_id, quantity) VALUES (3, 2, 1, 1)"))
    
    conn.execute(text("INSERT INTO payments (payment_id, order_id, amount, payment_method) VALUES (1, 1, 1059.97, 'Credit Card')"))
    conn.execute(text("INSERT INTO payments (payment_id, order_id, amount, payment_method) VALUES (2, 2, 999.99, 'PayPal')"))
    
    conn.commit()
    print("Sample data loaded successfully")

# Verify data
result = conn.execute(text("SELECT COUNT(*) FROM order_items"))
count = result.fetchone()[0]
print(f"Order items count: {count}")