# NL2SQL E-Commerce Query Generator

## Project Overview

This project implements an end-to-end **Natural Language to Query (NL2Query)** system that converts natural language questions into **safe, executable SQL and Cypher queries** over an e-commerce dataset.
The system leverages **open-source LLMs**, **Retrieval-Augmented Generation (RAG)**, and an **agentic orchestration framework** to ensure accuracy, safety, and scalability.

The solution supports:

* SQL query generation
* Cypher query generation for Neo4j
* Query validation and execution
* Self-correction on query failure
* API-based interaction and optional Docker deployment

> ⚠️ Note: A single-purpose LLM is considered an incomplete solution.

---

## Tech Stack & Frameworks

* **Agentic Framework**: Phidata / Agno / LangChain
* **LLM**: Freely available open-source model (e.g., CodeLlama)
* **Relational Database**: PostgreSQL
* **Graph Database**: Neo4j
* **Vector Database**: FAISS / Weaviate / Pinecone
* **Backend API**: FastAPI
* **Containerization**: Docker & Docker Compose (optional)
* **Dataset**: Kaggle E-Commerce Dataset for SQL Analysis

Dataset link:
[https://www.kaggle.com/datasets/nabihazahid/ecommerce-dataset-for-sql-analysis](https://www.kaggle.com/datasets/nabihazahid/ecommerce-dataset-for-sql-analysis)

---

## Database Setup

### Relational Database

* Uses the Kaggle E-Commerce dataset
* Schema contains **5–8 tables**
* Stored as SQL schema and seed files

### Graph Database (Neo4j)

* Same dataset represented as a graph
* Nodes represent entities such as customers, orders, products, categories
* Relationships show interactions between entities
* Relationship diagram is provided (hand-drawn or exported from Neo4j)

---

## Vector Database & Prompt Engineering

### Model Selection

* Uses a freely available open-source LLM

### Prompt Engineering (Required)

* Dynamic schema injection (relevant tables and columns only)
* Clear instructions for SQL generation
* 10 few-shot examples (NL → SQL) stored in vector database
* Top-5 relevant examples retrieved and injected dynamically into the prompt

### Deliverables

* Working model integration with code
* Prompt template with schema injection
* Comparison of **two different prompt strategies**

### Questions Answered

* Why this model was chosen
* Impact of schema context size on generation quality

---

## Query Validation & Execution

### Validation Pipeline

1. SQL syntax validation
2. Table and column existence check
3. Safety checks (blocks `DROP`, `DELETE`, `UPDATE`, `TRUNCATE`)
4. Query execution
5. Self-correction by sending error feedback to the LLM

### Deliverables

* Validation module with proper error handling
* 3–5 examples of validation catches:

  * Syntax error
  * Invalid table
  * Invalid column
  * Unsafe query

### Questions Answered

* Percentage of queries valid on first attempt
* SQL injection prevention strategy

---

## Testing & Evaluation

### Test Suite

* 15–20 natural language queries
* Difficulty levels: easy, medium, difficult

### Evaluation Metrics

* Execution success rate (%)
* Average generation time (ms)
* Average execution time (ms)

### Deliverables

* Test results table
* Performance metrics summary

---

## API Endpoints

### Generate and Execute SQL

```http
POST /api/nl2sql
```

**Request**

```json
{
  "question": "Show total sales by category",
  "execute": true
}
```

---

### Get Schema Information

```http
GET /api/schema
```

---

### Validate SQL Query

```http
POST /api/validate
```

**Request**

```json
{
  "sql_query": "SELECT * FROM products"
}
```

---

## Docker Deployment (Optional)

### Services

* PostgreSQL (database)
* Ollama (LLM serving)
* FastAPI application

### Run

```bash
docker-compose up
```

---

## Project Structure

```text
nl2sql-ecommerce/
├── data/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── relationship_diagram.png
├── nl2sql/
│   ├── generator.py
│   ├── validator.py
│   └── executor.py
├── api/
│   ├── main.py
│   └── Dockerfile
├── tests/
│   ├── test_queries.json
│   └── test_results.md
├── notebooks/
│   └── evaluation.py
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Test Results Summary

* Execution success rate
* Common failure types
* Query correction effectiveness
* Performance statistics

(Detailed results available in `tests/test_results.md`)

---

## Known Limitations

* Performance may degrade with very large schemas
* Complex nested queries may require multiple retries
* Schema context size must be carefully controlled
* Graph-to-SQL translation complexity increases with scale

---

## Key Questions Addressed

* Why NL2SQL is harder than general text generation
* Why RAG-style prompting is better than fine-tuning
* First-attempt query success rate
* Most common failure types
* Strategy to scale beyond 50+ tables

---

## Deliverables

* Working FastAPI backend with 3 endpoints
* End-to-end NL2Query pipeline
* Dockerized setup
* API documentation via `/docs`
* Technical report (`REPORT.md`)
* Optional demo (video or screenshots)

---
