import re
import sqlglot
from typing import Tuple, List
from nl2sql.database import db_manager

# Dangerous SQL keywords that should be blocked
UNSAFE_KEYWORDS = [
    'DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 
    'ALTER', 'CREATE', 'REPLACE', 'GRANT', 'REVOKE'
]

def validate_sql(sql_query: str, allowed_tables: List[str] = None) -> Tuple[bool, str]:
    """
    Validate SQL query for syntax, safety, and schema correctness.
    
    Args:
        sql_query: The SQL query to validate
        allowed_tables: List of allowed table names (if None, fetch from schema)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sql_query or not sql_query.strip():
        return False, "Empty query provided"
    
    sql_query = sql_query.strip()
    
    # 1. Safety check - block dangerous operations
    sql_upper = sql_query.upper()
    for keyword in UNSAFE_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            return False, f"Unsafe operation detected: {keyword} is not allowed"
    
    # 2. Syntax validation using sqlglot
    try:
        parsed = sqlglot.parse_one(sql_query, read='postgres')
        if not parsed:
            return False, "Failed to parse SQL query"
    except Exception as e:
        return False, f"Syntax error: {str(e)}"
    
    # 3. Schema validation - check tables and columns exist
    try:
        schema_info = db_manager.get_schema_info()
        
        if allowed_tables is None:
            allowed_tables = list(schema_info.keys())
        
        # Extract table names from query
        tables_in_query = set()
        for table in parsed.find_all(sqlglot.exp.Table):
            table_name = table.name.lower()
            tables_in_query.add(table_name)
        
        # Check if tables exist
        for table in tables_in_query:
            if table not in allowed_tables:
                return False, f"Table '{table}' does not exist in schema"
        
        # Extract column references and validate
        for column in parsed.find_all(sqlglot.exp.Column):
            column_name = column.name.lower()
            table_name = column.table.lower() if column.table else None
            
            # Skip validation for wildcards and aggregates
            if column_name == '*':
                continue
            
            # If table is specified, check column exists in that table
            if table_name and table_name in schema_info:
                table_columns = [col['name'].lower() for col in schema_info[table_name]]
                if column_name not in table_columns:
                    return False, f"Column '{column_name}' does not exist in table '{table_name}'"
            
    except Exception as e:
        # Schema validation is best-effort, don't fail on errors
        print(f"Warning: Schema validation error: {e}")
    
    # 4. Additional safety checks
    if ';' in sql_query[:-1]:  # Allow semicolon only at the end
        return False, "Multiple statements not allowed"
    
    # All validations passed
    return True, "Query is valid"

def extract_tables_from_query(sql_query: str) -> List[str]:
    """Extract table names from SQL query."""
    try:
        parsed = sqlglot.parse_one(sql_query, read='postgres')
        tables = []
        for table in parsed.find_all(sqlglot.exp.Table):
            tables.append(table.name)
        return tables
    except:
        return []

def sanitize_query(sql_query: str) -> str:
    """Sanitize SQL query by removing comments and extra whitespace."""
    # Remove SQL comments
    sql_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
    
    # Remove extra whitespace
    sql_query = ' '.join(sql_query.split())
    
    return sql_query.strip()
