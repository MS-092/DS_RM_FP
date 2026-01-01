"""
Base Strategy Interface for Fault Tolerance Techniques

Defines the abstract interface that all fault tolerance strategies must implement.
This follows the Strategy Pattern to allow runtime switching between techniques.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseFaultToleranceStrategy(ABC):
    """
    Abstract base class for all fault tolerance strategies.
    
    Each strategy must implement methods for:
    - Storing data with fault tolerance guarantees
    - Retrieving data with recovery capabilities
    - Simulating failures for research experiments
    - Recovering from simulated failures
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the strategy with optional configuration.
        
        Args:
            config: Strategy-specific configuration parameters
        """
        self.config = config or {}
        self.stats = {
            'writes': 0,
            'reads': 0,
            'failures_simulated': 0,
            'recoveries': 0,
            'last_operation': None
        }
        self._is_failed = False
        logger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return the name of this fault tolerance strategy."""
        pass
    
    @abstractmethod
    def store(self, key: str, value: Any) -> bool:
        """
        Store a key-value pair with fault tolerance guarantees.
        
        Args:
            key: Unique identifier for the data
            value: The data to store
            
        Returns:
            True if storage was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value by its key, with recovery if needed.
        
        Args:
            key: The key to look up
            
        Returns:
            The stored value, or None if not found
        """
        pass
    
    @abstractmethod
    def simulate_failure(self) -> None:
        """
        Simulate a node/component failure for research experiments.
        
        This method should put the strategy into a "failed" state
        that mimics real-world failure scenarios.
        """
        pass
    
    @abstractmethod
    def recover(self) -> float:
        """
        Recover from a simulated failure.
        
        Returns:
            The time (in seconds) taken to recover
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Return statistics about this strategy's operations."""
        return {
            **self.stats,
            'strategy': self.strategy_name,
            'is_failed': self._is_failed
        }
    
    def is_healthy(self) -> bool:
        """Check if the strategy is currently operational."""
        return not self._is_failed
    
    def _record_operation(self, operation_type: str) -> None:
        """Record an operation for statistics tracking."""
        self.stats[operation_type] = self.stats.get(operation_type, 0) + 1
        self.stats['last_operation'] = datetime.now().isoformat()
