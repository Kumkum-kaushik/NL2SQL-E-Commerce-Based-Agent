from nl2sql.database import db_manager

def get_schema_description(relevant_tables: list = None) -> str:
    """
    Get formatted schema description. Use Graph retrieval if tables provided.
    """
    if relevant_tables:
        return db_manager.get_relevant_schema_subgraph(relevant_tables)
    
    # Fallback to full schema if no tables specified
    schema_info = db_manager.get_schema_info()
    schema_lines = ["Full Database Schema:"]
    for table_name, columns in schema_info.items():
        col_defs = [f"{col['name']} ({col['type']}){ ' [PK]' if col['pk'] else ''}" for col in columns]
        schema_lines.append(f"Table {table_name}: {', '.join(col_defs)}")
    
    return "\n".join(schema_lines)


# Strategy 1: Schema-first with few-shot examples
STRATEGY_1_SYSTEM = """You are an expert SQL query generator.
Your task is to convert natural language questions into valid SQL queries for a PostgreSQL database.

Database Schema Context:
{schema}

Few-Shot Examples:
{examples}

Rules:
1. Generate ONLY SELECT queries.
2. Use correct table and column names from the provided schema.
3. Use proper SQL syntax (PostgreSQL).
4. Return ONLY the SQL query, no explanations or markdown code blocks.
5. Add LIMIT clauses when appropriate.

Question: {question}

SQL Query:"""


# Strategy 2: Chain-of-thought reasoning
STRATEGY_2_SYSTEM = """You are an expert SQL query generator.
Your task is to convert natural language questions into valid SQL queries using step-by-step reasoning.

Database Schema Context:
{schema}

Few-Shot Examples:
{examples}

Process:
1. Identify required tables and relationships based on the Graph schema provided.
2. Identify which columns are required.
3. Determine JOIN conditions.
4. Construct the final PostgreSQL query.

Rules:
- Generate ONLY SELECT queries.
- Return ONLY the final SQL query at the end.
- Syntax: PostgreSQL.

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
