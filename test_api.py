import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    """Test root endpoint."""
    print("Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Failed: {e}")
        return False

def test_schema():
    """Test schema endpoint."""
    print("\nTesting Schema Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/schema")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Tables: {list(data['tables'].keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"Failed: {e}")
        return False

def test_nl2sql(question, execute=True):
    """Test NL2SQL generation and execution."""
    print(f"\nTesting NL2SQL: '{question}'")
    try:
        payload = {
            "question": question,
            "execute": execute,
            "strategy": 1
        }
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/nl2sql", json=payload)
        duration = time.time() - start
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if "sql" in data:
            print(f"Generated SQL: {data['sql']}")
            print(f"Valid: {data.get('valid', 'Unknown')}")
            print(f"Generation Time: {data.get('generation_time_ms', 'N/A')} ms")
        
        if "result" in data:
            result = data["result"]
            print(f"Execution Success: {result.get('success', False)}")
            print(f"Rows Returned: {result.get('row_count', 0)}")
            if result.get('data'):
                print(f"First Row: {result['data'][0]}")
        
        if "error" in data:
            print(f"Error: {data['error']}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"Failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("NL2SQL System Verification")
    print("="*60)
    
    # Wait for server to be ready
    print("Waiting for server...")
    time.sleep(2)
    
    if test_root() and test_schema():
        test_nl2sql("Show total sales by category")
        test_nl2sql("List all customers from USA")
        test_nl2sql("What is the most popular product?")
        test_nl2sql("Show me failure invalid table name") # Expected failure
    else:
        print("\nServer validation failed!")
