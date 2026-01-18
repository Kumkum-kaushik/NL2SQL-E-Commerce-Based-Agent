from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time
import os
from collections import defaultdict
import threading

from nl2sql.agents.team import process_nl2sql_request
from nl2sql.validator import validate_sql
from nl2sql.executor import execute_sql, execute_sql_with_limit
from nl2sql.database import db_manager
# Note: Cache and rate limit stats removed as Gemini handles this differently

app = FastAPI(
    title="NL2SQL E-Commerce API",
    description="Convert natural language to SQL queries using Google Gemini AI and Phidata Agent Team",
    version="2.0.0"
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
        "version": "2.0.0",
        "framework": "Phidata",
        "database": "SQLite",
        "vector_db": "Pinecone",
        "llm": "Google Gemini 1.5 Flash"
    }

@app.post("/api/nl2sql")
def generate_and_execute(req: NL2SQLRequest):
    """
    Convert natural language to SQL using Phidata Agent Team and optionally execute.
    
    Args:
        question: Natural language question
        execute: Whether to execute the query
        strategy: Prompt strategy (1 or 2)
        max_rows: Maximum rows to return
    
    Returns:
        Generated SQL and optionally execution results with workflow details
    """
    try:
        # Use agent team workflow
        result = process_nl2sql_request(
            question=req.question,
            execute=req.execute,
            strategy=req.strategy,
            max_rows=req.max_rows
        )
        
        return result
        
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
