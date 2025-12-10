#!/usr/bin/env python3
"""
Load Testing Script for GitForge - Repository Cloning
Simulates multiple users cloning repositories concurrently
"""

import asyncio
import subprocess
import time
from datetime import datetime
import argparse
import json
import os
import tempfile
import shutil

GITEA_URL = "http://localhost:3000"

async def clone_repository(repo_url, clone_num, temp_dir):
    """Clone a repository"""
    clone_dir = os.path.join(temp_dir, f"clone_{clone_num}")
    
    try:
        start_time = time.time()
        
        # Run git clone
        process = await asyncio.create_subprocess_exec(
            "git", "clone", repo_url, clone_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        end_time = time.time()
        
        if process.returncode == 0:
            # Get repository size
            size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(clone_dir)
                for filename in filenames
            )
            
            return {
                "success": True,
                "duration": end_time - start_time,
                "size_bytes": size,
                "clone_num": clone_num
            }
        else:
            return {
                "success": False,
                "duration": end_time - start_time,
                "error": stderr.decode(),
                "clone_num": clone_num
            }
    except Exception as e:
        return {
            "success": False,
            "duration": 0,
            "error": str(e),
            "clone_num": clone_num
        }

async def run_clone_test(repo_url, num_clones=10, concurrent=3):
    """Run clone load test"""
    print(f"Starting clone test: {num_clones} clones, {concurrent} concurrent")
    print(f"Repository: {repo_url}")
    print("-" * 60)
    
    # Create temporary directory for clones
    temp_dir = tempfile.mkdtemp(prefix="gitforge_clone_test_")
    print(f"Using temp directory: {temp_dir}")
    
    try:
        results = []
        start_time = time.time()
        
        # Clone in batches
        for batch_start in range(0, num_clones, concurrent):
            batch_end = min(batch_start + concurrent, num_clones)
            
            print(f"Cloning batch {batch_start + 1} to {batch_end}...")
            
            tasks = [
                clone_repository(repo_url, i, temp_dir)
                for i in range(batch_start, batch_end)
            ]
            
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            # Brief pause between batches
            if batch_end < num_clones:
                await asyncio.sleep(0.5)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate statistics
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        durations = [r["duration"] for r in successful]
        sizes = [r.get("size_bytes", 0) for r in successful]
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        total_size = sum(sizes)
        avg_size = total_size / len(sizes) if sizes else 0
        
        # Print results
        print("\n" + "=" * 60)
        print("CLONE TEST RESULTS")
        print("=" * 60)
        print(f"Total Clones:        {num_clones}")
        print(f"Successful:          {len(successful)} ({len(successful)/num_clones*100:.1f}%)")
        print(f"Failed:              {len(failed)} ({len(failed)/num_clones*100:.1f}%)")
        print(f"Total Duration:      {total_duration:.2f}s")
        print(f"Throughput:          {num_clones/total_duration:.2f} clones/sec")
        print(f"\nClone Times:")
        print(f"  Average:           {avg_duration:.2f}s")
        print(f"  Min:               {min_duration:.2f}s")
        print(f"  Max:               {max_duration:.2f}s")
        print(f"\nData Transfer:")
        print(f"  Total:             {total_size/1024/1024:.2f} MB")
        print(f"  Average per clone: {avg_size/1024/1024:.2f} MB")
        
        if failed:
            print(f"\nFailed Clones:")
            for i, result in enumerate(failed[:5]):
                print(f"  {i+1}. Clone #{result['clone_num']}: {result.get('error', 'Unknown error')[:100]}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")
        
        # Save results
        output_file = f"clone_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "test_config": {
                    "repo_url": repo_url,
                    "num_clones": num_clones,
                    "concurrent": concurrent
                },
                "summary": {
                    "total": num_clones,
                    "successful": len(successful),
                    "failed": len(failed),
                    "total_duration": total_duration,
                    "throughput": num_clones/total_duration,
                    "avg_clone_time": avg_duration,
                    "total_size_mb": total_size/1024/1024,
                    "avg_size_mb": avg_size/1024/1024
                },
                "results": results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {output_file}")
        print("=" * 60)
        
    finally:
        # Cleanup
        print(f"\nCleaning up temporary directory...")
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="Load test GitForge repository cloning")
    parser.add_argument("repo_url", help="Repository URL to clone (e.g., http://localhost:3000/user/repo.git)")
    parser.add_argument("-n", "--num-clones", type=int, default=10,
                        help="Number of times to clone (default: 10)")
    parser.add_argument("-c", "--concurrent", type=int, default=3,
                        help="Number of concurrent clones (default: 3)")
    
    args = parser.parse_args()
    
    # Check if git is available
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: git command not found. Please install git.")
        return
    
    asyncio.run(run_clone_test(args.repo_url, args.num_clones, args.concurrent))

if __name__ == "__main__":
    main()
