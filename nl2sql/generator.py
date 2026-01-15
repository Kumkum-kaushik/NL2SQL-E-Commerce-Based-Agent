import logging
from nl2sql.fewshot_store import FewShotStore
from nl2sql.llm_client import call_llm
from nl2sql.database import db_manager
from nl2sql.prompts import (
    get_schema_description,
    generate_prompt_strategy1,
    generate_prompt_strategy2,
    extract_sql_from_response
)
from nl2sql.validator import validate_sql
from pathlib import Path
import re

# Configure logging
logger = logging.getLogger(__name__)

# Initialize few-shot store
EXAMPLES_FILE = Path(__file__).parent.parent / "tests" / "test_queries.json"
store = FewShotStore(str(EXAMPLES_FILE))

def extract_relevant_tables(question: str) -> list:
    """
    Extract potentially relevant tables from the question.
    Uses a simple keyword matching against the schema.
    """
    schema_info = db_manager.get_schema_info()
    tables = list(schema_info.keys())
    
    relevant = []
    # Simple regex match for table names in question
    for table in tables:
        # Check if table name or its plural/singular forms are in question
        if table.lower() in question.lower() or table[:-1].lower() in question.lower():
            relevant.append(table)
            
    # Heuristic for common mentions: 'product' -> 'products', 'customer' -> 'customers'
    if not relevant:
        if 'product' in question.lower(): relevant.append('products')
        if 'customer' in question.lower(): relevant.append('customers')
        if 'order' in question.lower(): relevant.append('orders')
        if 'payment' in question.lower(): relevant.append('payments')
        if 'item' in question.lower(): relevant.append('order_items')

    logger.info(f"Identified potential tables: {relevant}")
    return list(set(relevant))

def nl_to_sql(question: str, strategy: int = 1, max_retries: int = 2) -> str:
    """
    Convert natural language question to SQL query with self-correction.
    """
    logger.info(f"Generating SQL for question: '{question}' with strategy {strategy}")
    
    # Step 1: Extract relevant tables using keywords/heuristics
    relevant_tables = extract_relevant_tables(question)
    
    # Step 2: Get Graph-enhanced schema description
    schema = get_schema_description(relevant_tables)
    
    # Retrieve similar examples using RAG
    examples = store.retrieve(question, top_k=5)
    logger.info(f"Retrieved {len(examples)} examples")
    
    # Generate initial query
    for attempt in range(max_retries + 1):
        try:
            # Generate prompt based on strategy
            if strategy == 1:
                prompt = generate_prompt_strategy1(question, schema, examples)
            else:
                prompt = generate_prompt_strategy2(question, schema, examples)
            
            logger.debug(f"Generated prompt for attempt {attempt}. Length: {len(prompt)}")
            
            # Call LLM
            response = call_llm(prompt, temperature=0.1)
            logger.info("Received response from LLM")
            
            # Extract SQL from response
            sql = extract_sql_from_response(response)
            logger.info(f"Extracted SQL: {sql}")
            
            # Validate query
            is_valid, error_msg = validate_sql(sql)
            
            if is_valid:
                logger.info("SQL validation successful")
                return sql
            else:
                logger.warning(f"SQL validation failed: {error_msg}")
                # Self-correction: add error feedback to prompt
                if attempt < max_retries:
                    logger.info("Attempting self-correction")
                    correction_prompt = f"""{prompt}

Previous attempt generated invalid SQL:
{sql}

Error: {error_msg}

Please generate a corrected SQL query that fixes this error:"""
                    
                    response = call_llm(correction_prompt, temperature=0.2)
                    sql = extract_sql_from_response(response)
                    
                    # Validate corrected query
                    is_valid, _ = validate_sql(sql)
                    if is_valid:
                        logger.info("Self-correction successful")
                        return sql
                else:
                    logger.warning("Max retries reached, returning invalid SQL")
                    # Return last attempt even if invalid
                    return sql
                    
        except Exception as e:
            logger.error(f"Error in generator loop (Attempt {attempt}): {str(e)}")
            if attempt == max_retries:
                raise Exception(f"Failed to generate SQL after {max_retries + 1} attempts: {e}")
    
    return ""

def nl_to_sql_with_strategy_comparison(question: str) -> dict:
    """
    Generate SQL using both strategies and return comparison.
    
    Args:
        question: Natural language question
    
    Returns:
        Dictionary with results from both strategies
    """
    result = {
        "question": question,
        "strategy1": {},
        "strategy2": {}
    }
    
    # Try strategy 1
    try:
        sql1 = nl_to_sql(question, strategy=1)
        is_valid1, msg1 = validate_sql(sql1)
        result["strategy1"] = {
            "sql": sql1,
            "valid": is_valid1,
            "message": msg1
        }
    except Exception as e:
        result["strategy1"] = {
            "error": str(e)
        }
    
    # Try strategy 2
    try:
        sql2 = nl_to_sql(question, strategy=2)
        is_valid2, msg2 = validate_sql(sql2)
        result["strategy2"] = {
            "sql": sql2,
            "valid": is_valid2,
            "message": msg2
        }
    except Exception as e:
        result["strategy2"] = {
            "error": str(e)
        }
    
    return result
