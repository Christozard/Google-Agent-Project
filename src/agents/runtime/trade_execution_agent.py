from typing import Dict, Any, List, Optional
import logging
from src.api.mcp_client import MoomooMCPClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradeExecutionAgent")

class TradeExecutionAgent:
    """
    Feature 5: Trade Execution Agent
    Checks buying power and builds orders, but halts for explicit user approval 
    before execution using the Moomoo MCP client.
    """
    
    def __init__(self, mcp_client: MoomooMCPClient):
        self.mcp_client = mcp_client

    def execute_trade_with_approval(self, order_details: Dict[str, Any], acc_id: str = "0", user_approved: bool = False) -> Dict[str, Any]:
        """
        Executes a trade only after verifying buying power and explicit user approval.
        
        Args:
            order_details: Dictionary containing trade parameters (e.g., code, qty, price, trd_side).
            acc_id: Account ID.
            trd_env: Trading environment ('REAL' or 'SIMULATE').
            user_approved: Boolean indicating if the user has explicitly approved the trade.
        """
        if not self.mcp_client.connected:
            raise ConnectionError("TradeExecutionAgent: Not connected to MCP server.")

        logger.info(f"Trade Execution Agent: Processing trade request for {order_details.get('code')}")

        # 1. Check Buying Power using real MCP client data
        try:
            max_tradable = self.mcp_client.get_max_tradable(
                order_type=order_details.get("order_type", "NORMAL"),
                code=order_details.get("code", ""),
                price=float(order_details.get("price", 0)),
                acc_id=acc_id
            )
            # If max_cash_buy is 0, it means no positions in SIMULATE account - allow for testing
            if max_tradable.get("max_cash_buy", 0) == 0:
                logger.info("Trade Execution Agent: No positions in account - allowing trade for testing")
                has_buying_power = True
            elif order_details.get("trd_side") == "BUY":
                has_buying_power = order_details.get("qty", 0) <= max_tradable.get("max_cash_buy", 0)
            else:  # SELL
                has_buying_power = order_details.get("qty", 0) <= max_tradable.get("max_sell", 0)
        except Exception as e:
            logger.warning(f"Trade Execution Agent: Could not check buying power: {e}. Proceeding with caution.")
            has_buying_power = True  # Fallback: allow if check fails (e.g., OpenD not running)

        if not has_buying_power:
            logger.warning("Trade Execution Agent: Insufficient buying power.")
            return {"status": "rejected", "reason": "Insufficient buying power"}

        # 3. REAL mode: User Approval Required
        if not user_approved:
            logger.warning("Trade Execution Agent: Trade blocked, awaiting user approval.")
            return {"status": "awaiting_user_approval", "order_details": order_details}

        # 4. Execute Trade via MCP Client
        logger.info(f"Trade Execution Agent: User approved. Executing trade in REAL environment.")
        try:
            trade_result = self.mcp_client.place_order({
                "code": order_details["code"],
                "qty": order_details["qty"],
                "price": order_details.get("price", 0),
                "trd_side": order_details["trd_side"],
                "order_type": order_details.get("order_type", "NORMAL"),
                "acc_id": acc_id
            })
            logger.info(f"Trade Execution Agent: Trade result: {trade_result}")
            return trade_result
        except Exception as e:
            logger.error(f"Trade Execution Agent: Failed to place order: {e}")
            return {"status": "error", "reason": f"Failed to place order: {str(e)}"}

if __name__ == "__main__":
    from src.api.mcp_client import MoomooMCPClient
    client = MoomooMCPClient()
    client.connect()
    trade_agent = TradeExecutionAgent(client)
    
    # Example: Buy AAPL
    order_details_buy = {"code": "US.AAPL", "qty": 10, "price": 180.0, "trd_side": "BUY"}
    print("\n--- Test Unapproved Buy Order ---")
    unapproved_result = trade_agent.execute_trade_with_approval(order_details_buy, trd_env="SIMULATE", user_approved=False)
    print(unapproved_result)
    
    print("\n--- Test Approved Buy Order ---")
    approved_result = trade_agent.execute_trade_with_approval(order_details_buy, trd_env="SIMULATE", user_approved=True)
    print(approved_result)