import pickle
import os
import threading
import time

CHECKPOINT_DIR = "/tmp/checkpoints"
CHECKPOINT_INTERVAL = 10  # seconds


class CheckpointManager:
    def __init__(self, state_provider):
        """
        state_provider: function that returns application state
        """
        self.state_provider = state_provider
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    def save_checkpoint(self):
        state = self.state_provider()
        filename = f"{CHECKPOINT_DIR}/checkpoint.pkl"

        with open(filename, "wb") as f:
            pickle.dump(state, f)

    def load_checkpoint(self):
        filename = f"{CHECKPOINT_DIR}/checkpoint.pkl"
        if not os.path.exists(filename):
            return None

        with open(filename, "rb") as f:
            return pickle.load(f)

    def start_periodic_checkpointing(self):
        def loop():
            while True:
                self.save_checkpoint()
                time.sleep(CHECKPOINT_INTERVAL)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
