import requests
import threading

REPLICATION_WINDOW = 3

class WindowedReplicationManager:
    def __init__(self, peers):
        """
        peers: list of backend replica base URLs
        """
        self.peers = peers
        self.buffer = []
        self.lock = threading.Lock()

    def record_state_change(self, state):
        """
        Call this on every state change.
        """
        with self.lock:
            self.buffer.append(state.copy())

            if len(self.buffer) >= REPLICATION_WINDOW:
                self._replicate_buffer()
                self.buffer.clear()

    def _replicate_buffer(self):
        """
        Replicate the latest state to peers.
        """
        latest_state = self.buffer[-1]

        for peer in self.peers:
            try:
                requests.post(
                    f"{peer}/internal/replicate",
                    json=latest_state,
                    timeout=1
                )
            except Exception:
                pass  # tolerate replica failure
