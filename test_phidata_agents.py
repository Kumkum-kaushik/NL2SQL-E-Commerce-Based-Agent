"""
Test script for Phidata NL2SQL Agent Team
Tests the complete workflow from natural language to SQL execution
"""
import logging
import sys
from nl2sql.agents.team import process_nl2sql_request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simple_query():
    """Test a simple query."""
    print("\n" + "="*80)
    print("TEST 1: Simple Product Query")
    print("="*80)
    
    question = "Show me the top 5 products by price"
    
    result = process_nl2sql_request(
        question=question,
        execute=True,
        strategy=1,
        max_rows=5
    )
    
    print(f"\nQuestion: {result['question']}")
    print(f"Generated SQL: {result['sql']}")
    print(f"Valid: {result['valid']}")
    print(f"Generation Time: {result.get('generation_time_ms', 0)}ms")
    
    if result.get('execution_result'):
        exec_result = result['execution_result']
        if exec_result.get('success'):
            print(f"Execution Success: {exec_result['row_count']} rows returned")
            print("\nSample Data:")
            for row in exec_result['data'][:3]:
                print(f"  {row}")
        else:
            print(f"Execution Failed: {exec_result.get('error')}")
    
    print(f"\nTotal Time: {result.get('total_time_ms', 0)}ms")
    return result

def test_aggregation_query():
    """Test an aggregation query."""
    print("\n" + "="*80)
    print("TEST 2: Aggregation Query")
    print("="*80)
    
    question = "What is the total number of orders?"
    
    result = process_nl2sql_request(
        question=question,
        execute=True,
        strategy=2,  # Use chain-of-thought strategy
        max_rows=10
    )
    
    print(f"\nQuestion: {result['question']}")
    print(f"Generated SQL: {result['sql']}")
    print(f"Valid: {result['valid']}")
    
    if result.get('execution_result'):
        exec_result = result['execution_result']
        if exec_result.get('success'):
            print(f"Result: {exec_result['data']}")
        else:
            print(f"Execution Failed: {exec_result.get('error')}")
    
    return result

def test_validation_only():
    """Test SQL generation without execution."""
    print("\n" + "="*80)
    print("TEST 3: Validation Only (No Execution)")
    print("="*80)
    
    question = "List all customers"
    
    result = process_nl2sql_request(
        question=question,
        execute=False,  # Don't execute
        strategy=1
    )
    
    print(f"\nQuestion: {result['question']}")
    print(f"Generated SQL: {result['sql']}")
    print(f"Valid: {result['valid']}")
    print(f"Validation Message: {result.get('validation_message')}")
    
    return result

def main():
    """Run all tests."""
    print("\n" + "#"*80)
    print("# PHIDATA NL2SQL AGENT TEAM - TEST SUITE")
    print("#"*80)
    
    try:
        # Test 1: Simple query
        result1 = test_simple_query()
        
        # Test 2: Aggregation
        result2 = test_aggregation_query()
        
        # Test 3: Validation only
        result3 = test_validation_only()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Test 1 (Simple): {'PASS' if result1.get('valid') else 'FAIL'}")
        print(f"Test 2 (Aggregation): {'PASS' if result2.get('valid') else 'FAIL'}")
        print(f"Test 3 (Validation): {'PASS' if result3.get('valid') else 'FAIL'}")
        print("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
