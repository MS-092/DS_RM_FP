"""
Baseline Strategy - No Fault Tolerance (Control Group)

This strategy implements a simple in-memory data store with NO fault tolerance.
When a failure is simulated, ALL data is lost and must be rebuilt manually.

This serves as the control group for research experiments, representing a 
system without any fault tolerance mechanisms.

Research Context:
- Expected Recovery Time: Manual intervention required (infinite or very long)
- Data Loss on Failure: 100% of in-memory data
- Use Case: Baseline comparison for measuring effectiveness of other techniques
"""

from typing import Any, Dict, Optional
import time
import logging

from .base import BaseFaultToleranceStrategy

logger = logging.getLogger(__name__)


class BaselineStrategy(BaseFaultToleranceStrategy):
    """
    Baseline fault tolerance strategy with NO redundancy.
    
    Data is stored only in memory with no persistence or replication.
    A simulated failure results in complete data loss.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the baseline strategy.
        
        Config options:
            - None required (this is the simplest strategy)
        """
        super().__init__(config)
        self._data_store: Dict[str, Any] = {}
        logger.info("BaselineStrategy initialized - NO FAULT TOLERANCE ACTIVE")
    
    @property
    def strategy_name(self) -> str:
        return "Baseline (No Fault Tolerance)"
    
    def store(self, key: str, value: Any) -> bool:
        """
        Store data in memory only.
        
        WARNING: Data will be lost on failure simulation.
        """
        if self._is_failed:
            logger.warning("BaselineStrategy: Cannot store - system is in failed state")
            return False
        
        self._data_store[key] = {
            'value': value,
            'timestamp': time.time()
        }
        self._record_operation('writes')
        logger.debug(f"Baseline stored key: {key}")
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data from memory.
        
        Returns None if system is failed or key doesn't exist.
        """
        if self._is_failed:
            logger.warning("BaselineStrategy: Cannot retrieve - system is in failed state")
            return None
        
        self._record_operation('reads')
        entry = self._data_store.get(key)
        return entry['value'] if entry else None
    
    def simulate_failure(self) -> None:
        """
        Simulate a catastrophic failure.
        
        In baseline mode, this DESTROYS ALL DATA to simulate
        a node crash without any backup mechanisms.
        """
        logger.critical("🔥 BASELINE FAILURE SIMULATED - ALL DATA LOST!")
        
        # Record how much data was lost
        data_lost_count = len(self._data_store)
        
        # Complete data loss - this is the key characteristic of baseline
        self._data_store.clear()
        
        self._is_failed = True
        self._record_operation('failures_simulated')
        
        logger.info(f"Baseline failure: {data_lost_count} records permanently lost")
    
    def recover(self) -> float:
        """
        Attempt recovery from failure.
        
        In baseline mode, recovery simply clears the failed state.
        Data cannot be recovered - it's permanently lost.
        
        Returns:
            Time taken to "recover" (just state reset, no data recovery)
        """
        start_time = time.time()
        
        if not self._is_failed:
            logger.info("BaselineStrategy: Not in failed state, nothing to recover")
            return 0.0
        
        # "Recovery" for baseline just means the system is back online
        # But all previous data is gone forever
        self._is_failed = False
        self._data_store = {}  # Fresh start with empty store
        
        recovery_time = time.time() - start_time
        self._record_operation('recoveries')
        
        logger.warning(f"Baseline recovered in {recovery_time:.4f}s - DATA NOT RESTORED (none available)")
        
        return recovery_time
    
    def get_data_count(self) -> int:
        """Return the number of items currently stored."""
        return len(self._data_store)
    
    def list_keys(self) -> list:
        """Return all keys in the data store."""
        return list(self._data_store.keys())
