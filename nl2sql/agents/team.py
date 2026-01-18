"""
Team Leader Agent - Orchestrates Generator, Validator, and Executor agents
Coordinates the NL2SQL workflow with self-correction capabilities
"""
import logging
import time
from phi.agent import Agent
from nl2sql.phidata_setup import gemini_model
from nl2sql.agents.generator_agent import generate_sql
from nl2sql.agents.validator_agent import validate_sql_with_agent, get_validation_feedback
from nl2sql.agents.executor_agent import execute_sql_with_agent
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def create_team_leader() -> Agent:
    """
    Create the Team Leader Agent that coordinates all sub-agents.
    
    Returns:
        Configured Team Leader Agent
    """
    logger.info("Creating Team Leader Agent")
    
    instructions = [
        "You are the Team Leader for an NL2SQL system.",
        "Your role is to coordinate three specialized agents:",
        "1. Generator Agent - Converts natural language to SQL",
        "2. Validator Agent - Validates SQL for correctness and safety",
        "3. Executor Agent - Executes validated SQL queries",
        "Workflow:",
        "- Receive natural language question from user",
        "- Delegate to Generator to create SQL",
        "- Delegate to Validator to check SQL",
        "- If valid, delegate to Executor to run query",
        "- If invalid, provide feedback and retry generation",
        "- Return final results to user",
    ]
    
    logger.debug(f"Team Leader instructions: {len(instructions)} rules defined")
    
    agent = Agent(
        name="TeamLeader",
        role="Coordinate NL2SQL workflow across specialized agents",
        model=gemini_model,
        instructions=instructions,
        markdown=True,
        show_tool_calls=False,
        debug_mode=False,
    )
    
    logger.info("Team Leader Agent created successfully")
    return agent

def process_nl2sql_request(
    question: str,
    execute: bool = True,
    strategy: int = 1,
    max_rows: int = 100,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Process NL2SQL request using the agent team workflow.
    
    Args:
        question: Natural language question
        execute: Whether to execute the query
        strategy: Prompt strategy (1 or 2)
        max_rows: Maximum rows to return
        max_retries: Maximum retry attempts for self-correction
    
    Returns:
        Dictionary with complete results
    """
    logger.info("="*80)
    logger.info(f"TEAM WORKFLOW STARTED")
    logger.info(f"Question: {question}")
    logger.info(f"Strategy: {strategy}, Execute: {execute}, Max Rows: {max_rows}")
    logger.info("="*80)
    
    start_time = time.time()
    result = {
        "question": question,
        "strategy": strategy,
        "workflow_steps": []
    }
    
    try:
        # STEP 1: Generate SQL
        logger.info("\n[STEP 1/3] GENERATOR AGENT - Generating SQL query...")
        gen_start = time.time()
        
        sql = generate_sql(question, strategy=strategy)
        gen_time = (time.time() - gen_start) * 1000
        
        result["sql"] = sql
        result["generation_time_ms"] = round(gen_time, 2)
        result["workflow_steps"].append({
            "step": "generation",
            "agent": "Generator",
            "status": "completed",
            "time_ms": round(gen_time, 2)
        })
        
        logger.info(f"✓ SQL generated in {gen_time:.2f}ms")
        logger.debug(f"Generated SQL: {sql}")
        
        # STEP 2: Validate SQL (with self-correction)
        logger.info("\n[STEP 2/3] VALIDATOR AGENT - Validating SQL query...")
        val_start = time.time()
        
        is_valid, validation_msg = validate_sql_with_agent(sql)
        val_time = (time.time() - val_start) * 1000
        
        result["valid"] = is_valid
        result["validation_message"] = validation_msg
        result["validation_time_ms"] = round(val_time, 2)
        result["workflow_steps"].append({
            "step": "validation",
            "agent": "Validator",
            "status": "completed" if is_valid else "failed",
            "time_ms": round(val_time, 2),
            "message": validation_msg
        })
        
        # Self-correction loop
        retry_count = 0
        while not is_valid and retry_count < max_retries:
            logger.warning(f"✗ Validation failed: {validation_msg}")
            logger.info(f"\n[SELF-CORRECTION] Attempt {retry_count + 1}/{max_retries}")
            
            # Get AI feedback
            feedback = get_validation_feedback(sql, validation_msg)
            logger.debug(f"Validation feedback: {feedback}")
            
            # Retry generation with feedback
            logger.info("Re-generating SQL with validation feedback...")
            correction_prompt = f"""{question}

Previous SQL attempt failed validation:
{sql}

Error: {validation_msg}

Feedback: {feedback}

Please generate a corrected SQL query."""
            
            sql = generate_sql(correction_prompt, strategy=strategy)
            result["sql"] = sql
            logger.debug(f"Corrected SQL: {sql}")
            
            # Re-validate
            is_valid, validation_msg = validate_sql_with_agent(sql)
            result["valid"] = is_valid
            result["validation_message"] = validation_msg
            
            result["workflow_steps"].append({
                "step": f"self_correction_{retry_count + 1}",
                "agent": "Generator + Validator",
                "status": "completed" if is_valid else "failed",
                "message": validation_msg
            })
            
            retry_count += 1
        
        if is_valid:
            logger.info(f"✓ SQL validation passed")
        else:
            logger.error(f"✗ SQL validation failed after {max_retries} retries")
            result["error"] = f"SQL validation failed: {validation_msg}"
            result["total_time_ms"] = round((time.time() - start_time) * 1000, 2)
            return result
        
        # STEP 3: Execute SQL (if requested)
        if execute:
            logger.info("\n[STEP 3/3] EXECUTOR AGENT - Executing SQL query...")
            exec_start = time.time()
            
            execution_result = execute_sql_with_agent(sql, max_rows=max_rows)
            exec_time = (time.time() - exec_start) * 1000
            
            result["execution_time_ms"] = round(exec_time, 2)
            result["execution_result"] = execution_result
            
            if execution_result.get('success'):
                row_count = execution_result.get('row_count', 0)
                logger.info(f"✓ Query executed successfully, returned {row_count} rows")
                result["workflow_steps"].append({
                    "step": "execution",
                    "agent": "Executor",
                    "status": "completed",
                    "time_ms": round(exec_time, 2),
                    "rows_returned": row_count
                })
            else:
                error = execution_result.get('error', 'Unknown error')
                logger.error(f"✗ Query execution failed: {error}")
                result["workflow_steps"].append({
                    "step": "execution",
                    "agent": "Executor",
                    "status": "failed",
                    "time_ms": round(exec_time, 2),
                    "error": error
                })
        else:
            logger.info("\n[STEP 3/3] EXECUTOR AGENT - Skipped (execute=False)")
            result["workflow_steps"].append({
                "step": "execution",
                "agent": "Executor",
                "status": "skipped"
            })
        
        # Calculate total time
        total_time = (time.time() - start_time) * 1000
        result["total_time_ms"] = round(total_time, 2)
        
        logger.info("="*80)
        logger.info(f"TEAM WORKFLOW COMPLETED in {total_time:.2f}ms")
        logger.info(f"Success: {result.get('valid', False)}")
        logger.info("="*80)
        
        return result
        
    except Exception as e:
        logger.error(f"ERROR in team workflow: {str(e)}", exc_info=True)
        result["error"] = str(e)
        result["total_time_ms"] = round((time.time() - start_time) * 1000, 2)
        result["workflow_steps"].append({
            "step": "error",
            "status": "failed",
            "error": str(e)
        })
        return result

# Export
__all__ = ['create_team_leader', 'process_nl2sql_request']
