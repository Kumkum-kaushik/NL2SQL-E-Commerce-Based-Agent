import sqlite3
from typing import List, Dict, Any
from nl2sql.database import get_connection

def execute_sql(sql_query: str, timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Execute SQL query safely and return results.
    
    Args:
        sql_query: The SQL query to execute
        timeout: Query timeout in seconds
    
    Returns:
        List of dictionaries representing query results
    
    Raises:
        Exception: If query execution fails
    """
    conn = None
    try:
        # Get database connection
        conn = get_connection()
        conn.row_factory = sqlite3.Row  # Enable column name access
        
        # Set timeout
        conn.execute(f"PRAGMA busy_timeout = {timeout * 1000}")
        
        # Execute query
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        results = []
        for row in rows:
            results.append(dict(row))
        
        return results
        
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        raise Exception(f"Execution error: {str(e)}")
    finally:
        if conn:
            conn.close()

def execute_sql_with_limit(sql_query: str, max_rows: int = 100) -> Dict[str, Any]:
    """
    Execute SQL query with row limit and return formatted results.
    
    Args:
        sql_query: The SQL query to execute
        max_rows: Maximum number of rows to return
    
    Returns:
        Dictionary with results, count, and metadata
    """
    try:
        # Add LIMIT if not present
        if 'LIMIT' not in sql_query.upper():
            sql_query = f"{sql_query.rstrip(';')} LIMIT {max_rows}"
        
        results = execute_sql(sql_query)
        
        return {
            "success": True,
            "row_count": len(results),
            "data": results,
            "truncated": len(results) >= max_rows
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

def format_results_as_table(results: List[Dict[str, Any]]) -> str:
    """Format query results as a readable table string."""
    if not results:
        return "No results found."
    
    # Get column names
    columns = list(results[0].keys())
    
    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in results:
        for col in columns:
            widths[col] = max(widths[col], len(str(row[col])))
    
    # Create header
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)
    
    # Create rows
    rows = []
    for row in results:
        rows.append(" | ".join(str(row[col]).ljust(widths[col]) for col in columns))
    
    return f"{header}\n{separator}\n" + "\n".join(rows)
