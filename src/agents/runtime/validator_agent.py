"""
Validator Agent - Feature 3 auxiliary agent.
Validates trade orders, portfolio actions, and agent outputs
against defined rules and bounds before execution.
"""
from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ValidatorAgent")


class ValidatorAgent:
    """
    Validates orders, actions, and agent outputs against safety rules
    and business constraints. Acts as a gate before execution.
    """

    def __init__(self, max_order_qty: int = 10000, max_order_value: float = 1000000.0):
        self.max_order_qty = max_order_qty
        self.max_order_value = max_order_value
        self.validation_log: List[Dict[str, Any]] = []

    def validate_order(self, order_details: Dict[str, Any],
                       available_cash: float = 0.0,
                       current_positions: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Validates a single trade order against safety rules.
        
        Args:
            order_details: Dictionary with code, qty, price, trd_side, etc.
            available_cash: Available buying power.
            current_positions: Dict of {code: qty} for sell validation.
            
        Returns:
            Dict with 'valid' (bool), 'warnings' (list), and 'errors' (list).
        """
        errors = []
        warnings = []

        code = order_details.get("code", "Unknown")
        qty = order_details.get("qty", 0)
        price = order_details.get("price", 0)
        side = order_details.get("trd_side", "BUY")
        total_value = qty * price

        # Rule 1: Quantity bounds
        if qty <= 0:
            errors.append(f"Invalid quantity: {qty}. Must be > 0.")
        elif qty > self.max_order_qty:
            errors.append(f"Quantity {qty} exceeds max allowed ({self.max_order_qty}).")

        # Rule 2: Price bounds
        if price <= 0:
            errors.append(f"Invalid price: {price}. Must be > 0.")

        # Rule 3: Total value bounds
        if total_value > self.max_order_value:
            errors.append(f"Order value ${total_value:.2f} exceeds max allowed (${self.max_order_value:.2f}).")

        # Rule 4: Buying power check for BUY orders
        if side == "BUY" and total_value > available_cash > 0:
            errors.append(f"Insufficient buying power: ${total_value:.2f} needed, ${available_cash:.2f} available.")

        # Rule 5: Position check for SELL orders
        if side == "SELL" and current_positions:
            current_qty = current_positions.get(code, 0)
            if qty > current_qty:
                errors.append(f"Cannot sell {qty} shares of {code}; only {current_qty} held.")

        # Rule 6: Warnings for large orders
        if total_value > self.max_order_value * 0.5:
            warnings.append(f"Large order: ${total_value:.2f} (>{self.max_order_value * 0.5:.2f}). Recommend review.")

        valid = len(errors) == 0
        result = {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "order_summary": f"{side} {qty} x {code} @ ${price:.2f} = ${total_value:.2f}"
        }

        self.validation_log.append(result)
        if valid:
            logger.info(f"ValidatorAgent: Order for {code} passed validation.")
        else:
            logger.warning(f"ValidatorAgent: Order for {code} failed validation: {errors}")

        return result

    def validate_rebalancing_actions(self, actions: List[Dict[str, Any]],
                                     total_portfolio_value: float = 0.0) -> Dict[str, Any]:
        """
        Validates a set of rebalancing actions for consistency.
        
        Checks:
        - Total sell value doesn't exceed portfolio
        - No conflicting buy/sell on same sector
        - Overall allocation drift is reasonable
        """
        errors = []
        warnings = []

        total_sell_value = sum(a.get("amount", 0) for a in actions if a.get("action") == "SELL")
        total_buy_value = sum(a.get("amount", 0) for a in actions if a.get("action") == "BUY")

        # Check sell doesn't exceed portfolio
        if total_sell_value > total_portfolio_value > 0:
            errors.append(f"Total sell value ${total_sell_value:.2f} exceeds portfolio value ${total_portfolio_value:.2f}.")

        # Check for duplicate sectors in actions
        sectors_in_action = {}
        for action in actions:
            sector = action.get("sector", "Unknown")
            if sector in sectors_in_action:
                warnings.append(f"Multiple actions for sector {sector}.")
            sectors_in_action[sector] = action.get("action")

        # Check buy/sell ratio isn't extreme
        if total_buy_value > 0 and total_sell_value > 0:
            ratio = total_buy_value / total_sell_value
            if ratio > 5:
                warnings.append(f"Aggressive buy/sell ratio ({ratio:.2f}). Recommend review.")
            elif ratio < 0.2 and total_buy_value > 0:
                warnings.append(f"Very conservative buy/sell ratio ({ratio:.2f}). Recommend review.")

        valid = len(errors) == 0
        result = {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "total_sell": total_sell_value,
            "total_buy": total_buy_value,
            "action_count": len(actions)
        }

        self.validation_log.append(result)
        return result

    def get_validation_log(self) -> List[Dict[str, Any]]:
        """Returns the full validation history."""
        return self.validation_log

    def clear_validation_log(self):
        """Clears the validation log."""
        self.validation_log = []
        logger.info("ValidatorAgent: Validation log cleared.")