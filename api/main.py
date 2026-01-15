from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time
import os
from collections import defaultdict
import threading

from nl2sql.generator import nl_to_sql, nl_to_sql_with_strategy_comparison
from nl2sql.validator import validate_sql
from nl2sql.executor import execute_sql, execute_sql_with_limit
from nl2sql.database import db_manager
from nl2sql.llm_client import get_cache_stats, get_rate_limit_stats, clear_cache

app = FastAPI(
    title="NL2SQL E-Commerce API",
    description="Convert natural language to SQL queries using Gemini AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# API-level rate limiting (per IP)
API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "20"))  # requests per minute
api_rate_tracker = defaultdict(list)
api_rate_lock = threading.Lock()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    API-level rate limiting middleware (per IP address).
    """
    client_ip = request.client.host
    current_time = time.time()
    
    with api_rate_lock:
        # Clean up old requests (older than 60 seconds)
        api_rate_tracker[client_ip] = [
            req_time for req_time in api_rate_tracker[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(api_rate_tracker[client_ip]) >= API_RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": f"Rate limit exceeded: {API_RATE_LIMIT} requests per minute",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        api_rate_tracker[client_ip].append(current_time)
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(API_RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(
        API_RATE_LIMIT - len(api_rate_tracker[client_ip])
    )
    
    return response

class NL2SQLRequest(BaseModel):
    question: str
    execute: bool = True
    strategy: int = 1  # 1 or 2
    max_rows: int = 100

class ValidateRequest(BaseModel):
    sql_query: str

@app.get("/")
def root():
    """API health check."""
    return {
        "message": "NL2SQL E-commerce API is running",
        "version": "1.0.0",
        "database": "SQLite",
        "llm": "Gemini 1.5 Flash"
    }

@app.post("/api/nl2sql")
def generate_and_execute(req: NL2SQLRequest):
    """
    Convert natural language to SQL and optionally execute.
    
    Args:
        question: Natural language question
        execute: Whether to execute the query
        strategy: Prompt strategy (1 or 2)
        max_rows: Maximum rows to return
    
    Returns:
        Generated SQL and optionally execution results
    """
    start_time = time.time()
    
    try:
        # Generate SQL
        sql = nl_to_sql(req.question, strategy=req.strategy)
        generation_time = (time.time() - start_time) * 1000  # ms
        
        # Validate SQL
        valid, msg = validate_sql(sql)
        if not valid:
            return {
                "question": req.question,
                "sql": sql,
                "valid": False,
                "error": msg,
                "generation_time_ms": round(generation_time, 2)
            }
        
        response = {
            "question": req.question,
            "sql": sql,
            "valid": True,
            "generation_time_ms": round(generation_time, 2)
        }
        
        # Execute if requested
        if req.execute:
            exec_start = time.time()
            result = execute_sql_with_limit(sql, max_rows=req.max_rows)
            exec_time = (time.time() - exec_start) * 1000  # ms
            
            response["execution_time_ms"] = round(exec_time, 2)
            response["result"] = result
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/validate")
def validate_only(req: ValidateRequest):
    """
    Validate SQL query without execution.
    
    Args:
        sql_query: SQL query to validate
    
    Returns:
        Validation result
    """
    try:
        valid, msg = validate_sql(req.sql_query)
        return {
            "sql": req.sql_query,
            "valid": valid,
            "message": msg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schema")
async def get_schema(request: Request):
    """Get database schema information."""
    try:
        schema = db_manager.get_schema_info()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare-strategies")
def compare_strategies(question: str):
    """
    Compare both prompt strategies for a question.
    
    Args:
        question: Natural language question
    
    Returns:
        Results from both strategies
    """
    try:
        result = nl_to_sql_with_strategy_comparison(question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/cache")
def get_cache_statistics():
    """
    Get cache statistics.
    
    Returns:
        Cache hits, misses, size, and hit rate
    """
    try:
        return get_cache_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/rate-limit")
def get_rate_limit_statistics():
    """
    Get rate limiter statistics.
    
    Returns:
        Request counts, tokens remaining, and limits
    """
    try:
        return get_rate_limit_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cache/clear")
def clear_cache_endpoint():
    """
    Clear the cache.
    
    Returns:
        Success message
    """
    try:
        clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
