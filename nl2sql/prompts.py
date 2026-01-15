from nl2sql.database import get_schema_info

def get_schema_description() -> str:
    """
    Get formatted schema description for prompt injection.
    
    Returns:
        Formatted schema string with tables and columns
    """
    schema_info = get_schema_info()
    
    schema_lines = []
    for table_name, columns in schema_info.items():
        col_defs = []
        for col in columns:
            col_str = f"{col['name']} {col['type']}"
            if col['pk']:
                col_str += " PRIMARY KEY"
            col_defs.append(col_str)
        
        schema_lines.append(f"{table_name}({', '.join(col_defs)})")
    
    return "\n".join(schema_lines)


# Strategy 1: Schema-first with few-shot examples
STRATEGY_1_SYSTEM = """You are an expert SQL query generator for SQLite databases.

Your task is to convert natural language questions into valid SQL queries.

Database Schema:
{schema}

Few-Shot Examples:
{examples}

Rules:
1. Generate ONLY SELECT queries
2. DO NOT use DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER, or CREATE
3. Use correct table and column names from the schema
4. Return ONLY the SQL query, no explanations
5. Use proper SQL syntax for SQLite
6. Add LIMIT clauses when appropriate to avoid large result sets

Question: {question}

SQL Query:"""


# Strategy 2: Chain-of-thought reasoning
STRATEGY_2_SYSTEM = """You are an expert SQL query generator for SQLite databases.

Your task is to convert natural language questions into valid SQL queries using step-by-step reasoning.

Database Schema:
{schema}

Few-Shot Examples:
{examples}

Process:
1. Identify which tables are needed
2. Identify which columns are required
3. Determine any JOIN conditions
4. Identify any WHERE, GROUP BY, or ORDER BY clauses
5. Construct the final SQL query

Rules:
- Generate ONLY SELECT queries
- DO NOT use DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER, or CREATE
- Use correct table and column names from the schema
- Return ONLY the SQL query at the end, no explanations

Question: {question}

Let's think step by step and then provide the SQL query:"""


def format_examples(examples: list) -> str:
    """Format few-shot examples for prompt."""
    if not examples:
        return "No examples available."
    
    formatted = []
    for i, ex in enumerate(examples, 1):
        formatted.append(f"Example {i}:")
        formatted.append(f"Q: {ex['question']}")
        formatted.append(f"SQL: {ex['sql']}")
        formatted.append("")
    
    return "\n".join(formatted)


def generate_prompt_strategy1(question: str, schema: str, examples: list) -> str:
    """Generate prompt using Strategy 1 (schema-first with examples)."""
    examples_text = format_examples(examples)
    return STRATEGY_1_SYSTEM.format(
        schema=schema,
        examples=examples_text,
        question=question
    )


def generate_prompt_strategy2(question: str, schema: str, examples: list) -> str:
    """Generate prompt using Strategy 2 (chain-of-thought)."""
    examples_text = format_examples(examples)
    return STRATEGY_2_SYSTEM.format(
        schema=schema,
        examples=examples_text,
        question=question
    )


def extract_sql_from_response(response: str) -> str:
    """
    Extract SQL query from LLM response.
    Handles cases where the LLM includes explanations.
    """
    # Remove markdown code blocks if present
    if "```sql" in response:
        start = response.find("```sql") + 6
        end = response.find("```", start)
        response = response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        response = response[start:end].strip()
    
    # Take the last SELECT statement if multiple lines
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    
    # Find lines that look like SQL
    sql_lines = []
    for line in lines:
        if line.upper().startswith('SELECT') or (sql_lines and not line.endswith(':')):
            sql_lines.append(line)
    
    if sql_lines:
        return ' '.join(sql_lines)
    
    return response.strip()
