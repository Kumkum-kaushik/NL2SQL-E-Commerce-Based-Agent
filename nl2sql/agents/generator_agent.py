"""
Generator Agent - SQL Query Generation with RAG
Converts natural language questions to SQL queries using Gemini LLM and Pinecone knowledge base
"""
import logging
from phi.agent import Agent
from nl2sql.phidata_setup import gemini_model, get_knowledge_base
from nl2sql.database import db_manager
from nl2sql.prompts import get_schema_description
import re

# Configure logging
logger = logging.getLogger(__name__)

def extract_relevant_tables(question: str) -> list:
    """
    Extract potentially relevant tables from the question.
    Uses keyword matching against the schema.
    """
    logger.debug(f"Extracting relevant tables from question: {question}")
    schema_info = db_manager.get_schema_info()
    tables = list(schema_info.keys())
    
    relevant = []
    for table in tables:
        if table.lower() in question.lower() or table[:-1].lower() in question.lower():
            relevant.append(table)
            logger.debug(f"Found relevant table: {table}")
    
    # Heuristic for common mentions
    if not relevant:
        logger.debug("No tables found by name matching, using heuristics")
        question_lower = question.lower()
        if 'product' in question_lower: 
            relevant.append('products')
        if 'customer' in question_lower: 
            relevant.append('customers')
        if 'order' in question_lower: 
            relevant.append('orders')
            # For order-related queries, often need order_items for details
            if 'detail' in question_lower or 'item' in question_lower:
                relevant.append('order_items')
        if 'payment' in question_lower: 
            relevant.append('payments')
        if 'item' in question_lower or 'detail' in question_lower: 
            relevant.append('order_items')
    else:
        # Even if we found tables by name, check for additional context
        question_lower = question.lower()
        if 'order' in question_lower and ('detail' in question_lower or 'item' in question_lower):
            if 'order_items' not in relevant:
                relevant.append('order_items')
                logger.debug("Added order_items due to 'order details' context")
    
    relevant = list(set(relevant))
    logger.info(f"Identified {len(relevant)} relevant tables: {relevant}")
    return relevant

def extract_sql_from_response(response: str) -> str:
    """
    Extract SQL query from LLM response.
    Handles cases where the LLM includes explanations or markdown.
    """
    logger.debug(f"Extracting SQL from response (length: {len(response)})")
    
    # Remove markdown code blocks if present
    if "```sql" in response:
        start = response.find("```sql") + 6
        end = response.find("```", start)
        response = response[start:end].strip()
        logger.debug("Extracted SQL from ```sql code block")
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        response = response[start:end].strip()
        logger.debug("Extracted SQL from ``` code block")
    
    # Take the last SELECT statement if multiple lines
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    
    # Find lines that look like SQL
    sql_lines = []
    for line in lines:
        if line.upper().startswith('SELECT') or (sql_lines and not line.endswith(':')):
            sql_lines.append(line)
    
    if sql_lines:
        result = ' '.join(sql_lines)
        logger.info(f"Extracted SQL query: {result[:100]}...")
        return result
    
    logger.warning("Could not extract SQL from structured format, returning full response")
    return response.strip()

def create_generator_agent(strategy: int = 1) -> Agent:
    """
    Create the Generator Agent with RAG capabilities.
    
    Args:
        strategy: Prompt strategy (1 or 2)
            1 = Schema-first with few-shot examples
            2 = Chain-of-thought reasoning
    
    Returns:
        Configured Generator Agent
    """
    logger.info(f"Creating Generator Agent with strategy {strategy}")
    
    # Get knowledge base for RAG (with fallback)
    try:
        knowledge_base = get_knowledge_base()
        logger.debug(f"Knowledge base loaded: {knowledge_base is not None}")
    except Exception as kb_error:
        logger.warning(f"Knowledge base creation failed: {str(kb_error)}")
        logger.info("Proceeding without knowledge base (will use schema-only approach)")
        knowledge_base = None
    
    # Define instructions based on strategy
    if strategy == 1:
        instructions = [
            "You are an expert SQL query generator for PostgreSQL databases.",
            "Your task is to convert natural language questions into valid SQL queries.",
            "Use the provided schema context and few-shot examples to guide your generation.",
            "CRITICAL RULES:",
            "1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)",
            "2. Use correct table and column names from the provided schema",
            "3. Use proper PostgreSQL syntax",
            "4. Return ONLY the SQL query without explanations or markdown",
            "5. Add LIMIT clauses when appropriate to avoid large result sets",
            "6. Use JOINs when querying multiple tables",
            "7. Handle aggregations (COUNT, SUM, AVG) correctly",
        ]
    else:  # strategy == 2
        instructions = [
            "You are an expert SQL query generator using step-by-step reasoning.",
            "Your task is to convert natural language questions into valid SQL queries.",
            "PROCESS:",
            "1. Identify required tables from the schema",
            "2. Identify required columns",
            "3. Determine JOIN conditions if multiple tables",
            "4. Construct the final PostgreSQL query",
            "CRITICAL RULES:",
            "- Generate ONLY SELECT queries",
            "- Return ONLY the final SQL query at the end",
            "- Use proper PostgreSQL syntax",
            "- No explanations in the final output, just the SQL",
        ]
    
    logger.debug(f"Agent instructions: {len(instructions)} rules defined")
    
    # Create agent (with optional knowledge base)
    agent_kwargs = {
        "name": "SQLGenerator",
        "role": "Convert natural language to SQL queries",
        "model": gemini_model,
        "instructions": instructions,
        "markdown": False,
        "show_tool_calls": False,
        "debug_mode": False,
    }
    
    # Only add knowledge base if available
    if knowledge_base is not None:
        agent_kwargs.update({
            "knowledge": knowledge_base,
            "search_knowledge": True,
        })
        logger.info("Generator Agent created with knowledge base")
    else:
        logger.info("Generator Agent created without knowledge base (schema-only mode)")
    
    agent = Agent(**agent_kwargs)

    return agent

def generate_sql(question: str, strategy: int = 1) -> str:
    """
    Generate SQL query from natural language question.
    
    Args:
        question: Natural language question
        strategy: Prompt strategy (1 or 2)
    
    Returns:
        Generated SQL query
    """
    logger.info(f"Generating SQL for question: '{question}' with strategy {strategy}")
    
    try:
        # Extract relevant tables
        relevant_tables = extract_relevant_tables(question)
        
        # Get graph-enhanced schema description
        schema = get_schema_description(relevant_tables)
        logger.debug(f"Schema description length: {len(schema)} characters")
        
        # Create generator agent
        agent = create_generator_agent(strategy=strategy)
        
        # Prepare prompt with schema context
        schema_info = db_manager.get_schema_info()
        available_tables = list(schema_info.keys())
        
        prompt = f"""Database Schema Context:
{schema}

Available Tables: {', '.join(available_tables)}
Key Table Mappings:
- "customers" table for customer information
- "products" table for product information  
- "orders" table for order information
- "order_items" table for order details/items (use this for order details)
- "payments" table for payment information

Question: {question}

Generate a SQL query to answer this question. Return ONLY the SQL query without any explanations or markdown formatting."""
        
        logger.debug(f"Prompt prepared (length: {len(prompt)})")
        
        # Run agent
        logger.info("Running Generator Agent...")
        response = agent.run(prompt)
        
        # Extract response content
        if hasattr(response, 'content'):
            sql_response = response.content
        elif isinstance(response, str):
            sql_response = response
        else:
            sql_response = str(response)
        
        logger.debug(f"Agent response received (length: {len(sql_response)})")
        
        # Extract SQL from response
        sql = extract_sql_from_response(sql_response)
        
        logger.info(f"SQL generation completed: {sql[:100]}...")
        return sql
        
    except Exception as e:
        logger.error(f"Error generating SQL: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate SQL: {str(e)}")

# Export
__all__ = ['create_generator_agent', 'generate_sql', 'extract_relevant_tables', 'extract_sql_from_response']
