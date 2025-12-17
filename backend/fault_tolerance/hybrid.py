"""
Hybrid Strategy - Combined Checkpointing and Replication

This strategy combines both fault tolerance techniques:
- Active replication provides immediate failover (low RTO)
- Checkpointing provides persistent recovery (data durability)

Together, they offer the best of both worlds:
- Near-zero downtime during single node failures (from replication)
- Complete data recovery even if all nodes fail (from checkpoints)

Research Context:
- Recovery Time: Near-instant for partial failures, checkpoint-based for full failures
- Data Loss: Minimal (only uncommitted transactions since last checkpoint)
- Use Case: Production-grade fault tolerance
"""

from typing import Any, Dict, Optional
import time
import os
import json
import threading
import logging

from .base import BaseFaultToleranceStrategy
from .checkpointing import CheckpointingStrategy
from .replication import ReplicationStrategy

logger = logging.getLogger(__name__)


class HybridStrategy(BaseFaultToleranceStrategy):
    """
    Hybrid fault tolerance combining checkpointing and replication.
    
    Data flow:
    1. Writes go to all replicas (synchronous)
    2. Background checkpointing persists state to disk
    3. On partial failure: failover to healthy replicas
    4. On total failure: recover from latest checkpoint, then sync
    """
    
    DEFAULT_CHECKPOINT_INTERVAL = 30  # seconds
    DEFAULT_REPLICATION_FACTOR = 3
    DEFAULT_CHECKPOINT_DIR = "/tmp/gitforge_hybrid_checkpoints"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the hybrid strategy.
        
        Config options:
            - checkpoint_interval: Seconds between checkpoints (default: 30)
            - replication_factor: Number of replicas (default: 3)
            - checkpoint_dir: Directory for checkpoint files
        """
        super().__init__(config)
        
        self.checkpoint_interval = self.config.get(
            'checkpoint_interval',
            self.DEFAULT_CHECKPOINT_INTERVAL
        )
        self.replication_factor = self.config.get(
            'replication_factor',
            self.DEFAULT_REPLICATION_FACTOR
        )
        self.checkpoint_dir = self.config.get(
            'checkpoint_dir',
            self.DEFAULT_CHECKPOINT_DIR
        )
        
        # Initialize the replication component
        self._replication = ReplicationStrategy({
            'replication_factor': self.replication_factor
        })
        
        # Checkpointing state
        self._last_checkpoint_time: Optional[float] = None
        self._checkpoint_count = 0
        self._checkpoint_thread: Optional[threading.Thread] = None
        self._stop_checkpointing = threading.Event()
        
        # Ensure checkpoint directory exists
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # Load from checkpoint if available
        self._load_from_checkpoint()
        
        # Start background checkpointing
        self._start_checkpointing()
        
        logger.info(
            f"HybridStrategy initialized: "
            f"replication_factor={self.replication_factor}, "
            f"checkpoint_interval={self.checkpoint_interval}s"
        )
    
    @property
    def strategy_name(self) -> str:
        return f"Hybrid (Replication: {self.replication_factor}, Checkpoint: {self.checkpoint_interval}s)"
    
    def store(self, key: str, value: Any) -> bool:
        """
        Store data using replication (immediate) with checkpoint backup.
        
        Data is:
        1. Synchronously written to all healthy replicas
        2. Periodically checkpointed to disk in the background
        """
        if self._is_failed:
            logger.warning("HybridStrategy: Cannot store - system is in failed state")
            return False
        
        # Use replication for the actual store
        success = self._replication.store(key, value)
        
        if success:
            self._record_operation('writes')
            logger.debug(f"Hybrid stored key: {key} (replicated + will be checkpointed)")
        
        return success
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data from healthy replicas.
        
        Reads are served from the replication layer for performance.
        """
        if self._is_failed:
            logger.warning("HybridStrategy: Cannot retrieve - system is in failed state")
            return None
        
        self._record_operation('reads')
        return self._replication.retrieve(key)
    
    def simulate_failure(self, failure_type: str = "partial") -> None:
        """
        Simulate different types of failures.
        
        Args:
            failure_type: 
                - "partial": Single node failure (replication handles it)
                - "majority": Majority of nodes fail (replication degrades)
                - "total": All nodes fail (need checkpoint recovery)
        """
        logger.critical(f"🔥 HYBRID FAILURE SIMULATED: {failure_type}")
        
        # Stop background checkpointing during failure
        self._stop_checkpointing.set()
        if self._checkpoint_thread:
            self._checkpoint_thread.join(timeout=2)
        
        if failure_type == "partial":
            # Single node failure - replication handles it
            self._replication.simulate_failure(node_count=1)
            # Hybrid system stays online
            
        elif failure_type == "majority":
            # Majority failure - system degrades
            nodes_to_fail = (self.replication_factor // 2) + 1
            self._replication.simulate_failure(node_count=nodes_to_fail)
            
        elif failure_type == "total":
            # Total failure - all replicas down
            self._replication.simulate_failure(node_count=self.replication_factor)
            self._is_failed = True
        
        self._record_operation('failures_simulated')
    
    def recover(self) -> float:
        """
        Recover from failure using the best available method.
        
        Strategy:
        1. If replicas have data: just recover failed nodes from healthy ones
        2. If all replicas empty: restore from checkpoint first, then sync
        
        Returns:
            Time taken to fully recover
        """
        start_time = time.time()
        
        # First, try to recover through replication (fast path)
        if self._replication._get_healthy_replicas():
            # Some replicas still have data - use replication recovery
            replication_recovery_time = self._replication.recover()
            logger.info(f"Hybrid: Recovered via replication in {replication_recovery_time:.4f}s")
        else:
            # All replicas empty - need checkpoint recovery (slow path)
            logger.info("Hybrid: All replicas empty, recovering from checkpoint...")
            checkpoint_loaded = self._load_from_checkpoint()
            
            if checkpoint_loaded:
                # Recover replication layer and sync data from checkpoint
                self._replication.recover()
                
                # Re-populate replicas from checkpoint data
                logger.info("Hybrid: Syncing checkpoint data to recovered replicas")
            else:
                logger.warning("Hybrid: No checkpoint available, starting fresh")
                self._replication.recover()
        
        # Clear failed state
        self._is_failed = False
        
        # Restart background checkpointing
        self._stop_checkpointing.clear()
        self._start_checkpointing()
        
        recovery_time = time.time() - start_time
        self._record_operation('recoveries')
        
        logger.info(f"✅ Hybrid recovery completed in {recovery_time:.4f}s")
        return recovery_time
    
    def create_checkpoint(self) -> bool:
        """
        Create a checkpoint from the current replicated state.
        
        Reads from a healthy replica and persists to disk.
        """
        if self._is_failed:
            return False
        
        try:
            # Get data from a healthy replica
            healthy_replicas = self._replication._get_healthy_replicas()
            if not healthy_replicas:
                logger.warning("Cannot checkpoint: no healthy replicas")
                return False
            
            source_replica = healthy_replicas[0]
            
            checkpoint_data = {
                'timestamp': time.time(),
                'checkpoint_id': self._checkpoint_count + 1,
                'data': source_replica.data.copy(),
                'replication_factor': self.replication_factor,
                'cluster_status': self._replication.get_cluster_status()
            }
            
            # Write to disk
            filename = f"hybrid_checkpoint_{self._checkpoint_count + 1}_{int(time.time())}.json"
            filepath = os.path.join(self.checkpoint_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(checkpoint_data, f, default=str)
            
            self._last_checkpoint_time = time.time()
            self._checkpoint_count += 1
            
            # Cleanup old checkpoints
            self._cleanup_old_checkpoints()
            
            logger.info(
                f"📸 Hybrid checkpoint created: {filename} "
                f"({len(source_replica.data)} records from {source_replica.node_id})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to create hybrid checkpoint: {e}")
            return False
    
    def _load_from_checkpoint(self) -> bool:
        """Load state from the latest checkpoint file."""
        try:
            checkpoint_files = [
                f for f in os.listdir(self.checkpoint_dir)
                if f.startswith('hybrid_checkpoint_') and f.endswith('.json')
            ]
            
            if not checkpoint_files:
                logger.info("No hybrid checkpoint files found")
                return False
            
            # Get latest checkpoint
            checkpoint_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(self.checkpoint_dir, f)),
                reverse=True
            )
            
            latest_file = checkpoint_files[0]
            filepath = os.path.join(self.checkpoint_dir, latest_file)
            
            with open(filepath, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Restore data to all replicas
            data = checkpoint_data.get('data', {})
            for replica in self._replication._replicas.values():
                replica.data = data.copy()
                replica.is_healthy = True
            
            self._checkpoint_count = checkpoint_data.get('checkpoint_id', 0)
            
            logger.info(f"📂 Loaded hybrid checkpoint: {latest_file} ({len(data)} records)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load hybrid checkpoint: {e}")
            return False
    
    def _cleanup_old_checkpoints(self, max_checkpoints: int = 5) -> None:
        """Remove old checkpoint files."""
        try:
            files = sorted([
                f for f in os.listdir(self.checkpoint_dir)
                if f.startswith('hybrid_checkpoint_') and f.endswith('.json')
            ])
            
            while len(files) > max_checkpoints:
                oldest = files.pop(0)
                os.remove(os.path.join(self.checkpoint_dir, oldest))
                logger.debug(f"Removed old hybrid checkpoint: {oldest}")
                
        except Exception as e:
            logger.error(f"Hybrid checkpoint cleanup failed: {e}")
    
    def _start_checkpointing(self) -> None:
        """Start background checkpointing thread."""
        def checkpoint_loop():
            while not self._stop_checkpointing.is_set():
                self._stop_checkpointing.wait(timeout=self.checkpoint_interval)
                if not self._stop_checkpointing.is_set():
                    self.create_checkpoint()
        
        self._checkpoint_thread = threading.Thread(target=checkpoint_loop, daemon=True)
        self._checkpoint_thread.start()
    
    def get_hybrid_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the hybrid system."""
        return {
            'strategy': self.strategy_name,
            'replication': self._replication.get_cluster_status(),
            'checkpointing': {
                'checkpoint_count': self._checkpoint_count,
                'last_checkpoint_time': self._last_checkpoint_time,
                'checkpoint_interval': self.checkpoint_interval,
                'checkpoint_dir': self.checkpoint_dir
            },
            'operational': not self._is_failed
        }
