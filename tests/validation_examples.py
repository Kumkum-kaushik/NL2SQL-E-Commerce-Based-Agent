"""
Generate validation examples showing different types of validation catches.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nl2sql.validator import validate_sql


def test_validation_examples():
    """Test various validation scenarios and document them."""
    
    examples = [
        {
            "name": "Unsafe Query - DROP TABLE",
            "sql": "DROP TABLE customers;",
            "expected": "Should be rejected due to unsafe operation"
        },
        {
            "name": "Unsafe Query - DELETE",
            "sql": "DELETE FROM orders WHERE order_id = 1;",
            "expected": "Should be rejected due to unsafe operation"
        },
        {
            "name": "Unsafe Query - UPDATE",
            "sql": "UPDATE products SET price = 0 WHERE product_id = 1;",
            "expected": "Should be rejected due to unsafe operation"
        },
        {
            "name": "Invalid Table Name",
            "sql": "SELECT * FROM non_existent_table;",
            "expected": "Should be rejected due to invalid table"
        },
        {
            "name": "Invalid Column Name",
            "sql": "SELECT invalid_column FROM customers;",
            "expected": "Should be rejected due to invalid column"
        },
        {
            "name": "Syntax Error - Missing FROM",
            "sql": "SELECT * WHERE customer_id = 1;",
            "expected": "Should be rejected due to syntax error"
        },
        {
            "name": "Syntax Error - Unclosed Quote",
            "sql": "SELECT * FROM customers WHERE name = 'John;",
            "expected": "Should be rejected due to syntax error"
        },
        {
            "name": "Valid Query - Simple SELECT",
            "sql": "SELECT * FROM customers;",
            "expected": "Should be accepted"
        },
        {
            "name": "Valid Query - JOIN",
            "sql": "SELECT c.name, o.order_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id;",
            "expected": "Should be accepted"
        },
        {
            "name": "Valid Query - Aggregation",
            "sql": "SELECT category, COUNT(*) as count FROM products GROUP BY category;",
            "expected": "Should be accepted"
        }
    ]
    
    print("=" * 80)
    print("VALIDATION EXAMPLES TEST")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    for idx, example in enumerate(examples, 1):
        print(f"\n[{idx}/{len(examples)}] {example['name']}")
        print(f"SQL: {example['sql']}")
        print(f"Expected: {example['expected']}")
        
        valid, message = validate_sql(example['sql'])
        
        print(f"Result: {'✓ VALID' if valid else '✗ INVALID'}")
        print(f"Message: {message}")
        
        results.append({
            'name': example['name'],
            'sql': example['sql'],
            'expected': example['expected'],
            'valid': valid,
            'message': message
        })
    
    # Generate markdown report
    output_file = os.path.join(os.path.dirname(__file__), 'validation_examples.md')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# SQL Validation Examples\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This document demonstrates the various validation checks performed by the NL2SQL system.\n\n")
        f.write("---\n\n")
        
        # Group by type
        unsafe_queries = [r for r in results if 'Unsafe' in r['name']]
        invalid_schema = [r for r in results if 'Invalid' in r['name']]
        syntax_errors = [r for r in results if 'Syntax Error' in r['name']]
        valid_queries = [r for r in results if 'Valid Query' in r['name']]
        
        # Unsafe Operations
        f.write("## 1. Unsafe Operations (Blocked)\n\n")
        f.write("The system blocks all destructive SQL operations to ensure data safety.\n\n")
        for result in unsafe_queries:
            f.write(f"### {result['name']}\n\n")
            f.write(f"**SQL:**\n```sql\n{result['sql']}\n```\n\n")
            f.write(f"**Result:** {'✓ Valid' if result['valid'] else '✗ Invalid'}\n\n")
            f.write(f"**Message:** {result['message']}\n\n")
            f.write("---\n\n")
        
        # Invalid Schema
        f.write("## 2. Schema Validation\n\n")
        f.write("The system validates that all referenced tables and columns exist in the database schema.\n\n")
        for result in invalid_schema:
            f.write(f"### {result['name']}\n\n")
            f.write(f"**SQL:**\n```sql\n{result['sql']}\n```\n\n")
            f.write(f"**Result:** {'✓ Valid' if result['valid'] else '✗ Invalid'}\n\n")
            f.write(f"**Message:** {result['message']}\n\n")
            f.write("---\n\n")
        
        # Syntax Errors
        f.write("## 3. Syntax Validation\n\n")
        f.write("The system checks for SQL syntax errors before execution.\n\n")
        for result in syntax_errors:
            f.write(f"### {result['name']}\n\n")
            f.write(f"**SQL:**\n```sql\n{result['sql']}\n```\n\n")
            f.write(f"**Result:** {'✓ Valid' if result['valid'] else '✗ Invalid'}\n\n")
            f.write(f"**Message:** {result['message']}\n\n")
            f.write("---\n\n")
        
        # Valid Queries
        f.write("## 4. Valid Queries (Accepted)\n\n")
        f.write("Examples of queries that pass all validation checks.\n\n")
        for result in valid_queries:
            f.write(f"### {result['name']}\n\n")
            f.write(f"**SQL:**\n```sql\n{result['sql']}\n```\n\n")
            f.write(f"**Result:** {'✓ Valid' if result['valid'] else '✗ Invalid'}\n\n")
            f.write(f"**Message:** {result['message']}\n\n")
            f.write("---\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Total Examples:** {len(results)}\n")
        f.write(f"- **Valid Queries:** {len([r for r in results if r['valid']])}\n")
        f.write(f"- **Invalid Queries:** {len([r for r in results if not r['valid']])}\n\n")
        f.write("### Validation Categories\n\n")
        f.write(f"- Unsafe Operations: {len(unsafe_queries)}\n")
        f.write(f"- Schema Validation: {len(invalid_schema)}\n")
        f.write(f"- Syntax Errors: {len(syntax_errors)}\n")
        f.write(f"- Valid Queries: {len(valid_queries)}\n")
    
    print(f"\n\n✓ Validation examples report generated: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    test_validation_examples()
