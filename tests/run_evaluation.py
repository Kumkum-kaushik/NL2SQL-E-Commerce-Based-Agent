"""
Comprehensive test suite for NL2SQL system.
Runs all test queries, measures performance, and generates detailed metrics.
"""

import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nl2sql.generator import nl_to_sql, nl_to_sql_with_strategy_comparison
from nl2sql.validator import validate_sql
from nl2sql.executor import execute_sql_with_limit


class TestRunner:
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.results = []
        self.strategy_comparison_results = []
        
    def load_test_queries(self) -> List[Dict]:
        """Load test queries from JSON file."""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_single_query_test(self, question: str, expected_sql: str, 
                             difficulty: str, strategy: int) -> Dict[str, Any]:
        """Run a single query test and collect metrics."""
        result = {
            'question': question,
            'expected_sql': expected_sql,
            'difficulty': difficulty,
            'strategy': strategy,
        }
        
        try:
            # Measure generation time
            gen_start = time.time()
            generated_sql = nl_to_sql(question, strategy=strategy)
            gen_time = (time.time() - gen_start) * 1000  # ms
            
            result['generated_sql'] = generated_sql
            result['generation_time_ms'] = round(gen_time, 2)
            
            # Validate SQL
            valid, msg = validate_sql(generated_sql)
            result['valid'] = valid
            result['validation_message'] = msg
            
            if not valid:
                result['execution_success'] = False
                result['error'] = msg
                return result
            
            # Execute SQL
            try:
                exec_start = time.time()
                exec_result = execute_sql_with_limit(generated_sql, max_rows=100)
                exec_time = (time.time() - exec_start) * 1000  # ms
                
                result['execution_time_ms'] = round(exec_time, 2)
                result['execution_success'] = True
                result['row_count'] = len(exec_result.get('rows', []))
                
            except Exception as e:
                result['execution_success'] = False
                result['error'] = str(e)
                
        except Exception as e:
            result['generation_success'] = False
            result['error'] = str(e)
            
        return result
    
    def run_all_tests(self):
        """Run all test queries for both strategies."""
        print("=" * 80)
        print("NL2SQL EVALUATION TEST SUITE")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        queries = self.load_test_queries()
        total_queries = len(queries)
        
        print(f"Loaded {total_queries} test queries\n")
        
        # Test both strategies
        for strategy in [1, 2]:
            strategy_name = "Schema-First" if strategy == 1 else "Chain-of-Thought"
            print(f"\n{'=' * 80}")
            print(f"Testing Strategy {strategy}: {strategy_name}")
            print(f"{'=' * 80}\n")
            
            for idx, query in enumerate(queries, 1):
                print(f"[{idx}/{total_queries}] Testing: {query['question'][:60]}...")
                
                result = self.run_single_query_test(
                    question=query['question'],
                    expected_sql=query.get('sql', ''),
                    difficulty=query['difficulty'],
                    strategy=strategy
                )
                
                self.results.append(result)
                
                # Print result
                if result.get('execution_success', False):
                    print(f"  ✓ Success | Gen: {result['generation_time_ms']}ms | "
                          f"Exec: {result['execution_time_ms']}ms | "
                          f"Rows: {result['row_count']}")
                else:
                    print(f"  ✗ Failed | Error: {result.get('error', 'Unknown')[:50]}")
        
        print(f"\n{'=' * 80}")
        print("Test suite completed!")
        print(f"{'=' * 80}\n")
    
    def run_strategy_comparison(self):
        """Run strategy comparison for selected queries."""
        print(f"\n{'=' * 80}")
        print("STRATEGY COMPARISON TEST")
        print(f"{'=' * 80}\n")
        
        queries = self.load_test_queries()
        
        # Test a few representative queries
        test_indices = [0, 6, 10, 13]  # Easy, medium, difficult queries
        
        for idx in test_indices:
            if idx < len(queries):
                query = queries[idx]
                print(f"Comparing strategies for: {query['question']}")
                
                try:
                    comparison = nl_to_sql_with_strategy_comparison(query['question'])
                    self.strategy_comparison_results.append({
                        'question': query['question'],
                        'difficulty': query['difficulty'],
                        'comparison': comparison
                    })
                    print(f"  ✓ Comparison complete\n")
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}\n")
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate metrics from test results."""
        metrics = {
            'total_queries': len(self.results) // 2,  # Divided by 2 strategies
            'strategies': {}
        }
        
        for strategy in [1, 2]:
            strategy_name = "Strategy 1 (Schema-First)" if strategy == 1 else "Strategy 2 (Chain-of-Thought)"
            strategy_results = [r for r in self.results if r['strategy'] == strategy]
            
            total = len(strategy_results)
            successful = len([r for r in strategy_results if r.get('execution_success', False)])
            valid = len([r for r in strategy_results if r.get('valid', False)])
            
            gen_times = [r['generation_time_ms'] for r in strategy_results if 'generation_time_ms' in r]
            exec_times = [r['execution_time_ms'] for r in strategy_results if 'execution_time_ms' in r]
            
            # By difficulty
            difficulties = {}
            for diff in ['easy', 'medium', 'difficult']:
                diff_results = [r for r in strategy_results if r['difficulty'] == diff]
                if diff_results:
                    diff_success = len([r for r in diff_results if r.get('execution_success', False)])
                    difficulties[diff] = {
                        'total': len(diff_results),
                        'successful': diff_success,
                        'success_rate': round((diff_success / len(diff_results)) * 100, 2)
                    }
            
            metrics['strategies'][strategy_name] = {
                'total_queries': total,
                'successful_executions': successful,
                'valid_queries': valid,
                'success_rate': round((successful / total) * 100, 2) if total > 0 else 0,
                'validation_rate': round((valid / total) * 100, 2) if total > 0 else 0,
                'avg_generation_time_ms': round(sum(gen_times) / len(gen_times), 2) if gen_times else 0,
                'avg_execution_time_ms': round(sum(exec_times) / len(exec_times), 2) if exec_times else 0,
                'min_generation_time_ms': round(min(gen_times), 2) if gen_times else 0,
                'max_generation_time_ms': round(max(gen_times), 2) if gen_times else 0,
                'by_difficulty': difficulties
            }
        
        return metrics
    
    def generate_report(self, output_file: str):
        """Generate markdown report with all results."""
        metrics = self.calculate_metrics()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# NL2SQL System - Test Results and Evaluation\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Test Queries:** {metrics['total_queries']}\n")
            f.write(f"- **Strategies Tested:** 2 (Schema-First, Chain-of-Thought)\n")
            f.write(f"- **Total Test Runs:** {len(self.results)}\n\n")
            
            # Overall Metrics
            f.write("## Performance Metrics by Strategy\n\n")
            
            for strategy_name, stats in metrics['strategies'].items():
                f.write(f"### {strategy_name}\n\n")
                f.write(f"| Metric | Value |\n")
                f.write(f"|--------|-------|\n")
                f.write(f"| Total Queries | {stats['total_queries']} |\n")
                f.write(f"| Successful Executions | {stats['successful_executions']} |\n")
                f.write(f"| Valid Queries | {stats['valid_queries']} |\n")
                f.write(f"| **Success Rate** | **{stats['success_rate']}%** |\n")
                f.write(f"| Validation Rate | {stats['validation_rate']}% |\n")
                f.write(f"| Avg Generation Time | {stats['avg_generation_time_ms']} ms |\n")
                f.write(f"| Avg Execution Time | {stats['avg_execution_time_ms']} ms |\n")
                f.write(f"| Min Generation Time | {stats['min_generation_time_ms']} ms |\n")
                f.write(f"| Max Generation Time | {stats['max_generation_time_ms']} ms |\n\n")
                
                # By difficulty
                f.write("#### Performance by Difficulty\n\n")
                f.write("| Difficulty | Total | Successful | Success Rate |\n")
                f.write("|------------|-------|------------|-------------|\n")
                for diff, diff_stats in stats['by_difficulty'].items():
                    f.write(f"| {diff.capitalize()} | {diff_stats['total']} | "
                           f"{diff_stats['successful']} | {diff_stats['success_rate']}% |\n")
                f.write("\n")
            
            # Detailed Results
            f.write("## Detailed Test Results\n\n")
            
            for strategy in [1, 2]:
                strategy_name = "Schema-First" if strategy == 1 else "Chain-of-Thought"
                f.write(f"### Strategy {strategy}: {strategy_name}\n\n")
                
                strategy_results = [r for r in self.results if r['strategy'] == strategy]
                
                for idx, result in enumerate(strategy_results, 1):
                    status = "✓ PASS" if result.get('execution_success', False) else "✗ FAIL"
                    f.write(f"#### Test {idx}: {status}\n\n")
                    f.write(f"**Question:** {result['question']}\n\n")
                    f.write(f"**Difficulty:** {result['difficulty']}\n\n")
                    f.write(f"**Generated SQL:**\n```sql\n{result.get('generated_sql', 'N/A')}\n```\n\n")
                    
                    if result.get('execution_success', False):
                        f.write(f"- Generation Time: {result['generation_time_ms']} ms\n")
                        f.write(f"- Execution Time: {result['execution_time_ms']} ms\n")
                        f.write(f"- Rows Returned: {result['row_count']}\n\n")
                    else:
                        f.write(f"- **Error:** {result.get('error', 'Unknown error')}\n\n")
                    
                    f.write("---\n\n")
            
            # Strategy Comparison
            if self.strategy_comparison_results:
                f.write("## Strategy Comparison Examples\n\n")
                for comp in self.strategy_comparison_results:
                    f.write(f"### {comp['question']}\n\n")
                    f.write(f"**Difficulty:** {comp['difficulty']}\n\n")
                    
                    comparison = comp['comparison']
                    for key in ['strategy_1', 'strategy_2']:
                        strategy_num = key.split('_')[1]
                        strategy_name = "Schema-First" if strategy_num == '1' else "Chain-of-Thought"
                        f.write(f"#### Strategy {strategy_num}: {strategy_name}\n\n")
                        
                        if key in comparison:
                            data = comparison[key]
                            f.write(f"```sql\n{data.get('sql', 'N/A')}\n```\n\n")
                            f.write(f"- Generation Time: {data.get('generation_time_ms', 'N/A')} ms\n")
                            f.write(f"- Valid: {data.get('valid', 'N/A')}\n\n")
                    
                    f.write("---\n\n")
        
        print(f"\n✓ Report generated: {output_file}")
    
    def save_raw_results(self, output_file: str):
        """Save raw results as JSON for further analysis."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'strategy_comparisons': self.strategy_comparison_results,
            'metrics': self.calculate_metrics()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Raw results saved: {output_file}")


def main():
    """Main execution function."""
    # File paths
    test_file = os.path.join(os.path.dirname(__file__), 'test_queries.json')
    results_md = os.path.join(os.path.dirname(__file__), 'test_results.md')
    results_json = os.path.join(os.path.dirname(__file__), 'test_results.json')
    
    # Create test runner
    runner = TestRunner(test_file)
    
    # Run tests
    runner.run_all_tests()
    
    # Run strategy comparison
    runner.run_strategy_comparison()
    
    # Generate reports
    runner.generate_report(results_md)
    runner.save_raw_results(results_json)
    
    # Print summary
    metrics = runner.calculate_metrics()
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for strategy_name, stats in metrics['strategies'].items():
        print(f"\n{strategy_name}:")
        print(f"  Success Rate: {stats['success_rate']}%")
        print(f"  Avg Generation Time: {stats['avg_generation_time_ms']} ms")
        print(f"  Avg Execution Time: {stats['avg_execution_time_ms']} ms")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
