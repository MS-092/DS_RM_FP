import threading
import time

CHECKPOINT_INTERVAL = 15  # seconds


class CombinedCheckpointReplicationManager:
    def __init__(self, replication_mgr, checkpoint_mgr):
        self.replication_mgr = replication_mgr
        self.checkpoint_mgr = checkpoint_mgr
        self.lock = threading.Lock()

    def on_state_change(self, state):
        """
        Called whenever application state changes.
        """
        with self.lock:
            # Respect replication window
            self.replication_mgr.record_state_change(state)

            # Opportunistic checkpoint
            self.checkpoint_mgr.save_checkpoint()

    def recover(self):
        """
        Recovery order:
        1. Use replica state if available (external trigger)
        2. Fallback to local checkpoint
        """
        state = self.checkpoint_mgr.load_checkpoint()
        return state

    def start_periodic_checkpointing(self):
        """
        Ensure durability even if replication window not reached.
        """
        def loop():
            while True:
                with self.lock:
                    self.checkpoint_mgr.save_checkpoint()
                time.sleep(CHECKPOINT_INTERVAL)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
