FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database and load schema
RUN python -c "
from nl2sql.database import DatabaseManager
from sqlalchemy import text
import os

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Create database
db = DatabaseManager()
with db.get_connection() as conn:
    # Create tables
    conn.execute(text('''CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        country TEXT
    )'''))
    
    conn.execute(text('''CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL
    )'''))
    
    conn.execute(text('''CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(customer_id),
        order_date DATE
    )'''))
    
    conn.execute(text('''CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER REFERENCES orders(order_id),
        product_id INTEGER REFERENCES products(product_id),
        quantity INTEGER
    )'''))
    
    conn.execute(text('''CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY,
        order_id INTEGER REFERENCES orders(order_id),
        amount REAL,
        payment_method TEXT
    )'''))
    
    conn.commit()
print('Database initialized')
"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]