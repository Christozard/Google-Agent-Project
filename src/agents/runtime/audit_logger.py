"""
Audit Logger - Feature 3 auxiliary agent.
Provides comprehensive logging of all agent activities, decisions,
and system events for compliance, debugging, and explainability.
"""
from typing import Dict, Any, List, Optional
import logging
import json
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuditLogger")


class AuditLogger:
    """
    Centralized audit logging for all agent activities.
    Writes structured, timestamped logs to disk and maintains
    an in-memory buffer for recent events.
    """

    def __init__(self, log_dir: str = "logs/audit/"):
        self.log_dir = log_dir
        self.buffer: List[Dict[str, Any]] = []
        self.buffer_max_size = 1000
        os.makedirs(self.log_dir, exist_ok=True)

    def log(self, agent: str, action: str, details: Dict[str, Any],
            level: str = "INFO", persist: bool = True) -> Dict[str, Any]:
        """
        Log an audit event.
        
        Args:
            agent: Name of the agent performing the action.
            action: Description of the action (e.g., 'order_validated', 'trade_executed').
            details: Structured data about the action.
            level: Log level (INFO, WARNING, ERROR).
            persist: If True, write to disk immediately.
            
        Returns:
            The audit entry dict with timestamp and ID.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "level": level,
            "details": details
        }

        # Add to in-memory buffer
        self.buffer.append(entry)
        if len(self.buffer) > self.buffer_max_size:
            self.buffer.pop(0)

        # Persist to disk
        if persist:
            self._write_to_disk(entry)

        # Also log to Python logger
        log_msg = f"[{agent}] {action}: {json.dumps(details, default=str)[:200]}"
        if level == "ERROR":
            logger.error(log_msg)
        elif level == "WARNING":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return entry

    def _write_to_disk(self, entry: Dict[str, Any]):
        """Write a single audit entry to a daily log file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"audit_{date_str}.jsonl")
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except IOError as e:
            logger.error(f"AuditLogger: Failed to write to {log_file}: {e}")

    def get_recent(self, count: int = 50, agent: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the most recent audit entries.
        
        Args:
            count: Number of entries to return.
            agent: Optional filter by agent name.
        """
        if agent:
            filtered = [e for e in self.buffer if e["agent"] == agent]
        else:
            filtered = list(self.buffer)
        return filtered[-count:]

    def get_by_action(self, action: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit entries filtered by action type."""
        return [e for e in self.buffer if e["action"] == action][-limit:]

    def get_by_level(self, level: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit entries filtered by severity level."""
        return [e for e in self.buffer if e["level"] == level][-limit:]

    def get_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent ERROR-level audit entries."""
        return self.get_by_level("ERROR", limit)

    def get_warnings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent WARNING-level audit entries."""
        return self.get_by_level("WARNING", limit)

    def generate_report(self, start_time: Optional[str] = None,
                        end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a summary report of audit activity.
        
        Args:
            start_time: ISO format start time filter.
            end_time: ISO format end time filter.
            
        Returns:
            Dict with counts, top agents, top actions, etc.
        """
        entries = self.buffer

        if start_time:
            entries = [e for e in entries if e["timestamp"] >= start_time]
        if end_time:
            entries = [e for e in entries if e["timestamp"] <= end_time]

        if not entries:
            return {"status": "no_data", "message": "No audit entries in the specified range."}

        # Count by agent
        agent_counts: Dict[str, int] = {}
        action_counts: Dict[str, int] = {}
        level_counts: Dict[str, int] = {"INFO": 0, "WARNING": 0, "ERROR": 0}

        for entry in entries:
            agent_counts[entry["agent"]] = agent_counts.get(entry["agent"], 0) + 1
            action_counts[entry["action"]] = action_counts.get(entry["action"], 0) + 1
            level_counts[entry["level"]] = level_counts.get(entry["level"], 0) + 1

        return {
            "status": "report_generated",
            "total_entries": len(entries),
            "agent_activity": dict(sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)),
            "action_frequency": dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "level_breakdown": level_counts,
            "time_range": {
                "start": entries[0]["timestamp"],
                "end": entries[-1]["timestamp"]
            }
        }

    def clear_buffer(self):
        """Clear the in-memory buffer (does not delete disk logs)."""
        self.buffer.clear()
        logger.info("AuditLogger: In-memory buffer cleared.")