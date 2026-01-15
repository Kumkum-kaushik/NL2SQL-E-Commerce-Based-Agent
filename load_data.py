import csv
import re
from datetime import datetime
from nl2sql.database import db_manager
from sqlalchemy import text

DATASET_FILE = "ecommerce_dataset_10000.csv"

def parse_id(id_str):
    """Extract integer ID from string like CUST123, PROD456, ORD789."""
    if not id_str:
        return None
    # Remove non-numeric characters
    num_part = re.sub(r'\D', '', id_str)
    return int(num_part) if num_part else None

def load_data():
    print("=" * 60)
    print("Loading Ecommerce Dataset...")
    print("=" * 60)

    # Data structures to de-duplicate and aggregate
    customers = {}
    products = {}
    orders = {} 
    
    print(f"Reading {DATASET_FILE}...")
    
    try:
        with open(DATASET_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Parse IDs
                cust_id = parse_id(row['customer_id'])
                prod_id = parse_id(row['product_id'])
                order_id = parse_id(row['order_id'])
                
                # 1. Customer
                if cust_id not in customers:
                    customers[cust_id] = {
                        'id': cust_id,
                        'name': f"{row['first_name']} {row['last_name']}",
                        'email': f"{row['first_name'].lower()}.{row['last_name'].lower()}{cust_id}@example.com",
                        'country': row['country']
                    }
                
                # 2. Product
                if prod_id not in products:
                    products[prod_id] = {
                        'id': prod_id,
                        'name': row['product_name'],
                        'category': row['category'],
                        'price': float(row['unit_price'])
                    }
                
                # 3. Order & Order Items
                if order_id not in orders:
                    orders[order_id] = {
                        'id': order_id,
                        'customer_id': cust_id,
                        'date': row['order_date'],
                        'status': row['order_status'],
                        'payment_method': row['payment_method'],
                        'items': []
                    }
                
                # Add Item to Order
                orders[order_id]['items'].append({
                    'product_id': prod_id,
                    'quantity': int(row['quantity']),
                    'unit_price': float(row['unit_price'])
                })
                
    except FileNotFoundError:
        print(f"Error: File {DATASET_FILE} not found!")
        return

    print(f"Found {len(customers)} unique customers")
    print(f"Found {len(products)} unique products")
    print(f"Found {len(orders)} unique orders")
    
    # Database Operations
    with db_manager.engine.connect() as conn:
        print("\nClearing existing data...")
        # Disable FK checks to allow truncate/delete
        if "sqlite" in db_manager.db_url:
            conn.execute(text("PRAGMA foreign_keys = OFF"))
        
        # Clear tables
        conn.execute(text("DELETE FROM payments"))
        conn.execute(text("DELETE FROM order_items"))
        conn.execute(text("DELETE FROM orders"))
        conn.execute(text("DELETE FROM products"))
        conn.execute(text("DELETE FROM customers"))
        
        if "sqlite" in db_manager.db_url:
            conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()
        print("Tables cleared.")

        # --- Bulk Inserts ---
        # Note: Using individual inserts for simplicity/compatibility, could be optimized with batching
        
        print("\nInserting Customers...")
        count = 0
        for c in customers.values():
            conn.execute(
                text("INSERT INTO customers (customer_id, name, email, country) VALUES (:id, :name, :email, :country)"),
                c
            )
            count += 1
            if count % 1000 == 0: print(f"  Inserted {count} customers...")
        
        print(f"Inserted {count} customers total.")
        
        print("\nInserting Products...")
        for p in products.values():
            conn.execute(
                text("INSERT INTO products (product_id, name, category, price) VALUES (:id, :name, :category, :price)"),
                p
            )
        print(f"Inserted {len(products)} products.")
        
        print("\nInserting Orders, Items, and Payments...")
        item_count = 0
        payment_count = 0
        
        for o in orders.values():
            # Insert Order
            conn.execute(
                text("INSERT INTO orders (order_id, customer_id, order_date, status) VALUES (:id, :customer_id, :date, :status)"),
                o
            )
            
            # Calculate total amount for payment
            total_amount = 0
            
            # Insert Items
            for item in o['items']:
                conn.execute(
                    text("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (:oid, :pid, :qty, :price)"),
                    {'oid': o['id'], 'pid': item['product_id'], 'qty': item['quantity'], 'price': item['unit_price']}
                )
                total_amount += (item['quantity'] * item['unit_price'])
                item_count += 1
                
            # Insert Payment
            conn.execute(
                text("INSERT INTO payments (order_id, amount, payment_method, payment_date) VALUES (:oid, :amt, :method, :date)"),
                {'oid': o['id'], 'amt': total_amount, 'method': o['payment_method'], 'date': o['date']}
            )
            payment_count += 1
            
            if payment_count % 1000 == 0: print(f"  Processed {payment_count} orders...")
            
        conn.commit()
        print(f"\nCompleted! Stats:")
        print(f"- Orders: {len(orders)}")
        print(f"- Order Items: {item_count}")
        print(f"- Payments: {payment_count}")

if __name__ == "__main__":
    load_data()
