"""
Executor Agent - SQL Query Execution
Executes validated SQL queries and formats results
"""
import logging
from phi.agent import Agent
from nl2sql.phidata_setup import gemini_model
from nl2sql.executor import execute_sql, execute_sql_with_limit, format_results_as_table
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def create_executor_agent() -> Agent:
    """
    Create the Executor Agent for SQL execution.
    
    Returns:
        Configured Executor Agent
    """
    logger.info("Creating Executor Agent")
    
    instructions = [
        "You are an expert SQL executor.",
        "Your task is to execute SQL queries safely and return formatted results.",
        "You will receive a validated SQL query to execute.",
        "Always apply row limits to prevent overwhelming results.",
        "Format results in a clear, readable manner.",
    ]
    
    logger.debug(f"Agent instructions: {len(instructions)} rules defined")
    
    agent = Agent(
        name="SQLExecutor",
        role="Execute SQL queries and format results",
        model=gemini_model,
        instructions=instructions,
        markdown=False,
        show_tool_calls=False,
        debug_mode=False,
    )
    
    logger.info("Executor Agent created successfully")
    return agent

def execute_sql_with_agent(sql_query: str, max_rows: int = 100) -> Dict[str, Any]:
    """
    Execute SQL query with row limit and return formatted results.
    
    Args:
        sql_query: Validated SQL query to execute
        max_rows: Maximum number of rows to return
    
    Returns:
        Dictionary with execution results
    """
    logger.info(f"Executing SQL query with max_rows={max_rows}")
    logger.debug(f"SQL: {sql_query}")
    
    try:
        # Execute with limit
        result = execute_sql_with_limit(sql_query, max_rows=max_rows)
        
        if result.get('success'):
            row_count = result.get('row_count', 0)
            logger.info(f"✓ Query executed successfully, returned {row_count} rows")
            
            # Add formatted table view
            if result.get('data'):
                result['formatted_table'] = format_results_as_table(result['data'])
                logger.debug("Results formatted as table")
        else:
            error = result.get('error', 'Unknown error')
            logger.error(f"✗ Query execution failed: {error}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing SQL: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

def execute_and_summarize(sql_query: str, max_rows: int = 100) -> Dict[str, Any]:
    """
    Execute SQL query and provide AI-generated summary of results.
    
    Args:
        sql_query: Validated SQL query to execute
        max_rows: Maximum number of rows to return
    
    Returns:
        Dictionary with execution results and summary
    """
    logger.info("Executing SQL with AI summary")
    
    try:
        # Execute query
        result = execute_sql_with_agent(sql_query, max_rows=max_rows)
        
        if not result.get('success'):
            logger.warning("Query execution failed, skipping summary")
            return result
        
        # Generate summary using agent
        agent = create_executor_agent()
        
        data = result.get('data', [])
        row_count = len(data)
        
        if row_count == 0:
            summary = "No results found."
            logger.info("No results to summarize")
        else:
            # Create summary prompt
            sample_data = data[:5]  # First 5 rows for context
            prompt = f"""The following SQL query was executed:

{sql_query}

Results: {row_count} rows returned

Sample data (first 5 rows):
{sample_data}

Provide a brief, one-sentence summary of what these results show."""
            
            logger.debug(f"Summary prompt prepared (length: {len(prompt)})")
            
            response = agent.run(prompt)
            
            # Extract response content
            if hasattr(response, 'content'):
                summary = response.content
            elif isinstance(response, str):
                summary = response
            else:
                summary = str(response)
            
            logger.info(f"Summary generated: {summary[:100]}...")
        
        result['summary'] = summary
        return result
        
    except Exception as e:
        logger.error(f"Error in execute_and_summarize: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

# Export
__all__ = ['create_executor_agent', 'execute_sql_with_agent', 'execute_and_summarize']
