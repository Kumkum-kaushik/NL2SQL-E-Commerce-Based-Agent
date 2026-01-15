# SQL Validation Examples

**Generated:** 2026-01-15 12:01:02

This document demonstrates the various validation checks performed by the NL2SQL system.

---

## 1. Unsafe Operations (Blocked)

The system blocks all destructive SQL operations to ensure data safety.

### Unsafe Query - DROP TABLE

**SQL:**
```sql
DROP TABLE customers;
```

**Result:** ✗ Invalid

**Message:** Unsafe operation detected: DROP is not allowed

---

### Unsafe Query - DELETE

**SQL:**
```sql
DELETE FROM orders WHERE order_id = 1;
```

**Result:** ✗ Invalid

**Message:** Unsafe operation detected: DELETE is not allowed

---

### Unsafe Query - UPDATE

**SQL:**
```sql
UPDATE products SET price = 0 WHERE product_id = 1;
```

**Result:** ✗ Invalid

**Message:** Unsafe operation detected: UPDATE is not allowed

---

## 2. Schema Validation

The system validates that all referenced tables and columns exist in the database schema.

### Invalid Table Name

**SQL:**
```sql
SELECT * FROM non_existent_table;
```

**Result:** ✗ Invalid

**Message:** Table 'non_existent_table' does not exist in schema

---

### Invalid Column Name

**SQL:**
```sql
SELECT invalid_column FROM customers;
```

**Result:** ✓ Valid

**Message:** Query is valid

---

## 3. Syntax Validation

The system checks for SQL syntax errors before execution.

### Syntax Error - Missing FROM

**SQL:**
```sql
SELECT * WHERE customer_id = 1;
```

**Result:** ✓ Valid

**Message:** Query is valid

---

### Syntax Error - Unclosed Quote

**SQL:**
```sql
SELECT * FROM customers WHERE name = 'John;
```

**Result:** ✗ Invalid

**Message:** Syntax error: Error tokenizing 'SELECT * FROM customers WHERE name = 'John'

---

## 4. Valid Queries (Accepted)

Examples of queries that pass all validation checks.

### Valid Query - Simple SELECT

**SQL:**
```sql
SELECT * FROM customers;
```

**Result:** ✓ Valid

**Message:** Query is valid

---

### Valid Query - JOIN

**SQL:**
```sql
SELECT c.name, o.order_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id;
```

**Result:** ✓ Valid

**Message:** Query is valid

---

### Valid Query - Aggregation

**SQL:**
```sql
SELECT category, COUNT(*) as count FROM products GROUP BY category;
```

**Result:** ✓ Valid

**Message:** Query is valid

---

## Summary

- **Total Examples:** 10
- **Valid Queries:** 5
- **Invalid Queries:** 5

### Validation Categories

- Unsafe Operations: 3
- Schema Validation: 2
- Syntax Errors: 2
- Valid Queries: 3
