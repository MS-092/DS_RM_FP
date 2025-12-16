import subprocess
import time
import random
import csv
import requests
import datetime
import os

# --- CONFIGURATION BASED ON RESEARCH METHODOLOGY ---
# Target URL to check System Availability [cite: 134]
SYSTEM_URL = "http://localhost:8000/api/health" 
# Number of runs per configuration to ensure statistical power > 80% 
TOTAL_RUNS = 20 
# Chaos Mesh manifest to apply
# Assumes script is run from project root, or adjacent to infra folder
CHAOS_MANIFEST = "infra/chaos-mesh/pod-kill-experiment.yaml"
# Output file for analysis
DATA_FILE = "experiment_results_checkpointing_30s.csv"

def check_system_health():
    """Pings the system to check if it is available."""
    try:
        response = requests.get(SYSTEM_URL, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def inject_fault():
    """Applies the Chaos Mesh manifest using kubectl."""
    print(f"[{datetime.datetime.now()}] 💥 Injecting Fault: {CHAOS_MANIFEST}...")
    if not os.path.exists(CHAOS_MANIFEST):
        print(f"Error: Manifest file not found at {CHAOS_MANIFEST}")
        raise FileNotFoundError(f"{CHAOS_MANIFEST} not found")
        
    subprocess.run(["kubectl", "apply", "-f", CHAOS_MANIFEST], check=True)

def recover_fault():
    """Removes the Chaos Mesh manifest to allow auto-recovery."""
    print(f"[{datetime.datetime.now()}] 🧹 Cleaning up Fault...")
    subprocess.run(["kubectl", "delete", "-f", CHAOS_MANIFEST], check=True)

def run_experiment(run_id):
    """
    Executes a single experimental run.
    Logic follows the 'Recovery Time' variable definition.
    """
    print(f"\n--- Starting Run #{run_id} ---")
    
    # 1. Warm-up / Stabilization Phase 
    print("System stabilizing...")
    time.sleep(5) 

    # 2. Determine Failure Timing (Stratified Sampling) 
    # Simulates Early (0-25%), Mid (25-75%), or Late (75-100%) execution
    delay = random.randint(5, 15) 
    print(f"Waiting {delay}s before failure injection (simulating workload execution)...")
    time.sleep(delay)

    # 3. Inject Fault
    inject_fault()
    start_time = time.time()
    
    # 4. Measure Recovery Time
    # Poll system until it returns 200 OK
    while True:
        if check_system_health():
            end_time = time.time()
            break
        time.sleep(0.5) # Polling interval
    
    recovery_time = end_time - start_time
    print(f"✅ System Recovered! Time: {recovery_time:.2f} seconds")

    # 5. Cleanup
    recover_fault()
    
    # 6. Cooldown to prevent 'History Effect' bias 
    print("Cooling down for 10s...")
    time.sleep(10)

    return {
        "run_id": run_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "injection_delay": delay,
        "recovery_time_seconds": recovery_time,
        "status": "SUCCESS"
    }

# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    print(f"Starting Experiment Suite: N={TOTAL_RUNS} runs ")
    
    results = []
    
    # Initialize CSV with headers
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["run_id", "timestamp", "injection_delay", "recovery_time_seconds", "status"])
        writer.writeheader()

    for i in range(1, TOTAL_RUNS + 1):
        try:
            data = run_experiment(i)
            results.append(data)
            
            # Append result to CSV immediately (to save data on crash)
            with open(DATA_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["run_id", "timestamp", "injection_delay", "recovery_time_seconds", "status"])
                writer.writerow(data)
                
        except Exception as e:
            print(f"❌ Run #{i} Failed: {e}")

    print("\n\nExperiment Suite Completed.")
    print(f"Data saved to {DATA_FILE} for ANOVA analysis.")
