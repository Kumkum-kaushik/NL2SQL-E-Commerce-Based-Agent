# NL2SQL E-Commerce Query Generator (Phidata Version)

## Project Overview

This project implements an end-to-end **Natural Language to SQL (NL2SQL)** system using the **Phidata framework** with **Google Gemini AI** and **Pinecone vector database**. The system converts natural language questions into safe, executable SQL queries using an **agent team architecture**.

### Key Features

* **Agent Team Architecture**: Three specialized agents (Generator, Validator, Executor) coordinated by a Team Leader
* **RAG-Powered Generation**: Few-shot examples stored in Pinecone for semantic retrieval
* **Google Gemini LLM**: Fast and accurate SQL generation using Gemini 1.5 Flash
* **Self-Correction**: Automatic retry with validation feedback
* **Comprehensive Logging**: Debug-friendly logging throughout the system
* **Graph-Based Schema**: NetworkX-powered schema retrieval for optimal context

---

## Tech Stack

* **Framework**: Phidata 2.0+
* **LLM**: Google Gemini 1.5 Flash
* **Embeddings**: Google Gemini Embeddings (text-embedding-004)
* **Vector Database**: Pinecone (serverless, AWS us-east-1)
* **Main Database**: SQLite
* **Backend API**: FastAPI
* **Validation**: SQLGlot

---

## Architecture

```
User Question
     ↓
Team Leader Agent
     ↓
Generator Agent (+ Pinecone RAG)
     ↓
Validator Agent
     ↓
Executor Agent
     ↓
Results
```

### Agent Responsibilities

1. **Generator Agent**: Converts NL to SQL using RAG with Pinecone knowledge base
2. **Validator Agent**: Validates SQL syntax, safety, and schema correctness
3. **Executor Agent**: Executes validated queries and formats results
4. **Team Leader**: Orchestrates workflow with self-correction

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```bash
# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004

# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=nl2sql-examples
PINECONE_DIMENSION=768
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Phidata Configuration
PHI_DEBUG=true
PHI_MONITORING=true

# Database
DATABASE_URL=sqlite:///./ecommerce.db

# API Configuration
API_RATE_LIMIT=20
```

### 3. Initialize Database

```bash
python init_db.py
python load_data.py
```

### 4. Load Few-Shot Examples to Pinecone

The system automatically loads examples from `tests/test_queries.json` to Pinecone on first run.

---

## Usage

### Running the API

```bash
uvicorn api.main:app --reload
```

API will be available at `http://localhost:8000`

### API Endpoints

#### 1. Generate and Execute SQL

```http
POST /api/nl2sql
Content-Type: application/json

{
  "question": "Show me the top 5 products by price",
  "execute": true,
  "strategy": 1,
  "max_rows": 100
}
```

**Response:**

```json
{
  "question": "Show me the top 5 products by price",
  "sql": "SELECT * FROM products ORDER BY price DESC LIMIT 5",
  "valid": true,
  "generation_time_ms": 1234.56,
  "execution_time_ms": 45.67,
  "total_time_ms": 1280.23,
  "execution_result": {
    "success": true,
    "row_count": 5,
    "data": [...]
  },
  "workflow_steps": [...]
}
```

#### 2. Validate SQL

```http
POST /api/validate
Content-Type: application/json

{
  "sql_query": "SELECT * FROM products"
}
```

#### 3. Get Schema

```http
GET /api/schema
```

---

## Testing

### Run Test Suite

```bash
python test_phidata_agents.py
```

### Run API Tests

```bash
python test_api.py
```

---

## Project Structure

```
nl2sql-ecommerce/
├── nl2sql/
│   ├── phidata_setup.py          # Gemini + Pinecone configuration
│   ├── agents/
│   │   ├── generator_agent.py    # SQL generation with RAG
│   │   ├── validator_agent.py    # SQL validation
│   │   ├── executor_agent.py     # SQL execution
│   │   └── team.py               # Team Leader coordination
│   ├── database.py               # SQLite + graph schema
│   ├── validator.py              # Core validation logic
│   ├── executor.py               # Core execution logic
│   └── prompts.py                # Prompt templates
├── api/
│   └── main.py                   # FastAPI application
├── tests/
│   └── test_queries.json         # Few-shot examples
├── test_phidata_agents.py        # Agent team tests
├── requirements.txt
├── .env
└── README.md
```

---

## Logging & Debugging

The system includes comprehensive logging at all levels:

```python
# Enable debug logging
PHI_DEBUG=true  # in .env
```

Logs include:
- Agent workflow steps
- SQL generation process
- Validation results
- Execution timing
- Error traces

---

## Prompt Strategies

### Strategy 1: Schema-First
- Provides full schema context upfront
- Includes 5 most relevant few-shot examples
- Best for straightforward queries

### Strategy 2: Chain-of-Thought
- Step-by-step reasoning
- Identifies tables, columns, joins
- Best for complex queries

---

## Performance

Typical performance metrics:
- **Generation**: 1-3 seconds
- **Validation**: <100ms
- **Execution**: <500ms
- **Total**: 2-4 seconds (including Gemini API latency)

---

## Known Limitations

* Pinecone free tier has rate limits (100 requests/minute)
* Gemini free tier: 15 requests/minute, 1500 requests/day
* Complex nested queries may require multiple retries
* Graph schema retrieval works best with <50 tables

---

## Migration from Cerebras

This version replaces:
- ✅ Cerebras Llama → Google Gemini
- ✅ FAISS → Pinecone
- ✅ Direct LLM calls → Phidata Agent Team
- ✅ Manual orchestration → Team Leader coordination

All core features preserved:
- ✅ Graph-based schema retrieval
- ✅ Self-correction mechanism
- ✅ Rate limiting
- ✅ Caching (via Gemini API)
- ✅ Two prompt strategies

---

## License

MIT

---

## Contact

For questions or issues, please open a GitHub issue.
