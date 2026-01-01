#!/usr/bin/env python3
"""
Automated Experiment Runner for Fault Tolerance Research

This script runs N experiments per strategy configuration and collects
data for statistical analysis (ANOVA, T-tests, etc.)

Usage:
    python3 scripts/run_ft_experiments.py

Output:
    CSV file with all experiment results
"""

import requests
import csv
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any

# Configuration
API_BASE = "http://localhost:8000/api/fault-tolerance"
DEFAULT_RUNS = 20
DEFAULT_DATA_ITEMS = 100
COOLDOWN_SECONDS = 2

# Research configurations based on the design document
CONFIGURATIONS = [
    # Baseline (Control Group)
    {
        "strategy": "baseline",
        "name": "Baseline",
        "description": "No fault tolerance - control group"
    },
    
    # Checkpointing with different intervals
    {
        "strategy": "checkpointing",
        "checkpoint_interval": 15,
        "name": "Checkpoint_15s",
        "description": "Checkpointing every 15 seconds"
    },
    {
        "strategy": "checkpointing",
        "checkpoint_interval": 30,
        "name": "Checkpoint_30s",
        "description": "Checkpointing every 30 seconds"
    },
    {
        "strategy": "checkpointing",
        "checkpoint_interval": 60,
        "name": "Checkpoint_60s",
        "description": "Checkpointing every 60 seconds"
    },
    {
        "strategy": "checkpointing",
        "checkpoint_interval": 120,
        "name": "Checkpoint_120s",
        "description": "Checkpointing every 120 seconds"
    },
    
    # Replication with different factors
    {
        "strategy": "replication",
        "replication_factor": 2,
        "name": "Replication_F2",
        "description": "Replication factor 2 (tolerates 1 failure)"
    },
    {
        "strategy": "replication",
        "replication_factor": 3,
        "name": "Replication_F3",
        "description": "Replication factor 3 (majority quorum)"
    },
    {
        "strategy": "replication",
        "replication_factor": 5,
        "name": "Replication_F5",
        "description": "Replication factor 5 (tolerates 2 failures)"
    },
    
    # Hybrid combinations
    {
        "strategy": "hybrid",
        "checkpoint_interval": 30,
        "replication_factor": 3,
        "name": "Hybrid_30s_F3",
        "description": "Hybrid: 30s checkpoint + 3x replication"
    },
    {
        "strategy": "hybrid",
        "checkpoint_interval": 15,
        "replication_factor": 3,
        "name": "Hybrid_15s_F3",
        "description": "Hybrid: 15s checkpoint + 3x replication"
    },
]


def check_api_health() -> bool:
    """Check if the backend API is accessible."""
    try:
        response = requests.get(f"{API_BASE}/status", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def run_single_experiment(config: Dict[str, Any], data_items: int) -> Dict[str, Any]:
    """
    Run a single experiment with the given configuration.
    
    Args:
        config: Strategy configuration
        data_items: Number of test items to use
        
    Returns:
        Experiment results dictionary
    """
    # Decide if we should trigger a forced checkpoint to test persistence efficacy
    # We trigger it for 'checkpointing' and 'hybrid' strategies to demonstrate they CAN save data
    should_trigger = config["strategy"] in ["checkpointing", "hybrid"]
    
    payload = {
        "strategy": config["strategy"],
        "data_items": data_items,
        "checkpoint_interval": config.get("checkpoint_interval", 30),
        "replication_factor": config.get("replication_factor", 3),
        "trigger_checkpoint": should_trigger
    }
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_BASE}/run-experiment",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except (requests.ConnectionError, requests.Timeout) as e:
            if attempt < max_retries - 1:
                # print(f"    ⚠️ Connection warning (Run {attempt+1}/{max_retries}), retrying...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise Exception(f"Connection failed after {max_retries} retries: {str(e)}")
                
    return {} # Should not be reached


def run_experiment_suite(
    runs_per_config: int = DEFAULT_RUNS,
    data_items: int = DEFAULT_DATA_ITEMS,
    configs: List[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Run the complete experiment suite.
    
    Args:
        runs_per_config: Number of runs per configuration
        data_items: Test data items per run
        configs: List of configurations to test
        
    Returns:
        List of all experiment results
    """
    if configs is None:
        configs = CONFIGURATIONS
    
    results = []
    total_experiments = len(configs) * runs_per_config
    completed = 0
    
    print(f"\n{'='*60}")
    print(f"🧪 FAULT TOLERANCE EXPERIMENT SUITE")
    print(f"{'='*60}")
    print(f"Configurations: {len(configs)}")
    print(f"Runs per config: {runs_per_config}")
    print(f"Total experiments: {total_experiments}")
    print(f"Data items per run: {data_items}")
    print(f"{'='*60}\n")
    
    for config in configs:
        print(f"\n📋 Configuration: {config['name']}")
        print(f"   {config.get('description', '')}")
        print(f"   Strategy: {config['strategy']}")
        
        config_results = []
        
        for run in range(1, runs_per_config + 1):
            completed += 1
            progress = (completed / total_experiments) * 100
            
            print(f"   Run {run:02d}/{runs_per_config} [{progress:5.1f}%]...", end=" ", flush=True)
            
            try:
                start_time = time.time()
                result = run_single_experiment(config, data_items)
                elapsed = time.time() - start_time
                
                # Build result record
                record = {
                    "config_name": config["name"],
                    "strategy": config["strategy"],
                    "checkpoint_interval": config.get("checkpoint_interval", None),
                    "replication_factor": config.get("replication_factor", None),
                    "run_id": run,
                    "timestamp": datetime.now().isoformat(),
                    "recovery_time_seconds": result["recovery_time_seconds"],
                    "data_recovery_rate_percent": result["data_recovery_rate_percent"],
                    "items_stored": data_items,
                    "items_recovered": result["items_recovered"],
                    "store_time_seconds": result["store_time_seconds"],
                    "experiment_duration_seconds": elapsed,
                    "status": "SUCCESS"
                }
                
                config_results.append(record)
                results.append(record)
                
                print(f"✅ Recovery: {result['recovery_time_seconds']:.4f}s, "
                      f"Data: {result['data_recovery_rate_percent']:.1f}%")
                
            except Exception as e:
                print(f"❌ FAILED: {e}")
                results.append({
                    "config_name": config["name"],
                    "strategy": config["strategy"],
                    "run_id": run,
                    "timestamp": datetime.now().isoformat(),
                    "status": "FAILED",
                    "error": str(e)
                })
            
            # Cooldown between runs
            if run < runs_per_config:
                time.sleep(COOLDOWN_SECONDS)
        
        # Summary for this configuration
        if config_results:
            avg_recovery = sum(r["recovery_time_seconds"] for r in config_results) / len(config_results)
            avg_data_rate = sum(r["data_recovery_rate_percent"] for r in config_results) / len(config_results)
            print(f"   📊 Summary: Avg Recovery={avg_recovery:.4f}s, Avg Data Recovery={avg_data_rate:.1f}%")
    
    return results


def save_results(results: List[Dict], filename: str = None) -> str:
    """Save experiment results to CSV."""
    if filename is None:
        filename = f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Get all unique keys from results
    fieldnames = set()
    for r in results:
        fieldnames.update(r.keys())
    fieldnames = sorted(list(fieldnames))
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    return filename


def print_summary(results: List[Dict]):
    """Print a summary of experiment results."""
    print(f"\n{'='*60}")
    print("📊 EXPERIMENT SUMMARY")
    print(f"{'='*60}")
    
    # Group by configuration
    from collections import defaultdict
    by_config = defaultdict(list)
    for r in results:
        if r.get("status") == "SUCCESS":
            by_config[r["config_name"]].append(r["recovery_time_seconds"])
    
    print(f"\n{'Configuration':<20} {'Runs':>6} {'Mean (s)':>10} {'Std (s)':>10} {'Min (s)':>10} {'Max (s)':>10}")
    print("-" * 70)
    
    for config_name, times in sorted(by_config.items()):
        if times:
            mean_t = sum(times) / len(times)
            min_t = min(times)
            max_t = max(times)
            std_t = (sum((t - mean_t) ** 2 for t in times) / len(times)) ** 0.5
            
            print(f"{config_name:<20} {len(times):>6} {mean_t:>10.4f} {std_t:>10.4f} {min_t:>10.4f} {max_t:>10.4f}")
    
    print(f"\n{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Run fault tolerance experiments for distributed systems research"
    )
    parser.add_argument(
        "-n", "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help=f"Number of runs per configuration (default: {DEFAULT_RUNS})"
    )
    parser.add_argument(
        "-d", "--data-items",
        type=int,
        default=DEFAULT_DATA_ITEMS,
        help=f"Number of data items per experiment (default: {DEFAULT_DATA_ITEMS})"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output CSV filename"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["baseline", "checkpointing", "replication", "hybrid", "all"],
        default="all",
        help="Run only specific strategy type"
    )
    
    args = parser.parse_args()
    
    # Check API health
    print("🔍 Checking API health...")
    if not check_api_health():
        print("❌ ERROR: Backend API not accessible at", API_BASE)
        print("   Make sure the backend is running:")
        print("   - Local: cd backend && uvicorn main:app --port 8000")
        print("   - K8s: kubectl port-forward svc/backend 8000:8000 -n gitforge")
        return 1
    print("✅ API is healthy\n")
    
    # Filter configurations if needed
    configs = CONFIGURATIONS
    if args.strategy != "all":
        configs = [c for c in CONFIGURATIONS if c["strategy"] == args.strategy]
        print(f"📌 Filtering to {args.strategy} configurations only ({len(configs)} configs)")
    
    # Run experiments
    results = run_experiment_suite(
        runs_per_config=args.runs,
        data_items=args.data_items,
        configs=configs
    )
    
    # Save results
    filename = save_results(results, args.output)
    print(f"\n💾 Results saved to: {filename}")
    
    # Print summary
    print_summary(results)
    
    print("\n✅ Experiment suite completed!")
    return 0


if __name__ == "__main__":
    exit(main())
