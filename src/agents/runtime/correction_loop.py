"""
Correction Loop Agent - Feature 3 auxiliary agent.
Implements a feedback loop that detects errors/warnings from validation
and execution, then generates corrective actions to retry or adjust.
"""
from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CorrectionLoop")


class CorrectionLoop:
    """
    Detects failures in trade execution or validation and attempts
    to generate corrective actions (e.g., retry with adjusted params,
    split large orders, or escalate to user).
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_counts: Dict[str, int] = {}
        self.correction_log: List[Dict[str, Any]] = []

    def analyze_failure(self, failure_result: Dict[str, Any],
                        original_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes a failure result and proposes corrective action.
        
        Args:
            failure_result: The failed result from validation or execution.
            original_order: The original order details that failed.
            
        Returns:
            Dict with 'action' (retry, adjust, escalate, abort),
            'adjusted_order' (if applicable), and 'reasoning'.
        """
        order_key = self._order_key(original_order)
        current_retries = self.retry_counts.get(order_key, 0)
        errors = failure_result.get("errors", [failure_result.get("reason", "Unknown error")])
        errors_str = " ".join(errors)

        logger.info(f"CorrectionLoop: Analyzing failure for {order_key} (retry #{current_retries})")

        correction = {
            "order_key": order_key,
            "retry_count": current_retries,
            "original_order": original_order,
            "failure_reason": errors_str
        }

        # If max retries exceeded, escalate
        if current_retries >= self.max_retries:
            correction["action"] = "escalate"
            correction["reasoning"] = f"Max retries ({self.max_retries}) exceeded for {order_key}. Escalating to user."
            self.correction_log.append(correction)
            logger.warning(f"CorrectionLoop: Escalating {order_key} after {current_retries} retries.")
            return correction

        # Analyze specific error types
        if "exceeds max allowed" in errors_str:
            # Split the order into smaller chunks
            adjusted = self._split_order(original_order)
            if adjusted:
                self.retry_counts[order_key] = current_retries + 1
                correction["action"] = "adjust"
                correction["adjusted_order"] = adjusted
                correction["reasoning"] = f"Order exceeded limits. Splitting into smaller orders."
                self.correction_log.append(correction)
                return correction

        if "Insufficient buying power" in errors_str:
            # Try reducing quantity proportionally
            adjusted = self._reduce_order_to_fit(original_order, failure_result)
            if adjusted:
                self.retry_counts[order_key] = current_retries + 1
                correction["action"] = "adjust"
                correction["adjusted_order"] = adjusted
                correction["reasoning"] = f"Insufficient buying power. Reducing order quantity."
                self.correction_log.append(correction)
                return correction

        if "Cannot sell" in errors_str:
            # Adjust sell quantity to match held position
            adjusted = self._adjust_sell_qty(original_order, errors_str)
            if adjusted:
                self.retry_counts[order_key] = current_retries + 1
                correction["action"] = "adjust"
                correction["adjusted_order"] = adjusted
                correction["reasoning"] = f"Sell qty exceeds holdings. Adjusting to max available."
                self.correction_log.append(correction)
                return correction

        # Generic retry
        if current_retries < self.max_retries:
            self.retry_counts[order_key] = current_retries + 1
            correction["action"] = "retry"
            correction["adjusted_order"] = original_order
            correction["reasoning"] = f"Generic failure. Retrying (attempt {current_retries + 1}/{self.max_retries})."
            self.correction_log.append(correction)
            return correction

        # Default: escalate
        correction["action"] = "escalate"
        correction["reasoning"] = f"Unable to resolve automatically. Escalating."
        self.correction_log.append(correction)
        return correction

    def _order_key(self, order: Dict[str, Any]) -> str:
        """Generate a unique key for an order."""
        return f"{order.get('code', 'Unknown')}_{order.get('trd_side', 'UNKNOWN')}_{order.get('qty', 0)}"

    def _split_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Split a large order into a smaller chunk (half the original qty)."""
        qty = order.get("qty", 0)
        new_qty = max(1, qty // 2)
        adjusted = dict(order)
        adjusted["qty"] = new_qty
        adjusted["_correction_note"] = f"Split from {qty} to {new_qty}"
        return adjusted

    def _reduce_order_to_fit(self, order: Dict[str, Any],
                              failure_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Reduce order quantity to fit within available buying power."""
        qty = order.get("qty", 0)
        price = order.get("price", 1)
        new_qty = max(1, qty // 2)
        adjusted = dict(order)
        adjusted["qty"] = new_qty
        adjusted["_correction_note"] = f"Reduced from {qty} to {new_qty} for buying power"
        return adjusted

    def _adjust_sell_qty(self, order: Dict[str, Any],
                          errors_str: str) -> Optional[Dict[str, Any]]:
        """Adjust sell quantity to match available position."""
        # Extract available qty from error message
        import re
        match = re.search(r'only (\d+) held', errors_str)
        if match:
            available_qty = int(match.group(1))
            adjusted = dict(order)
            adjusted["qty"] = available_qty
            adjusted["_correction_note"] = f"Adjusted sell qty to {available_qty}"
            return adjusted
        return None

    def reset_retries(self, order_key: str):
        """Reset retry count for a given order."""
        self.retry_counts.pop(order_key, None)

    def get_correction_log(self) -> List[Dict[str, Any]]:
        """Returns the full correction history."""
        return self.correction_log

    def clear_correction_log(self):
        """Clears the correction log."""
        self.correction_log = []
        self.retry_counts.clear()
        logger.info("CorrectionLoop: Correction log cleared.")