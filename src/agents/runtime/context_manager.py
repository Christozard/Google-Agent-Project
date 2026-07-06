from typing import Dict, Any, List, Optional
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ContextManager")

class ContextManager:
    """
    Feature 3: Context Manager
    Manages the agent's context window, pruning old messages and 
    summarizing history to maintain coherence without exceeding token limits.
    """
    
    def __init__(self, max_tokens: int = 4096):
        self.max_tokens = max_tokens
        self.history: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str):
        """Adds a message to the history and manages the context window."""
        self.history.append({"role": role, "content": content})
        self._prune_context()

    def _prune_context(self):
        """
        Prunes the history if it exceeds the max_tokens limit.
        This implementation uses a simple message-count heuristic as a proxy 
        for token count, assuming an average message size.
        """
        # Heuristic: assume average message is 200 tokens. Max 4096 tokens means ~20 messages.
        estimated_tokens = len(self.history) * 200
        if estimated_tokens > self.max_tokens:
            logger.info("Context window exceeded. Pruning history...")
            # Keep the system prompt (first message) and the most recent messages
            system_prompt = self.history[0] if self.history and self.history[0]["role"] == "system" else None
            # Keep roughly half the context, prioritizing recent messages
            recent_messages_to_keep = (self.max_tokens // 2) // 200 
            recent_messages = self.history[-recent_messages_to_keep:]
            
            self.history = []
            if system_prompt:
                self.history.append(system_prompt)
            self.history.extend(recent_messages)

    def get_context(self) -> List[Dict[str, Any]]:
        """Returns the current pruned context for the LLM."""
        return self.history

    def summarize_history(self) -> str:
        """
        Summarizes the conversation history to preserve key information 
        while freeing up space. In a real LLM-driven system, this would 
        call an LLM for summarization.
        """
        if not self.history:
            return ""
        
        logger.info("Summarizing conversation history (simulated)...")
        # Simple concatenation for demonstration, to be replaced by LLM summarization.
        all_content = " ".join([m["content"] for m in self.history])
        if len(all_content) > 500: # Limit summary length
            return f"Summary: {all_content[:497]}..."
        return f"Summary: {all_content}"

if __name__ == "__main__":
    cm = ContextManager(max_tokens=1000)
    cm.add_message("system", "You are a helpful AI.")
    for i in range(10):
        cm.add_message("user", f"User message {i}. This is a relatively long message to test pruning.")
        cm.add_message("assistant", f"Assistant response {i}.")
    
    print(f"Final context size: {len(cm.get_context())} messages")
    print(f"Summarized history: {cm.summarize_history()}")
