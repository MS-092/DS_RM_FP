#!/usr/bin/env python3
"""
Load Testing Script for GitForge - Issue Creation
Creates multiple issues concurrently to test API performance
"""

import asyncio
import httpx
import time
from datetime import datetime
import argparse
import json

API_BASE_URL = "http://localhost:8000"

async def create_issue(client, issue_num, repository="load-test-repo"):
    """Create a single issue"""
    issue_data = {
        "title": f"Load Test Issue #{issue_num}",
        "description": f"This is a load test issue created at {datetime.now().isoformat()}",
        "repository": repository,
        "created_by": f"load-tester-{issue_num % 10}"
    }
    
    try:
        start_time = time.time()
        response = await client.post(f"{API_BASE_URL}/api/issues/", json=issue_data)
        end_time = time.time()
        
        if response.status_code == 200:
            return {
                "success": True,
                "issue_id": response.json().get("id"),
                "duration": end_time - start_time
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "duration": end_time - start_time
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "duration": 0
        }

async def run_load_test(num_issues=100, concurrent=10):
    """Run load test with specified parameters"""
    print(f"Starting load test: {num_issues} issues, {concurrent} concurrent requests")
    print(f"Target API: {API_BASE_URL}")
    print("-" * 60)
    
    results = []
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Create issues in batches
        for batch_start in range(0, num_issues, concurrent):
            batch_end = min(batch_start + concurrent, num_issues)
            batch_size = batch_end - batch_start
            
            print(f"Creating issues {batch_start + 1} to {batch_end}...")
            
            tasks = [
                create_issue(client, i)
                for i in range(batch_start, batch_end)
            ]
            
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            # Brief pause between batches
            if batch_end < num_issues:
                await asyncio.sleep(0.1)
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Calculate statistics
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    durations = [r["duration"] for r in successful]
    avg_duration = sum(durations) / len(durations) if durations else 0
    min_duration = min(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    
    # Print results
    print("\n" + "=" * 60)
    print("LOAD TEST RESULTS")
    print("=" * 60)
    print(f"Total Issues:        {num_issues}")
    print(f"Successful:          {len(successful)} ({len(successful)/num_issues*100:.1f}%)")
    print(f"Failed:              {len(failed)} ({len(failed)/num_issues*100:.1f}%)")
    print(f"Total Duration:      {total_duration:.2f}s")
    print(f"Throughput:          {num_issues/total_duration:.2f} issues/sec")
    print(f"\nResponse Times:")
    print(f"  Average:           {avg_duration*1000:.2f}ms")
    print(f"  Min:               {min_duration*1000:.2f}ms")
    print(f"  Max:               {max_duration*1000:.2f}ms")
    
    if failed:
        print(f"\nFailed Requests:")
        for i, result in enumerate(failed[:5]):  # Show first 5 failures
            print(f"  {i+1}. {result.get('error', result.get('status_code', 'Unknown error'))}")
        if len(failed) > 5:
            print(f"  ... and {len(failed) - 5} more")
    
    # Save detailed results
    output_file = f"load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "test_config": {
                "num_issues": num_issues,
                "concurrent": concurrent,
                "api_url": API_BASE_URL
            },
            "summary": {
                "total": num_issues,
                "successful": len(successful),
                "failed": len(failed),
                "total_duration": total_duration,
                "throughput": num_issues/total_duration,
                "avg_response_time": avg_duration,
                "min_response_time": min_duration,
                "max_response_time": max_duration
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Load test GitForge issue creation")
    parser.add_argument("-n", "--num-issues", type=int, default=100,
                        help="Number of issues to create (default: 100)")
    parser.add_argument("-c", "--concurrent", type=int, default=10,
                        help="Number of concurrent requests (default: 10)")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000",
                        help="API base URL (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    global API_BASE_URL
    API_BASE_URL = args.api_url
    
    asyncio.run(run_load_test(args.num_issues, args.concurrent))

if __name__ == "__main__":
    main()
