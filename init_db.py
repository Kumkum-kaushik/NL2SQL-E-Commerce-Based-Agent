"""
Initialize the NL2SQL E-Commerce database and vector store.

Run this script once to set up the database with schema and seed data,
and initialize the FAISS vector store with few-shot examples.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nl2sql.database import init_database
from nl2sql.vector_store import create_vector_store_from_file

def main():
    print("=" * 60)
    print("NL2SQL E-Commerce - Database Initialization")
    print("=" * 60)
    print()
    
    # Initialize SQLite database
    print("Step 1: Initializing SQLite database...")
    try:
        init_database()
        print("[OK] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        return
    
    print()
    
    # Initialize vector store
    print("Step 2: Initializing FAISS vector store...")
    try:
        examples_file = project_root / "tests" / "test_queries.json"
        vector_store = create_vector_store_from_file(str(examples_file))
        print(f"[OK] Vector store initialized with {len(vector_store.examples)} examples")
    except Exception as e:
        print(f"[ERROR] Error initializing vector store: {e}")
        return
    
    print()
    print("=" * 60)
    print("[OK] Initialization complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the API server: python run.py")
    print("3. Visit http://127.0.0.1:8000/docs for API documentation")
    print()

if __name__ == "__main__":
    main()
