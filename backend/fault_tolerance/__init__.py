"""
Fault Tolerance Module for Distributed Systems Research

This module provides explicit implementations of fault tolerance techniques:
- Baseline: No fault tolerance (control group)
- Checkpointing: Periodic state snapshots to persistent storage
- Replication: Active data replication across virtual nodes
- Hybrid: Combined checkpointing and replication

Each technique is implemented as a separate class following the Strategy pattern,
allowing researchers to switch between them for comparative experiments.
"""

from .baseline import BaselineStrategy
from .checkpointing import CheckpointingStrategy
from .replication import ReplicationStrategy
from .hybrid import HybridStrategy
from .manager import FaultToleranceManager, get_manager

__all__ = [
    'BaselineStrategy',
    'CheckpointingStrategy', 
    'ReplicationStrategy',
    'HybridStrategy',
    'FaultToleranceManager',
    'get_manager'
]
