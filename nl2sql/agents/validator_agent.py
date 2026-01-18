"""
Validator Agent - SQL Query Validation
Validates SQL syntax, safety, and schema correctness
"""
import logging
from phi.agent import Agent
from nl2sql.phidata_setup import gemini_model
from nl2sql.validator import validate_sql as validate_sql_core
from typing import Tuple

# Configure logging
logger = logging.getLogger(__name__)

def create_validator_agent() -> Agent:
    """
    Create the Validator Agent for SQL validation.
    
    Returns:
        Configured Validator Agent
    """
    logger.info("Creating Validator Agent")
    
    instructions = [
        "You are an expert SQL validator.",
        "Your task is to validate SQL queries for syntax, safety, and schema correctness.",
        "You will receive a SQL query and validation results.",
        "If the query is invalid, provide clear feedback on what needs to be fixed.",
        "Focus on:",
        "1. SQL syntax errors",
        "2. Invalid table or column names",
        "3. Unsafe operations (DROP, DELETE, UPDATE, etc.)",
        "4. Missing JOIN conditions",
        "5. Incorrect aggregations",
    ]
    
    logger.debug(f"Agent instructions: {len(instructions)} rules defined")
    
    agent = Agent(
        name="SQLValidator",
        role="Validate SQL queries for correctness and safety",
        model=gemini_model,
        instructions=instructions,
        markdown=False,
        show_tool_calls=False,
        debug_mode=False,
    )
    
    logger.info("Validator Agent created successfully")
    return agent

def validate_sql_with_agent(sql_query: str) -> Tuple[bool, str]:
    """
    Validate SQL query using core validation logic.
    
    Args:
        sql_query: SQL query to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    logger.info(f"Validating SQL query: {sql_query[:100]}...")
    
    try:
        # Use existing validation logic
        is_valid, message = validate_sql_core(sql_query)
        
        if is_valid:
            logger.info("✓ SQL validation passed")
        else:
            logger.warning(f"✗ SQL validation failed: {message}")
        
        return is_valid, message
        
    except Exception as e:
        logger.error(f"Error during SQL validation: {str(e)}", exc_info=True)
        return False, f"Validation error: {str(e)}"

def get_validation_feedback(sql_query: str, error_message: str) -> str:
    """
    Get AI-powered feedback on validation errors.
    
    Args:
        sql_query: The invalid SQL query
        error_message: The validation error message
    
    Returns:
        Detailed feedback on how to fix the query
    """
    logger.info("Getting AI-powered validation feedback")
    
    try:
        agent = create_validator_agent()
        
        prompt = f"""The following SQL query failed validation:

SQL Query:
{sql_query}

Validation Error:
{error_message}

Please provide specific guidance on how to fix this query. Be concise and actionable."""
        
        logger.debug(f"Feedback prompt prepared (length: {len(prompt)})")
        
        response = agent.run(prompt)
        
        # Extract response content
        if hasattr(response, 'content'):
            feedback = response.content
        elif isinstance(response, str):
            feedback = response
        else:
            feedback = str(response)
        
        logger.info(f"Validation feedback received (length: {len(feedback)})")
        return feedback
        
    except Exception as e:
        logger.error(f"Error getting validation feedback: {str(e)}", exc_info=True)
        return f"Could not generate feedback: {str(e)}"

# Export
__all__ = ['create_validator_agent', 'validate_sql_with_agent', 'get_validation_feedback']
