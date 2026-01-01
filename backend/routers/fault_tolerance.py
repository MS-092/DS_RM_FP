"""
Fault Tolerance API Router

Exposes the fault tolerance strategies via REST API for:
- The frontend Research Control Panel
- The automated experiment controller
- Manual testing and demonstration
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, Literal
import logging

from fault_tolerance import FaultToleranceManager, get_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fault-tolerance", tags=["fault-tolerance"])


# Request/Response Models

class StrategyConfig(BaseModel):
    """Configuration for a fault tolerance strategy."""
    strategy: Literal['baseline', 'checkpointing', 'replication', 'hybrid']
    checkpoint_interval: Optional[int] = 30
    replication_factor: Optional[int] = 3


class StoreRequest(BaseModel):
    """Request to store data."""
    key: str
    value: Any


class ExperimentRequest(BaseModel):
    """Request to run an experiment."""
    strategy: Literal['baseline', 'checkpointing', 'replication', 'hybrid']
    data_items: int = 100
    checkpoint_interval: Optional[int] = 30
    replication_factor: Optional[int] = 3
    trigger_checkpoint: Optional[bool] = False


# ... (existing code) ...

@router.post("/run-experiment")
async def run_experiment(request: ExperimentRequest) -> Dict[str, Any]:
    """
    Run a complete fault tolerance experiment.
    
    This will:
    1. Configure the specified strategy
    2. Store test data
    3. Simulate a failure
    4. Measure recovery time
    5. Verify data integrity
    
    Returns:
        Complete experiment results including all metrics
    """
    # Create a fresh manager with the specified strategy
    config = {}
    if request.checkpoint_interval:
        config['checkpoint_interval'] = request.checkpoint_interval
    if request.replication_factor:
        config['replication_factor'] = request.replication_factor
    
    manager = get_manager(
        strategy=request.strategy,
        config=config,
        force_new=True  # Always create fresh for experiments
    )
    
    # Run the experiment
    results = manager.run_experiment(
        data_items=request.data_items,
        trigger_checkpoint=request.trigger_checkpoint
    )
    
    return results


class FailureRequest(BaseModel):
    """Request to simulate a failure."""
    failure_type: Optional[str] = "default"
    node_count: Optional[int] = 1  # For replication strategy


# Endpoints

@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get the current status of the fault tolerance system.
    
    Returns:
        Current strategy, health status, and statistics
    """
    manager = get_manager()
    
    return {
        "strategy": manager.strategy_name,
        "strategy_details": manager.strategy.strategy_name,
        "is_healthy": manager.is_healthy(),
        "stats": manager.get_stats()
    }


@router.get("/strategies")
async def list_strategies() -> Dict[str, Any]:
    """
    List all available fault tolerance strategies.
    
    Returns:
        List of strategy names and their descriptions
    """
    return {
        "strategies": [
            {
                "name": "baseline",
                "description": "No fault tolerance - data lost on failure (control group)"
            },
            {
                "name": "checkpointing",
                "description": "Periodic snapshots to disk - recovers from last checkpoint"
            },
            {
                "name": "replication",
                "description": "Active data replication - instant failover to healthy replicas"
            },
            {
                "name": "hybrid",
                "description": "Combined checkpointing + replication - best of both worlds"
            }
        ]
    }


@router.post("/configure")
async def configure_strategy(config: StrategyConfig) -> Dict[str, Any]:
    """
    Configure and switch to a specific fault tolerance strategy.
    
    This will create a new strategy instance with the specified configuration.
    """
    manager = get_manager()
    
    strategy_config = {}
    
    if config.checkpoint_interval:
        strategy_config['checkpoint_interval'] = config.checkpoint_interval
    
    if config.replication_factor:
        strategy_config['replication_factor'] = config.replication_factor
    
    manager.set_strategy(config.strategy, strategy_config)
    
    logger.info(f"Strategy configured: {config.strategy} with config: {strategy_config}")
    
    return {
        "success": True,
        "message": f"Switched to {config.strategy} strategy",
        "current_strategy": manager.strategy.strategy_name
    }


@router.post("/store")
async def store_data(request: StoreRequest) -> Dict[str, Any]:
    """
    Store a key-value pair using the current fault tolerance strategy.
    """
    manager = get_manager()
    
    success = manager.store(request.key, request.value)
    
    return {
        "success": success,
        "key": request.key,
        "strategy": manager.strategy_name
    }


@router.get("/retrieve/{key}")
async def retrieve_data(key: str) -> Dict[str, Any]:
    """
    Retrieve a value by key using the current fault tolerance strategy.
    """
    manager = get_manager()
    
    value = manager.retrieve(key)
    
    return {
        "key": key,
        "value": value,
        "found": value is not None,
        "strategy": manager.strategy_name
    }


@router.post("/simulate-failure")
async def simulate_failure(request: FailureRequest = None) -> Dict[str, Any]:
    """
    Simulate a failure for research experiments.
    
    The behavior depends on the current strategy:
    - Baseline: Clears all data
    - Checkpointing: Clears memory (disk preserved)
    - Replication: Fails specified number of nodes
    - Hybrid: Varies based on failure_type (partial/majority/total)
    """
    manager = get_manager()
    
    if not request:
        request = FailureRequest()
    
    # Different strategies accept different failure parameters
    try:
        if manager.strategy_name == 'replication':
            manager.simulate_failure(node_count=request.node_count)
        elif manager.strategy_name == 'hybrid':
            manager.simulate_failure(failure_type=request.failure_type)
        else:
            manager.simulate_failure()
    except Exception as e:
        logger.error(f"Failure simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "success": True,
        "message": f"Failure simulated on {manager.strategy_name} strategy",
        "is_healthy": manager.is_healthy()
    }


@router.post("/recover")
async def recover_from_failure() -> Dict[str, Any]:
    """
    Recover from a simulated failure.
    
    Returns:
        Recovery time in seconds and post-recovery status
    """
    manager = get_manager()
    
    recovery_time = manager.recover()
    
    return {
        "success": True,
        "recovery_time_seconds": recovery_time,
        "is_healthy": manager.is_healthy(),
        "strategy": manager.strategy_name
    }





@router.get("/experiment-presets")
async def get_experiment_presets() -> Dict[str, Any]:
    """
    Get predefined experiment configurations for the research study.
    
    These presets match the research design document.
    """
    return {
        "presets": [
            {
                "name": "Baseline Control",
                "strategy": "baseline",
                "data_items": 100,
                "description": "No fault tolerance - measures worst-case scenario"
            },
            {
                "name": "Checkpointing 15s",
                "strategy": "checkpointing",
                "checkpoint_interval": 15,
                "data_items": 100,
                "description": "Frequent checkpoints - less data loss, higher overhead"
            },
            {
                "name": "Checkpointing 30s",
                "strategy": "checkpointing",
                "checkpoint_interval": 30,
                "data_items": 100,
                "description": "Standard checkpoint interval"
            },
            {
                "name": "Checkpointing 60s",
                "strategy": "checkpointing",
                "checkpoint_interval": 60,
                "data_items": 100,
                "description": "Infrequent checkpoints - more data loss, lower overhead"
            },
            {
                "name": "Replication Factor 2",
                "strategy": "replication",
                "replication_factor": 2,
                "data_items": 100,
                "description": "Minimal replication - single node failure tolerance"
            },
            {
                "name": "Replication Factor 3",
                "strategy": "replication",
                "replication_factor": 3,
                "data_items": 100,
                "description": "Standard replication - majority quorum"
            },
            {
                "name": "Replication Factor 5",
                "strategy": "replication",
                "replication_factor": 5,
                "data_items": 100,
                "description": "High replication - tolerates 2 node failures"
            },
            {
                "name": "Hybrid Standard",
                "strategy": "hybrid",
                "checkpoint_interval": 30,
                "replication_factor": 3,
                "data_items": 100,
                "description": "Combined approach - best RTO and durability"
            }
        ]
    }
