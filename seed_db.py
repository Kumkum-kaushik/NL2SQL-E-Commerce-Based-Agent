from nl2sql.database import db_manager
from sqlalchemy import text

def seed():
    """Seed the database with schema and initial data."""
    schema = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        country TEXT NOT NULL,
        created_at DATE DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        stock_quantity INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
        order_date DATE DEFAULT CURRENT_DATE,
        status TEXT DEFAULT 'pending'
    );

    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id SERIAL PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(order_id),
        product_id INTEGER NOT NULL REFERENCES products(product_id),
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS payments (
        payment_id SERIAL PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(order_id),
        amount DECIMAL(10,2) NOT NULL,
        payment_method TEXT NOT NULL,
        payment_date DATE DEFAULT CURRENT_DATE
    );
    """
    
    # Simple SQLite compatibility for the SERIAL/DECIMAL part
    if "sqlite" in db_manager.db_url:
        schema = schema.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        schema.replace("DECIMAL(10,2)", "REAL")
    
    with db_manager.engine.connect() as conn:
        print(f"Initializing database at: {db_manager.db_url}")
        for statement in schema.split(";"):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()
    print("V Database initialized.")

if __name__ == "__main__":
    seed()
