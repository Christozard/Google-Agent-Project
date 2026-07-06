import os
from typing import List, Optional

class BaseAgent:
    """Base class for all agents in the Investment Copilot system."""
    
    def __init__(self, name: str, role: str, memory_path: str = "shared_memory"):
        self.name = name
        self.role = role
        self.memory_path = memory_path

    def log_activity(self, message: str):
        """Logs agent activity to the progress.md file."""
        with open("progress.md", "a") as f:
            f.write(f"\n- [{self.name}] {message}")

    def read_memory(self, filename: str) -> str:
        """Reads a specific shared memory file."""
        try:
            with open(filename, "r") as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: {filename} not found."

    def write_memory(self, filename: str, content: str, append: bool = False):
        """Writes or appends content to a shared memory file."""
        mode = "a" if append else "w"
        with open(filename, mode) as f:
            f.write(content)

    def execute_task(self, task_description: str):
        """Abstract method to be implemented by specialized agents."""
        raise NotImplementedError("Subclasses must implement execute_task")