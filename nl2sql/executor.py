from typing import List, Dict, Any
from sqlalchemy import text
from nl2sql.database import db_manager

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
        # Get database connection from sqlalchemy manager
        with db_manager.get_connection() as conn:
            # Execute query using text() for security and compatibility
            result = conn.execute(text(sql_query))
            
            # Fetch results and convert to list of dictionaries
            # result.mappings() provides a dictionary-like interface for rows
            return [dict(row) for row in result.mappings()]
            
    except Exception as e:
        raise Exception(f"Execution error: {str(e)}")

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
