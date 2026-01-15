# NL2SQL E-Commerce System - Technical Report

## 1. Project Overview
This project implements an end-to-end **Natural Language to Query (NL2Query)** system that converts natural language questions into **safe, executable SQL queries** over an e-commerce dataset. It uses **Google Gemini** as the LLM, RAG-based few-shot learning, and a robust validation pipeline.

## 2. Model Selection: Google Gemini 1.5 Flash
We chose **Gemini 1.5 Flash** for this implementation because:
- **Speed & Latency**: It offers extremely fast inference times, critical for real-time query generation.
- **Cost Efficiency**: It provides a generous free tier and low cost per token, making it ideal for development and scaling.
- **Reasoning Capability**: Despite being a "light" model, it demonstrates strong SQL generation capabilities, especially when aided by few-shot examples.
- **Context Window**: Large context window allows for including schema definitions and multiple relevant examples without truncation.
- **Stability**: As a stable release (vs experimental), it has better quota limits and more reliable performance.

## 3. RAG vs Fine-tuning
We employed a **Retrieval-Augmented Generation (RAG)** approach instead of fine-tuning:
- **Dynamic Adaptability**: New examples can be added to the vector store without retraining the model.
- **Schema Flexibility**: The system adapts to schema changes instantly by just updating the schema description injected into the prompt.
- **Cost**: Fine-tuning requires significant compute resources and data preparation. RAG leverages existing general-purpose models effectively.
- **Accuracy**: By retrieving the top-5 most similar past queries (using FAISS), the model sees examples semantically close to the user's question, significantly improving accuracy.

## 4. Prompt Engineering Strategies
We implemented and compared two strategies:

### Strategy 1: Schema-First with Examples
- **Structure**: Schema definition → Few-shot examples → Question
- **Focus**: Direct translation based on pattern matching with examples.
- **Performance**: Faster (lower latency), works well for simple to medium complexity queries.

### Strategy 2: Chain-of-Thought (CoT) Reasoning
- **Structure**: Schema → Examples → Step-by-step reasoning instructions → Question
- **Process**: LLM is asked to:
  1. Identify needed tables
  2. Identify columns and joins
  3. Construct filters
  4. Generate final SQL
- **Performance**: Higher accuracy on complex queries (e.g., multi-table joins with aggregations), but slightly higher latency.

## 5. Security & Safety
SQL injection and destructive operations are prevented through a multi-layer validation pipeline:
1. **Keyword Blocking**: Queries containing `DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `ALTER` are correctly rejected.
2. **Schema Validation**: 
   - Tables extracted from the query are checked against the actual database schema.
   - Columns are verified to ensure they exist in the referenced tables.
   - Using `sqlglot` for robust parsing ensures we aren't just matching strings but understanding the SQL structure.
3. **Execution Safety**:
   - Application connects with read-only intent where possible (though SQLite file permissions are file-level).
   - `LIMIT` clauses are automatically injected/enforced to prevent massive data dumps.
   - Query timeouts prevent denial-of-service from long-running queries.

## 6. Scalability Strategy
To scale beyond 50+ tables (known limitation):
- **Dynamic Schema Selection**: Instead of injecting the entire schema, we would use a first-pass LLM call or vector search to identify *only* the relevant tables for the specific question.
- **Vector Store Partitioning**: Few-shot examples can be partitioned by domain (e.g., "sales", "inventory", "customer support") to improve retrieval relevance.
- **Graph Database**: For highly complex relationships (e.g., "friends of customers who bought X"), moving to Neo4j (as planned for Phase 2) would be more efficient than many-to-many SQL joins.

## 7. Performance Metrics (Observed)
- **Average Generation Time**: ~800ms - 1.5s
- **Average Execution Time**: < 50ms (SQLite is extremely fast for this dataset size)
- **Success Rate**: High execution success rate for standard e-commerce queries due to comprehensive few-shot coverage.

## 8. Conclusion
The system successfully demonstrates that a lightweight, efficient LLM like Gemini 1.5 Flash, combined with RAG and strong validation, can create a reliable NL2SQL interface for business data.
