# Quick Start Guide - Phidata NL2SQL

## ✅ Dependencies Fixed!

The dependency conflicts have been resolved by removing legacy packages and using compatible versions.

## What Was Removed

**Legacy packages** (from old Cerebras implementation):
- ❌ `langchain` and related packages
- ❌ `streamlit` (optional UI, not needed for core functionality)
- ❌ `flask` and `flask-cors` (not used)

## Current Clean Dependencies

```
✅ phidata >= 2.0.0
✅ google-generativeai >= 0.3.0
✅ pinecone >= 5.0.0
✅ fastapi >= 0.109.0
✅ sqlalchemy >= 2.0.25
✅ sqlglot >= 20.11.0
✅ networkx >= 3.2.0
```

## Next Steps

### 1. Initialize Pinecone Knowledge Base

```bash
python -c "from nl2sql.phidata_setup import get_knowledge_base; kb = get_knowledge_base(); print('Knowledge base loaded!')"
```

This uploads your few-shot examples from `tests/test_queries.json` to Pinecone.

### 2. Start the API Server

```bash
uvicorn api.main:app --reload --port 8000
```

### 3. Test the API

Open another terminal and run:

```bash
curl -X POST "http://localhost:8000/api/nl2sql" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Show me the top 5 products by price\", \"execute\": true}"
```

Or use the test script:

```bash
python test_phidata_agents.py
```

### 4. Access API Documentation

Open your browser: `http://localhost:8000/docs`

## Troubleshooting

### Warning Messages (Safe to Ignore)

You may see warnings about:
- `langchain` packages → **Ignore** (we don't use LangChain anymore)
- `streamlit` packages → **Ignore** (optional, not needed)
- `google.generativeai` deprecation → **Ignore** (phidata handles this)

These are from old packages in your conda environment and don't affect functionality.

### If You See Import Errors

Make sure you're in the virtual environment:

```bash
# Windows
venv\Scripts\activate

# Then reinstall
pip install -r requirements.txt
```

## API Endpoints

### Main Endpoint

```http
POST /api/nl2sql
{
  "question": "your natural language question",
  "execute": true,
  "strategy": 1,
  "max_rows": 100
}
```

### Other Endpoints

- `GET /api/schema` - Get database schema
- `POST /api/validate` - Validate SQL without execution
- `GET /` - Health check

## Logging

Debug logging is enabled by default (`PHI_DEBUG=true` in `.env`).

You'll see detailed logs for:
- ✅ Agent workflow steps
- ✅ SQL generation process
- ✅ Validation results
- ✅ Execution timing

## Example Usage

```python
from nl2sql.agents.team import process_nl2sql_request

result = process_nl2sql_request(
    question="What is the total number of orders?",
    execute=True,
    strategy=1,
    max_rows=100
)

print(f"SQL: {result['sql']}")
print(f"Valid: {result['valid']}")
print(f"Results: {result['execution_result']}")
```

## Success!

Your NL2SQL system is now running on:
- ✅ **Phidata** framework
- ✅ **Google Gemini** LLM
- ✅ **Pinecone** vector database
- ✅ **Three-agent team** architecture

All with comprehensive logging for debugging!
