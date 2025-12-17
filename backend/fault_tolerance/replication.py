"""
Replication Strategy - Active Data Replication

This strategy implements fault tolerance through data replication:
- Data is stored across multiple virtual "nodes" (in-memory replicas)
- Writes are synchronously replicated to all nodes
- Reads can be served from any replica
- On node failure, remaining replicas continue serving requests

Research Context:
- Recovery Time: Near-instant (failover to healthy replica)
- Data Loss on Failure: None (unless all replicas fail)
- Configurable Parameter: Replication factor (2, 3, 5)
- Trade-off: Higher factor = more redundancy but higher write latency
"""

from typing import Any, Dict, Optional, List, Set
import time
import random
import logging
from dataclasses import dataclass
from datetime import datetime

from .base import BaseFaultToleranceStrategy

logger = logging.getLogger(__name__)


@dataclass
class ReplicaNode:
    """Represents a single replica node in the replication cluster."""
    node_id: str
    is_healthy: bool
    data: Dict[str, Any]
    last_heartbeat: float
    write_count: int = 0
    read_count: int = 0


class ReplicationStrategy(BaseFaultToleranceStrategy):
    """
    Fault tolerance through active data replication.
    
    Implements synchronous replication across multiple virtual nodes.
    Uses a simple quorum-based approach for consistency.
    """
    
    DEFAULT_REPLICATION_FACTOR = 3
    HEARTBEAT_INTERVAL = 5.0  # seconds
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the replication strategy.
        
        Config options:
            - replication_factor: Number of replicas to maintain (default: 3)
            - write_quorum: Minimum replicas for successful write (default: majority)
            - read_quorum: Minimum replicas for successful read (default: 1)
        """
        super().__init__(config)
        
        self.replication_factor = self.config.get(
            'replication_factor',
            self.DEFAULT_REPLICATION_FACTOR
        )
        
        # Quorum settings
        self.write_quorum = self.config.get(
            'write_quorum',
            (self.replication_factor // 2) + 1  # Majority
        )
        self.read_quorum = self.config.get('read_quorum', 1)
        
        # Initialize replica nodes
        self._replicas: Dict[str, ReplicaNode] = {}
        self._initialize_replicas()
        
        # Track which nodes are currently "failed"
        self._failed_nodes: Set[str] = set()
        
        logger.info(
            f"ReplicationStrategy initialized: factor={self.replication_factor}, "
            f"write_quorum={self.write_quorum}, read_quorum={self.read_quorum}"
        )
    
    @property
    def strategy_name(self) -> str:
        return f"Replication (Factor: {self.replication_factor})"
    
    def _initialize_replicas(self) -> None:
        """Create the initial set of replica nodes."""
        for i in range(self.replication_factor):
            node_id = f"node-{i+1}"
            self._replicas[node_id] = ReplicaNode(
                node_id=node_id,
                is_healthy=True,
                data={},
                last_heartbeat=time.time()
            )
            logger.debug(f"Initialized replica: {node_id}")
    
    def _get_healthy_replicas(self) -> List[ReplicaNode]:
        """Return list of currently healthy replica nodes."""
        return [r for r in self._replicas.values() if r.is_healthy]
    
    def store(self, key: str, value: Any) -> bool:
        """
        Store data with synchronous replication to all healthy nodes.
        
        A write is considered successful if it reaches the write quorum.
        """
        if self._is_failed:
            logger.warning("ReplicationStrategy: Cannot store - entire cluster is failed")
            return False
        
        healthy_replicas = self._get_healthy_replicas()
        
        if len(healthy_replicas) < self.write_quorum:
            logger.error(
                f"Cannot write: only {len(healthy_replicas)} healthy replicas, "
                f"need {self.write_quorum} for quorum"
            )
            return False
        
        timestamp = time.time()
        entry = {
            'value': value,
            'timestamp': timestamp,
            'version': int(timestamp * 1000)  # Version for conflict resolution
        }
        
        # Synchronously replicate to all healthy nodes
        successful_writes = 0
        for replica in healthy_replicas:
            try:
                replica.data[key] = entry.copy()
                replica.write_count += 1
                successful_writes += 1
                logger.debug(f"Replicated key '{key}' to {replica.node_id}")
            except Exception as e:
                logger.error(f"Failed to replicate to {replica.node_id}: {e}")
        
        if successful_writes >= self.write_quorum:
            self._record_operation('writes')
            logger.debug(
                f"Write successful: key='{key}', replicated to {successful_writes}/{len(healthy_replicas)} nodes"
            )
            return True
        else:
            logger.error(
                f"Write failed: only {successful_writes} successful, needed {self.write_quorum}"
            )
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data from the healthiest available replica.
        
        Reads from any single healthy replica (read quorum = 1 by default).
        In production, this could implement read-repair or quorum reads.
        """
        if self._is_failed:
            logger.warning("ReplicationStrategy: Cannot retrieve - entire cluster is failed")
            return None
        
        healthy_replicas = self._get_healthy_replicas()
        
        if len(healthy_replicas) < self.read_quorum:
            logger.error(
                f"Cannot read: only {len(healthy_replicas)} healthy replicas, "
                f"need {self.read_quorum} for quorum"
            )
            return None
        
        # Read from a random healthy replica (load balancing)
        replica = random.choice(healthy_replicas)
        replica.read_count += 1
        
        self._record_operation('reads')
        entry = replica.data.get(key)
        
        if entry:
            logger.debug(f"Read key '{key}' from {replica.node_id}")
            return entry['value']
        
        return None
    
    def simulate_failure(self, node_count: int = 1) -> None:
        """
        Simulate failure of one or more replica nodes.
        
        Args:
            node_count: Number of nodes to fail (default: 1)
        
        Unlike baseline, the system continues operating as long as
        enough healthy replicas remain.
        """
        healthy_replicas = self._get_healthy_replicas()
        
        if node_count >= len(healthy_replicas):
            # All nodes failed - entire system goes down
            logger.critical(f"🔥 REPLICATION FAILURE: All {len(healthy_replicas)} nodes failed!")
            for replica in healthy_replicas:
                replica.is_healthy = False
                self._failed_nodes.add(replica.node_id)
            self._is_failed = True
        else:
            # Partial failure - system continues with remaining nodes
            nodes_to_fail = random.sample(healthy_replicas, node_count)
            for replica in nodes_to_fail:
                replica.is_healthy = False
                self._failed_nodes.add(replica.node_id)
                logger.warning(f"🔥 Replica {replica.node_id} FAILED - system continues with remaining nodes")
        
        self._record_operation('failures_simulated')
        
        remaining = len(self._get_healthy_replicas())
        logger.info(
            f"Replication failure simulated: {node_count} node(s) failed, "
            f"{remaining} healthy replica(s) remaining"
        )
    
    def recover(self) -> float:
        """
        Recover failed nodes and resync their data.
        
        In replication strategy, recovery involves:
        1. Bringing failed nodes back online
        2. Syncing data from healthy replicas to recovered nodes
        
        REALISM UPDATE: Includes simulated network latency and
        potential for cascading failure during high-load recovery.
        
        Returns:
            Time taken to recover (sync data to recovered nodes)
        """
        start_time = time.time()
        
        # Simulate Network Latency for node discovery (10-50ms)
        discovery_latency = random.uniform(0.010, 0.050)
        time.sleep(discovery_latency)
        
        if not self._failed_nodes:
            logger.info("ReplicationStrategy: No failed nodes to recover")
            return discovery_latency
        
        # Get a healthy replica to sync from
        healthy_replicas = self._get_healthy_replicas()
        
        if not healthy_replicas:
            # All nodes were down - need to recover from nothing (data loss)
            logger.warning("All replicas were down - recovering with empty state")
            for node_id in list(self._failed_nodes):
                replica = self._replicas[node_id]
                replica.is_healthy = True
                replica.data = {}
                self._failed_nodes.discard(node_id)
        else:
            # Sync from healthy replica
            source_replica = healthy_replicas[0]
            data_size = len(source_replica.data)
            
            # CASCADING FAILURE SIMULATION
            # 5% chance that the healthy node fails under load of syncing multiple failed nodes
            if len(self._failed_nodes) >= 2 and random.random() < 0.05:
                logger.critical(f"🔥 CASCADING FAILURE: Node {source_replica.node_id} crashed during sync load!")
                source_replica.is_healthy = False
                self._failed_nodes.add(source_replica.node_id)
                # Abort recovery for now
                return time.time() - start_time
            
            for node_id in list(self._failed_nodes):
                replica = self._replicas[node_id]
                
                # Simulate Data Transfer Latency
                # 0.5ms per item + 20ms base overhead
                transfer_latency = 0.020 + (data_size * 0.0005)
                time.sleep(transfer_latency)
                
                # Copy data from healthy source (simulating sync)
                replica.data = source_replica.data.copy()
                replica.is_healthy = True
                replica.last_heartbeat = time.time()
                
                self._failed_nodes.discard(node_id)
                logger.info(
                    f"✅ Recovered {node_id}: synced {len(replica.data)} records from {source_replica.node_id}"
                )
        
        # Clear global failed state if all nodes are now healthy
        self._is_failed = len(self._get_healthy_replicas()) == 0
        
        recovery_time = time.time() - start_time
        self._record_operation('recoveries')
        
        logger.info(f"Replication recovery completed in {recovery_time:.4f}s")
        return recovery_time
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get detailed status of the replication cluster."""
        healthy_nodes = self._get_healthy_replicas()
        
        return {
            'replication_factor': self.replication_factor,
            'healthy_nodes': len(healthy_nodes),
            'failed_nodes': list(self._failed_nodes),
            'write_quorum': self.write_quorum,
            'read_quorum': self.read_quorum,
            'can_accept_writes': len(healthy_nodes) >= self.write_quorum,
            'can_accept_reads': len(healthy_nodes) >= self.read_quorum,
            'nodes': {
                node_id: {
                    'healthy': replica.is_healthy,
                    'data_count': len(replica.data),
                    'write_count': replica.write_count,
                    'read_count': replica.read_count
                }
                for node_id, replica in self._replicas.items()
            }
        }
    
    def get_data_count(self) -> int:
        """Return the number of unique keys across replicas."""
        healthy = self._get_healthy_replicas()
        if not healthy:
            return 0
        return len(healthy[0].data)
