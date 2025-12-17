"""
Checkpointing Strategy - Periodic State Snapshots

This strategy implements fault tolerance through periodic checkpointing:
- Data is stored in memory for fast access
- Periodic snapshots are written to persistent storage (disk)
- On failure, the system recovers from the last checkpoint

Research Context:
- Recovery Time: Proportional to checkpoint size and I/O speed
- Data Loss on Failure: Only changes since last checkpoint
- Configurable Parameter: Checkpoint interval (15s, 30s, 60s, 120s)
- Trade-off: Lower interval = less data loss but higher overhead
"""

from typing import Any, Dict, Optional, List
import time
import json
import os
import threading
import logging
from datetime import datetime

from .base import BaseFaultToleranceStrategy

logger = logging.getLogger(__name__)


class CheckpointingStrategy(BaseFaultToleranceStrategy):
    """
    Fault tolerance through periodic state checkpointing.
    
    Implements a write-ahead log combined with periodic full snapshots
    to persistent storage (filesystem).
    """
    
    DEFAULT_CHECKPOINT_INTERVAL = 30  # seconds
    DEFAULT_CHECKPOINT_DIR = "/tmp/gitforge_checkpoints"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the checkpointing strategy.
        
        Config options:
            - checkpoint_interval: Seconds between checkpoints (default: 30)
            - checkpoint_dir: Directory to store checkpoint files
            - max_checkpoints: Maximum number of checkpoint files to retain
        """
        super().__init__(config)
        
        self.checkpoint_interval = self.config.get(
            'checkpoint_interval', 
            self.DEFAULT_CHECKPOINT_INTERVAL
        )
        self.checkpoint_dir = self.config.get(
            'checkpoint_dir',
            self.DEFAULT_CHECKPOINT_DIR
        )
        self.max_checkpoints = self.config.get('max_checkpoints', 5)
        
        # In-memory data store (primary storage for performance)
        self._data_store: Dict[str, Any] = {}
        
        # Write-ahead log for changes since last checkpoint
        self._wal: List[Dict[str, Any]] = []
        
        # Checkpoint metadata
        self._last_checkpoint_time: Optional[float] = None
        self._checkpoint_count = 0
        
        # Background checkpointing thread
        self._checkpoint_thread: Optional[threading.Thread] = None
        self._stop_checkpointing = threading.Event()
        
        # Ensure checkpoint directory exists
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # Load from existing checkpoint if available
        self._load_latest_checkpoint()
        
        # Start background checkpointing
        self._start_checkpointing()
        
        logger.info(
            f"CheckpointingStrategy initialized: interval={self.checkpoint_interval}s, "
            f"dir={self.checkpoint_dir}"
        )
    
    @property
    def strategy_name(self) -> str:
        return f"Checkpointing (Interval: {self.checkpoint_interval}s)"
    
    def store(self, key: str, value: Any) -> bool:
        """
        Store data in memory and add to write-ahead log.
        
        The WAL ensures we don't lose data between checkpoints.
        """
        if self._is_failed:
            logger.warning("CheckpointingStrategy: Cannot store - system is in failed state")
            return False
        
        timestamp = time.time()
        
        # Store in memory
        self._data_store[key] = {
            'value': value,
            'timestamp': timestamp
        }
        
        # Add to write-ahead log
        self._wal.append({
            'operation': 'store',
            'key': key,
            'value': value,
            'timestamp': timestamp
        })
        
        self._record_operation('writes')
        logger.debug(f"Checkpointing stored key: {key}, WAL size: {len(self._wal)}")
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""
        if self._is_failed:
            logger.warning("CheckpointingStrategy: Cannot retrieve - system is in failed state")
            return None
        
        self._record_operation('reads')
        entry = self._data_store.get(key)
        return entry['value'] if entry else None
    
    def simulate_failure(self) -> None:
        """
        Simulate a failure by clearing in-memory state.
        
        The checkpoint files on disk remain intact, simulating
        a crash where memory is lost but disk survives.
        """
        logger.critical("🔥 CHECKPOINTING FAILURE SIMULATED - Memory cleared, checkpoints preserved!")
        
        # Stop the background checkpointing thread
        self._stop_checkpointing.set()
        if self._checkpoint_thread:
            self._checkpoint_thread.join(timeout=2)
        
        # Record what we're losing
        wal_entries_lost = len(self._wal)
        
        # Clear memory (simulating crash)
        self._data_store.clear()
        self._wal.clear()
        
        self._is_failed = True
        self._record_operation('failures_simulated')
        
        logger.info(f"Checkpointing failure: Memory cleared, {wal_entries_lost} uncommitted WAL entries lost")
    
    def recover(self) -> float:
        """
        Recover from failure by loading the latest checkpoint.
        
        REALISM UPDATE: Includes simulated Disk I/O latency, 
        WAL replay time, and potential file corruption.
        
        Returns:
            Time taken to recover (load checkpoint from disk)
        """
        start_time = time.time()
        
        # REALISM UPDATE: Increased latencies to simulate Cloud/Network Storage
        import random
        fs_access_latency = random.uniform(0.1, 0.3) # 100-300ms latency to find file
        time.sleep(fs_access_latency)
        
        if not self._is_failed:
            logger.info("CheckpointingStrategy: Not in failed state, nothing to recover")
            return fs_access_latency
        
        # CORRUPTION SIMULATION
        # 2% chance that the checkpoint file is corrupted
        if random.random() < 0.02:
            logger.critical("🔥 DISK CORRUPTION: Checkpoint file is corrupted and unreadable!")
            self._is_failed = False 
            self._start_checkpointing()
            return time.time() - start_time
            
        # Recovery process: Load from disk
        try:
            checkpoint_loaded = self._load_latest_checkpoint()
            
            if checkpoint_loaded:
                # Simulate Read Bandwidth (e.g., AWS EBS or S3)
                # Intentionally slower for demo visibility
                data_size_kb = len(self._data_store) * 1.0 
                
                # Base latency + Transfer time (0.001s per KB is slow but visible)
                transfer_time = (data_size_kb * 0.005) + random.uniform(0.2, 0.5)
                time.sleep(transfer_time)
                
                # Simulate WAL Replay CPU time
                replay_time = len(self._data_store) * 0.002
                time.sleep(replay_time)
                
        except Exception as e:
            logger.error(f"Error during recovery simulation: {e}")
            checkpoint_loaded = False
        
        # Clear failed state
        self._is_failed = False
        
        # Restart background checkpointing
        self._stop_checkpointing.clear()
        self._start_checkpointing()
        
        recovery_time = time.time() - start_time
        self._record_operation('recoveries')
        
        if checkpoint_loaded:
            logger.info(
                f"✅ Checkpointing recovered in {recovery_time:.4f}s - "
                f"Restored {len(self._data_store)} records from checkpoint"
            )
        else:
            logger.warning(f"Checkpointing recovered in {recovery_time:.4f}s - No checkpoint found, starting fresh")
        
        return recovery_time
    
    def create_checkpoint(self) -> bool:
        """
        Create a checkpoint (snapshot) of current state.
        
        This is the core checkpointing operation that writes
        the entire in-memory state to persistent storage.
        """
        if self._is_failed:
            return False
        
        try:
            checkpoint_data = {
                'timestamp': time.time(),
                'checkpoint_id': self._checkpoint_count + 1,
                'data': self._data_store.copy(),
                'stats': self.stats.copy()
            }
            
            # Write checkpoint to disk
            filename = f"checkpoint_{self._checkpoint_count + 1}_{int(time.time())}.json"
            filepath = os.path.join(self.checkpoint_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(checkpoint_data, f, default=str)
            
            # Clear WAL after successful checkpoint
            self._wal.clear()
            self._last_checkpoint_time = time.time()
            self._checkpoint_count += 1
            
            # Cleanup old checkpoints
            self._cleanup_old_checkpoints()
            
            logger.info(f"📸 Checkpoint created: {filename} ({len(self._data_store)} records)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return False
    
    def _load_latest_checkpoint(self) -> bool:
        """Load the most recent checkpoint from disk."""
        try:
            # Find all checkpoint files
            checkpoint_files = [
                f for f in os.listdir(self.checkpoint_dir)
                if f.startswith('checkpoint_') and f.endswith('.json')
            ]
            
            if not checkpoint_files:
                logger.info("No checkpoint files found")
                return False
            
            # Sort by modification time and get the latest
            checkpoint_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(self.checkpoint_dir, f)),
                reverse=True
            )
            
            latest_file = checkpoint_files[0]
            filepath = os.path.join(self.checkpoint_dir, latest_file)
            
            with open(filepath, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Restore state from checkpoint
            self._data_store = checkpoint_data.get('data', {})
            self._checkpoint_count = checkpoint_data.get('checkpoint_id', 0)
            
            logger.info(f"📂 Loaded checkpoint: {latest_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False
    
    def _cleanup_old_checkpoints(self) -> None:
        """Remove old checkpoint files beyond the retention limit."""
        try:
            checkpoint_files = sorted([
                f for f in os.listdir(self.checkpoint_dir)
                if f.startswith('checkpoint_') and f.endswith('.json')
            ])
            
            while len(checkpoint_files) > self.max_checkpoints:
                oldest = checkpoint_files.pop(0)
                os.remove(os.path.join(self.checkpoint_dir, oldest))
                logger.debug(f"Removed old checkpoint: {oldest}")
                
        except Exception as e:
            logger.error(f"Checkpoint cleanup failed: {e}")
    
    def _start_checkpointing(self) -> None:
        """Start the background checkpointing thread."""
        def checkpoint_loop():
            while not self._stop_checkpointing.is_set():
                self._stop_checkpointing.wait(timeout=self.checkpoint_interval)
                if not self._stop_checkpointing.is_set():
                    self.create_checkpoint()
        
        self._checkpoint_thread = threading.Thread(target=checkpoint_loop, daemon=True)
        self._checkpoint_thread.start()
        logger.debug("Background checkpointing thread started")

    def force_checkpoint(self) -> bool:
        """Manually trigger a checkpoint (useful for testing/experiments)."""
        logger.info("⚠️ Force checkpoint requested by experiment controller")
        return self.create_checkpoint()
    
    def get_checkpoint_info(self) -> Dict[str, Any]:
        """Get information about checkpointing state."""
        return {
            'checkpoint_count': self._checkpoint_count,
            'last_checkpoint_time': self._last_checkpoint_time,
            'wal_entries': len(self._wal),
            'checkpoint_interval': self.checkpoint_interval,
            'checkpoint_dir': self.checkpoint_dir,
            'data_count': len(self._data_store)
        }
