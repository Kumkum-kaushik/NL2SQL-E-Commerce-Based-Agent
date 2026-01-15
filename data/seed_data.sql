INSERT INTO customers (name, email, country) VALUES
('Amit', 'amit@gmail.com', 'India'),
('Sara', 'sara@gmail.com', 'USA');

INSERT INTO products (name, category, price) VALUES
('Laptop', 'Electronics', 70000),
('Shoes', 'Fashion', 2000);

INSERT INTO orders (customer_id, order_date) VALUES
(1, '2024-01-10'),
(2, '2024-01-12');

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(2, 2, 2);

INSERT INTO payments (order_id, amount, payment_method) VALUES
(1, 70000, 'Card'),
(2, 4000, 'UPI');
