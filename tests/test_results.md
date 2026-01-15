# NL2SQL System - Test Results and Evaluation

**Generated:** 2026-01-15 22:44:46

---

## Executive Summary

- **Total Test Queries:** 15
- **Strategies Tested:** 2 (Schema-First, Chain-of-Thought)
- **Total Test Runs:** 30

## Performance Metrics by Strategy

### Strategy 1 (Schema-First)

| Metric | Value |
|--------|-------|
| Total Queries | 15 |
| Successful Executions | 15 |
| Accurate Executions | 14 |
| Valid Queries | 15 |
| Success Rate | 100.0% |
| **Accuracy Rate** | **93.33%** |
| Validation Rate | 100.0% |
| Avg Generation Time | 705.98 ms |
| Avg Execution Time | 14.93 ms |
| Min Generation Time | 418.93 ms |
| Max Generation Time | 1131.83 ms |

#### Performance by Difficulty

| Difficulty | Total | Successful | Accurate | Success Rate | Accuracy |
|------------|-------|------------|----------|--------------|----------|
| Easy | 5 | 5 | 5 | 100.0% | 100.0% |
| Medium | 6 | 6 | 6 | 100.0% | 100.0% |
| Difficult | 4 | 4 | 3 | 100.0% | 75.0% |

### Strategy 2 (Chain-of-Thought)

| Metric | Value |
|--------|-------|
| Total Queries | 15 |
| Successful Executions | 15 |
| Accurate Executions | 15 |
| Valid Queries | 15 |
| Success Rate | 100.0% |
| **Accuracy Rate** | **100.0%** |
| Validation Rate | 100.0% |
| Avg Generation Time | 1175.35 ms |
| Avg Execution Time | 11.68 ms |
| Min Generation Time | 540.7 ms |
| Max Generation Time | 3130.79 ms |

#### Performance by Difficulty

| Difficulty | Total | Successful | Accurate | Success Rate | Accuracy |
|------------|-------|------------|----------|--------------|----------|
| Easy | 5 | 5 | 5 | 100.0% | 100.0% |
| Medium | 6 | 6 | 6 | 100.0% | 100.0% |
| Difficult | 4 | 4 | 4 | 100.0% | 100.0% |

## Detailed Test Results

### Strategy 1: Schema-First

#### Test 1: ✓ ACCURATE

**Question:** Show all customers

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT * FROM customers;
```

- Generation Time: 1012.87 ms
- Execution Time: 4.84 ms
- Rows Returned: 100

---

#### Test 2: ✓ ACCURATE

**Question:** List all products in the Electronics category

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT * FROM products WHERE category = 'Electronics';
```

- Generation Time: 1131.83 ms
- Execution Time: 19.73 ms
- Rows Returned: 4

---

#### Test 3: ✓ ACCURATE

**Question:** How many orders have been placed?

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT COUNT(*) as total_orders FROM orders;
```

- Generation Time: 525.46 ms
- Execution Time: 18.72 ms
- Rows Returned: 1

---

#### Test 4: ✓ ACCURATE

**Question:** What is the total revenue from all payments?

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT SUM(amount) as total_revenue FROM payments;
```

- Generation Time: 719.67 ms
- Execution Time: 4.13 ms
- Rows Returned: 1

---

#### Test 5: ✓ ACCURATE

**Question:** Show customers from USA

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT * FROM customers WHERE country = 'USA';
```

- Generation Time: 484.01 ms
- Execution Time: 5.52 ms
- Rows Returned: 100

---

#### Test 6: ✓ ACCURATE

**Question:** List the top 5 most expensive products

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT * FROM products ORDER BY price DESC LIMIT 5;
```

- Generation Time: 454.76 ms
- Execution Time: 1.5 ms
- Rows Returned: 5

---

#### Test 7: ✓ ACCURATE

**Question:** Show total sales by category

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT p.category, SUM(oi.quantity * oi.unit_price) as total_sales FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.category ORDER BY total_sales DESC;
```

- Generation Time: 418.93 ms
- Execution Time: 21.37 ms
- Rows Returned: 6

---

#### Test 8: ✓ ACCURATE

**Question:** Which customers have placed more than one order?

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT c.name, c.email, COUNT(o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name, c.email HAVING COUNT(o.order_id) > 1;
```

- Generation Time: 884.87 ms
- Execution Time: 28.91 ms
- Rows Returned: 100

---

#### Test 9: ✓ ACCURATE

**Question:** What is the average order value?

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT AVG(amount) as avg_order_value FROM payments;
```

- Generation Time: 843.9 ms
- Execution Time: 3.24 ms
- Rows Returned: 1

---

#### Test 10: ✓ ACCURATE

**Question:** Show orders with their customer names and total amounts

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT o.order_id, c.name as customer_name, SUM(oi.quantity * oi.unit_price) as total_amount, o.order_date FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_id, c.name, o.order_date
```

- Generation Time: 447.86 ms
- Execution Time: 23.59 ms
- Rows Returned: 100

---

#### Test 11: ✓ ACCURATE

**Question:** Find the most popular product by quantity sold

**Difficulty:** difficult

**Generated SQL:**
```sql
SELECT p.name, SUM(oi.quantity) as total_quantity FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_id, p.name ORDER BY total_quantity DESC LIMIT 1;
```

- Generation Time: 500.86 ms
- Execution Time: 20.95 ms
- Rows Returned: 1

---

#### Test 12: ✓ PASS (Exec Only)

**Question:** Show monthly revenue for 2024

**Difficulty:** difficult

**Generated SQL:**
```sql
SELECT TO_CHAR(payment_date, 'YYYY-MM') as month, SUM(amount) as revenue FROM payments WHERE EXTRACT(YEAR FROM payment_date) = 2024 GROUP BY month ORDER BY month;
```

- Generation Time: 674.56 ms
- Execution Time: 0.0 ms
- Rows Returned: 0

---

#### Test 13: ✓ ACCURATE

**Question:** Which payment method is most commonly used?

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT payment_method, COUNT(*) as usage_count FROM payments GROUP BY payment_method ORDER BY usage_count DESC LIMIT 1;
```

- Generation Time: 981.98 ms
- Execution Time: 9.82 ms
- Rows Returned: 1

---

#### Test 14: ✓ ACCURATE

**Question:** List customers who have never placed an order

**Difficulty:** difficult

**Generated SQL:**
```sql
SELECT c.* FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL;
```

- Generation Time: 917.58 ms
- Execution Time: 25.14 ms
- Rows Returned: 0

---

#### Test 15: ✓ ACCURATE

**Question:** Show the top 3 customers by total spending

**Difficulty:** difficult

**Generated SQL:**
```sql
SELECT c.name, c.email, SUM(p.amount) as total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN payments p ON o.order_id = p.order_id GROUP BY c.customer_id, c.name, c.email ORDER BY total_spent DESC LIMIT 3;
```

- Generation Time: 590.55 ms
- Execution Time: 36.52 ms
- Rows Returned: 3

---

### Strategy 2: Chain-of-Thought

#### Test 1: ✓ ACCURATE

**Question:** Show all customers

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT * FROM customers;
```

- Generation Time: 661.29 ms
- Execution Time: 2.0 ms
- Rows Returned: 100

---

#### Test 2: ✓ ACCURATE

**Question:** List all products in the Electronics category

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT * FROM products WHERE category = 'Electronics';
```

- Generation Time: 1504.64 ms
- Execution Time: 1.02 ms
- Rows Returned: 4

---

#### Test 3: ✓ ACCURATE

**Question:** How many orders have been placed?

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT COUNT(*) as total_orders FROM orders;
```

- Generation Time: 1046.73 ms
- Execution Time: 1.54 ms
- Rows Returned: 1

---

#### Test 4: ✓ ACCURATE

**Question:** What is the total revenue from all payments?

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT SUM(amount) as total_revenue FROM payments;
```

- Generation Time: 540.7 ms
- Execution Time: 3.21 ms
- Rows Returned: 1

---

#### Test 5: ✓ ACCURATE

**Question:** Show customers from USA

**Difficulty:** easy

**Generated SQL:**
```sql
SELECT * FROM customers WHERE country = 'USA';
```

- Generation Time: 664.36 ms
- Execution Time: 2.54 ms
- Rows Returned: 100

---

#### Test 6: ✓ ACCURATE

**Question:** List the top 5 most expensive products

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT * FROM products ORDER BY price DESC LIMIT 5;
```

- Generation Time: 631.4 ms
- Execution Time: 1.52 ms
- Rows Returned: 5

---

#### Test 7: ✓ ACCURATE

**Question:** Show total sales by category

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT p.category, SUM(oi.quantity * oi.unit_price) as total_sales FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.category ORDER BY total_sales DESC;
```

- Generation Time: 1558.73 ms
- Execution Time: 14.59 ms
- Rows Returned: 6

---

#### Test 8: ✓ ACCURATE

**Question:** Which customers have placed more than one order?

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT c.name, c.email, COUNT(o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name, c.email HAVING COUNT(o.order_id) > 1;
```

- Generation Time: 1348.76 ms
- Execution Time: 17.6 ms
- Rows Returned: 100

---

#### Test 9: ✓ ACCURATE

**Question:** What is the average order value?

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT AVG(amount) as avg_order_value FROM payments;
```

- Generation Time: 1148.08 ms
- Execution Time: 2.01 ms
- Rows Returned: 1

---

#### Test 10: ✓ ACCURATE

**Question:** Show orders with their customer names and total amounts

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT o.order_id, c.name as customer_name, p.amount as total_amount, o.order_date FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN payments p ON o.order_id = p.order_id;
```

- Generation Time: 708.23 ms
- Execution Time: 2.53 ms
- Rows Returned: 100

---

#### Test 11: ✓ ACCURATE

**Question:** Find the most popular product by quantity sold

**Difficulty:** difficult

**Generated SQL:**
```sql
SELECT p.name, SUM(oi.quantity) as total_quantity FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_id, p.name ORDER BY total_quantity DESC LIMIT 1;
```

- Generation Time: 3130.79 ms
- Execution Time: 22.62 ms
- Rows Returned: 1

---

#### Test 12: ✓ ACCURATE

**Question:** Show monthly revenue for 2024

**Difficulty:** difficult

**Generated SQL:**
```sql
SELECT strftime('%Y-%m', payment_date) as month, SUM(amount) as revenue FROM payments WHERE strftime('%Y', payment_date) = '2024' GROUP BY month ORDER BY month;
```

- Generation Time: 603.61 ms
- Execution Time: 23.85 ms
- Rows Returned: 12

---

#### Test 13: ✓ ACCURATE

**Question:** Which payment method is most commonly used?

**Difficulty:** medium

**Generated SQL:**
```sql
SELECT payment_method, COUNT(*) as usage_count FROM payments GROUP BY payment_method ORDER BY usage_count DESC LIMIT 1;
```

- Generation Time: 929.62 ms
- Execution Time: 8.54 ms
- Rows Returned: 1

---

#### Test 14: ✓ ACCURATE

**Question:** List customers who have never placed an order

**Difficulty:** difficult

**Generated SQL:**
```sql
SELECT c.* FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL;
```

- Generation Time: 1779.04 ms
- Execution Time: 29.59 ms
- Rows Returned: 0

---

#### Test 15: ✓ ACCURATE

**Question:** Show the top 3 customers by total spending

**Difficulty:** difficult

**Generated SQL:**
```sql
SELECT c.name, c.email, SUM(p.amount) as total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN payments p ON o.order_id = p.order_id GROUP BY c.customer_id, c.name, c.email ORDER BY total_spent DESC LIMIT 3;
```

- Generation Time: 1374.3 ms
- Execution Time: 42.02 ms
- Rows Returned: 3

---

## Strategy Comparison Examples

### Show all customers

**Difficulty:** easy

#### Strategy 1: Schema-First

#### Strategy 2: Chain-of-Thought

---

### Show total sales by category

**Difficulty:** medium

#### Strategy 1: Schema-First

#### Strategy 2: Chain-of-Thought

---

### Find the most popular product by quantity sold

**Difficulty:** difficult

#### Strategy 1: Schema-First

#### Strategy 2: Chain-of-Thought

---

### List customers who have never placed an order

**Difficulty:** difficult

#### Strategy 1: Schema-First

#### Strategy 2: Chain-of-Thought

---

