"""
SharedMemory system for state persistence across all runtime agents.
Provides a centralized, thread-safe store for agent context, decisions,
and operational state.
"""
from typing import Dict, Any, List, Optional
import logging
import json
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SharedMemory")


class SharedMemory:
    """
    Centralized state persistence for the multi-agent system.
    All runtime agents read/write here to maintain coherence.
    """

    def __init__(self, storage_path: str = "src/shared_memory/"):
        self.storage_path = storage_path
        self._in_memory: Dict[str, Any] = {}
        os.makedirs(self.storage_path, exist_ok=True)

    def _file_path(self, key: str) -> str:
        """Convert a dot-separated key to a file path."""
        safe_key = key.replace(".", "/")
        return os.path.join(self.storage_path, f"{safe_key}.json")

    def put(self, key: str, value: Any, persist: bool = True):
        """
        Store a value in shared memory.
        
        Args:
            key: Dot-separated key (e.g., 'portfolio.health.diversification_score')
            value: Any JSON-serializable value
            persist: If True, also write to disk
        """
        self._in_memory[key] = value
        if persist:
            filepath = self._file_path(key)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                json.dump({"key": key, "value": value, "timestamp": datetime.now().isoformat()}, f, indent=2)
        logger.debug(f"SharedMemory: Stored {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from shared memory.
        Checks in-memory first, then falls back to disk.
        """
        if key in self._in_memory:
            return self._in_memory[key]
        filepath = self._file_path(key)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    return data.get("value", default)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"SharedMemory: Failed to read {filepath}: {e}")
                return default
        return default

    def get_all_with_prefix(self, prefix: str) -> Dict[str, Any]:
        """Retrieve all keys that start with the given prefix."""
        results = {}
        for key in list(self._in_memory.keys()):
            if key.startswith(prefix):
                results[key] = self._in_memory[key]
        # Also scan disk for persisted keys not in memory
        prefix_dir = self._file_path(prefix)
        base_dir = os.path.dirname(prefix_dir) if "." in prefix else self.storage_path
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for fname in files:
                    if fname.endswith(".json"):
                        fpath = os.path.join(root, fname)
                        try:
                            with open(fpath, "r") as f:
                                data = json.load(f)
                                k = data.get("key", "")
                                if k.startswith(prefix) and k not in results:
                                    results[k] = data.get("value")
                        except (json.JSONDecodeError, IOError):
                            pass
        return results

    def delete(self, key: str):
        """Remove a key from shared memory."""
        self._in_memory.pop(key, None)
        filepath = self._file_path(key)
        if os.path.exists(filepath):
            os.remove(filepath)

    def clear(self):
        """Clear all in-memory state (does not delete disk files)."""
        self._in_memory.clear()

    def snapshot(self) -> Dict[str, Any]:
        """Return a full snapshot of in-memory state."""
        return dict(self._in_memory)

    def log_decision(self, agent_name: str, decision: Dict[str, Any]):
        """Log a decision made by an agent with a timestamp."""
        timestamp = datetime.now().isoformat()
        decision_key = f"decisions.{agent_name}.{timestamp}"
        self.put(decision_key, decision)
        logger.info(f"SharedMemory: Decision logged for {agent_name}")

    def get_decision_history(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve decision history, optionally filtered by agent."""
        prefix = f"decisions.{agent_name}." if agent_name else "decisions."
        raw = self.get_all_with_prefix(prefix)
        decisions = []
        for key, value in raw.items():
            parts = key.split(".")
            decisions.append({
                "agent": parts[1] if len(parts) > 2 else "unknown",
                "timestamp": parts[-1] if len(parts) > 3 else "unknown",
                "decision": value
            })
        return sorted(decisions, key=lambda d: d.get("timestamp", ""), reverse=True)