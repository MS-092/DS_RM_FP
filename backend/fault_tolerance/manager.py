"""
Fault Tolerance Manager

This module provides a unified interface to switch between different
fault tolerance strategies at runtime. It allows the research experiment
controller to dynamically change the active strategy.

Usage:
    from fault_tolerance import FaultToleranceManager
    
    # Initialize with a specific strategy
    manager = FaultToleranceManager(strategy='checkpointing', config={
        'checkpoint_interval': 30
    })
    
    # Use for data operations
    manager.store('key', 'value')
    value = manager.retrieve('key')
    
    # Run experiment
    manager.simulate_failure()
    recovery_time = manager.recover()
    
    # Switch strategies
    manager.set_strategy('replication', {'replication_factor': 3})
"""

from typing import Any, Dict, Optional, Literal
import logging

from .base import BaseFaultToleranceStrategy
from .baseline import BaselineStrategy
from .checkpointing import CheckpointingStrategy
from .replication import ReplicationStrategy
from .hybrid import HybridStrategy

logger = logging.getLogger(__name__)

StrategyType = Literal['baseline', 'checkpointing', 'replication', 'hybrid']


class FaultToleranceManager:
    """
    Unified manager for fault tolerance strategies.
    
    Provides a single interface for:
    - Switching between strategies
    - Performing data operations
    - Running failure/recovery experiments
    - Collecting metrics
    """
    
    STRATEGY_MAP = {
        'baseline': BaselineStrategy,
        'checkpointing': CheckpointingStrategy,
        'replication': ReplicationStrategy,
        'hybrid': HybridStrategy
    }
    
    def __init__(
        self,
        strategy: StrategyType = 'baseline',
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the manager with a specific strategy.
        
        Args:
            strategy: One of 'baseline', 'checkpointing', 'replication', 'hybrid'
            config: Strategy-specific configuration
        """
        self._current_strategy_name = strategy
        self._current_strategy: BaseFaultToleranceStrategy = self._create_strategy(
            strategy, config
        )
        
        logger.info(f"FaultToleranceManager initialized with strategy: {strategy}")
    
    def _create_strategy(
        self,
        strategy_name: StrategyType,
        config: Optional[Dict[str, Any]]
    ) -> BaseFaultToleranceStrategy:
        """Create a strategy instance by name."""
        if strategy_name not in self.STRATEGY_MAP:
            raise ValueError(
                f"Unknown strategy: {strategy_name}. "
                f"Valid options: {list(self.STRATEGY_MAP.keys())}"
            )
        
        strategy_class = self.STRATEGY_MAP[strategy_name]
        return strategy_class(config)
    
    def set_strategy(
        self,
        strategy: StrategyType,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Switch to a different fault tolerance strategy.
        
        Note: This creates a new strategy instance. Any data in the
        previous strategy will not be automatically migrated.
        """
        logger.info(f"Switching strategy from {self._current_strategy_name} to {strategy}")
        
        self._current_strategy_name = strategy
        self._current_strategy = self._create_strategy(strategy, config)
    
    @property
    def strategy(self) -> BaseFaultToleranceStrategy:
        """Get the current strategy instance."""
        return self._current_strategy
    
    @property
    def strategy_name(self) -> str:
        """Get the name of the current strategy."""
        return self._current_strategy_name
    
    # Delegate data operations to the current strategy
    
    def store(self, key: str, value: Any) -> bool:
        """Store data using the current strategy."""
        return self._current_strategy.store(key, value)
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data using the current strategy."""
        return self._current_strategy.retrieve(key)
    
    def simulate_failure(self, **kwargs) -> None:
        """Simulate a failure using the current strategy."""
        self._current_strategy.simulate_failure(**kwargs)
    
    def recover(self) -> float:
        """Recover from failure and return recovery time."""
        return self._current_strategy.recover()
    
    def is_healthy(self) -> bool:
        """Check if the system is currently operational."""
        return self._current_strategy.is_healthy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from the current strategy."""
        return self._current_strategy.get_stats()
    
    # Manager-specific methods
    
    def get_available_strategies(self) -> list:
        """Return list of available strategy names."""
        return list(self.STRATEGY_MAP.keys())
    
    def run_experiment(
        self,
        data_items: int = 100,
        failure_type: str = "default",
        trigger_checkpoint: bool = False
    ) -> Dict[str, Any]:
        """
        Run a complete fault tolerance experiment.
        
        This method:
        1. Populates the store with test data (Synthetic Issues/Repos)
        2. Simulates a failure
        3. Measures recovery time
        4. Verifies data integrity
        
        Args:
            data_items: Number of test items to store
            failure_type: Type of failure to simulate
            trigger_checkpoint: Whether to force a checkpoint before failure (for testing RPO)
        
        Returns:
            Dictionary with experiment results
        """
        import time
        import random
        import json
        
        logger.info(f"Running experiment with {self._current_strategy_name} strategy")
        
        # Store test data (Synthetic Issue Tracker Data)
        logger.info(f"Storing {data_items} synthetic data items...")
        store_start = time.time()
        
        test_keys = []
        
        for i in range(data_items):
            # Generate realistic-looking Issue/Repo data
            item_type = "issue" if i % 2 == 0 else "repository"
            
            if item_type == "issue":
                key = f"issue_{i}"
                value = {
                    "type": "issue",
                    "id": i,
                    "title": f"Bug report #{i}: System crash on load",
                    "status": random.choice(["open", "closed", "in_progress"]),
                    "priority": random.choice(["high", "medium", "low"]),
                    "creator": f"user_{random.randint(1, 100)}",
                    "created_at": time.time()
                }
            else:
                key = f"repo_{i}"
                value = {
                    "type": "repository",
                    "id": i,
                    "name": f"project-alpha-{i}",
                    "owner": f"org_{random.randint(1, 10)}",
                    "stars": random.randint(0, 500),
                    "language": random.choice(["Python", "Go", "JavaScript", "Rust"]),
                    "last_updated": time.time()
                }
                
            self.store(key, value)
            test_keys.append(key)
        
        store_time = time.time() - store_start
        
        # Force checkpoint if requested (and supported)
        if trigger_checkpoint and hasattr(self._current_strategy, 'force_checkpoint'):
            logger.info("Triggering forced checkpoint for experiment data consistency...")
            self._current_strategy.force_checkpoint()
            # Brief sleep to ensure disk write completes in simulation
            time.sleep(0.1)
        
        # Simulate failure
        logger.info("Simulating failure...")
        self.simulate_failure()
        
        # Measure recovery
        logger.info("Starting recovery...")
        recovery_time = self.recover()
        
        # Verify data integrity
        logger.info("Verifying data integrity...")
        recovered_count = 0
        for key in test_keys:
            retrieved = self.retrieve(key)
            if retrieved is not None:
                recovered_count += 1
        
        data_recovery_rate = (recovered_count / data_items) * 100
        
        results = {
            'strategy': self._current_strategy_name,
            'strategy_full_name': self._current_strategy.strategy_name,
            'data_items': data_items,
            'store_time_seconds': store_time,
            'recovery_time_seconds': recovery_time,
            'items_recovered': recovered_count,
            'data_recovery_rate_percent': data_recovery_rate,
            'stats': self.get_stats()
        }
        
        logger.info(
            f"Experiment complete: recovery_time={recovery_time:.4f}s, "
            f"data_recovery={data_recovery_rate:.1f}%"
        )
        
        return results
        
        data_recovery_rate = (recovered_count / data_items) * 100
        
        results = {
            'strategy': self._current_strategy_name,
            'strategy_full_name': self._current_strategy.strategy_name,
            'data_items': data_items,
            'store_time_seconds': store_time,
            'recovery_time_seconds': recovery_time,
            'items_recovered': recovered_count,
            'data_recovery_rate_percent': data_recovery_rate,
            'stats': self.get_stats()
        }
        
        logger.info(
            f"Experiment complete: recovery_time={recovery_time:.4f}s, "
            f"data_recovery={data_recovery_rate:.1f}%"
        )
        
        return results


# Global singleton instance for easy access throughout the application
_manager_instance: Optional[FaultToleranceManager] = None


def get_manager(
    strategy: StrategyType = 'baseline',
    config: Optional[Dict[str, Any]] = None,
    force_new: bool = False
) -> FaultToleranceManager:
    """
    Get or create the global FaultToleranceManager instance.
    
    Args:
        strategy: Initial strategy if creating new instance
        config: Configuration for the strategy
        force_new: If True, always create a new instance
    
    Returns:
        The global manager instance
    """
    global _manager_instance
    
    if _manager_instance is None or force_new:
        _manager_instance = FaultToleranceManager(strategy, config)
    
    return _manager_instance
