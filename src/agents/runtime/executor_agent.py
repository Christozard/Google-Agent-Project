"""
Executor Agent - Feature 3 auxiliary agent.
Responsible for executing rebalancing plans and trade sequences
after receiving user approval. Wraps TradeExecutionAgent for
multi-step execution workflows.
"""
from typing import Dict, Any, List, Optional
import logging
from src.agents.runtime.trade_execution_agent import TradeExecutionAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExecutorAgent")


class ExecutorAgent:
    """
    Executes approved trade sequences and rebalancing plans.
    Ensures orders are submitted in the correct order (sells before buys)
    and tracks execution status.
    """

    def __init__(self, trade_execution_agent: TradeExecutionAgent):
        self.trade_execution_agent = trade_execution_agent
        self.execution_log: List[Dict[str, Any]] = []

    def execute_rebalancing_plan(self, rebalancing_actions: List[Dict[str, Any]],
                                 acc_id: str = "0", trd_env: str = "SIMULATE",
                                 user_approved: bool = False) -> Dict[str, Any]:
        """
        Executes a full rebalancing plan (multiple buy/sell actions).
        
        Strategy: Execute SELL orders first to free up capital, then BUY orders.
        
        Args:
            rebalancing_actions: List of actions from PortfolioRebalancer.
            acc_id: Account ID.
            trd_env: Trading environment.
            user_approved: Global user approval flag.
        """
        if not user_approved:
            logger.warning("ExecutorAgent: Rebalancing blocked - user approval required.")
            return {"status": "blocked", "reason": "User approval required for rebalancing"}

        if not rebalancing_actions:
            return {"status": "noop", "message": "No rebalancing actions to execute."}

        logger.info(f"ExecutorAgent: Executing rebalancing plan with {len(rebalancing_actions)} actions.")

        # Separate sells and buys: execute sells first
        sell_actions = [a for a in rebalancing_actions if a.get("action") == "SELL"]
        buy_actions = [a for a in rebalancing_actions if a.get("action") == "BUY"]

        results = []
        all_success = True

        for action_group, group_name in [(sell_actions, "SELL"), (buy_actions, "BUY")]:
            for action in action_group:
                # Convert sector-level action to an order detail
                order_detail = {
                    "code": action.get("code", "US.AAPL"),
                    "qty": int(action.get("amount", 0) / 100),  # Simplified qty conversion
                    "price": action.get("price", 0),
                    "trd_side": group_name,
                    "order_type": "NORMAL",
                    "trd_env": trd_env,
                    "acc_id": acc_id,
                    "rationale": action.get("rationale", "")
                }
                trade_result = self.trade_execution_agent.execute_trade_with_approval(
                    order_details=order_detail,
                    acc_id=acc_id,
                    trd_env=trd_env,
                    user_approved=user_approved
                )
                results.append({
                    "action": group_name,
                    "sector": action.get("sector", "Unknown"),
                    "order_detail": order_detail,
                    "result": trade_result
                })
                if trade_result.get("status") not in ("success", "awaiting_user_approval"):
                    all_success = False
                    logger.error(f"ExecutorAgent: {group_name} for {action.get('sector')} failed: {trade_result}")

        self.execution_log.extend(results)
        logger.info(f"ExecutorAgent: Rebalancing plan execution {'succeeded' if all_success else 'had failures'}.")
        return {
            "status": "executed" if all_success else "partial_failure",
            "execution_results": results,
            "total_actions": len(rebalancing_actions),
            "successful": sum(1 for r in results if r["result"].get("status") in ("success", "awaiting_user_approval")),
            "failed": sum(1 for r in results if r["result"].get("status") not in ("success", "awaiting_user_approval"))
        }

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Returns the full execution history."""
        return self.execution_log

    def clear_execution_log(self):
        """Clears the execution log."""
        self.execution_log = []
        logger.info("ExecutorAgent: Execution log cleared.")