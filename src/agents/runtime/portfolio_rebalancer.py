from typing import Dict, Any, List, Optional
import logging
import json
from src.api.mcp_client import MoomooMCPClient
from src.agents.runtime.portfolio_analyzer import PortfolioHealthAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PortfolioRebalancer")

class PortfolioRebalancer:
    """
    Feature 4: Portfolio Rebalancer
    Generates buy/sell allocations and rebalancing rationale based on target 
    allocations and current portfolio health.
    """
    
    def __init__(self, mcp_client: MoomooMCPClient, analyzer: PortfolioHealthAnalyzer):
        self.mcp_client = mcp_client
        self.analyzer = analyzer

    def rebalance_portfolio(self, target_allocation: Dict[str, float], acc_id: str = "0", trd_env: str = "REAL") -> Dict[str, Any]:
        """
        Calculates necessary buy/sell orders to bring the portfolio closer to the target allocation.
        
        Args:
            target_allocation: A dictionary of target sector/asset allocations (e.g., {"Tech": 50, "Finance": 30}).
            acc_id: Account ID.
            trd_env: Trading environment (
        """
        if not self.mcp_client.connected:
            raise ConnectionError("PortfolioRebalancer: Not connected to MCP server.")

        logger.info(f"Portfolio Rebalancer: Analyzing portfolio for rebalancing in {trd_env} account {acc_id}...")

        # Get current portfolio health
        current_health = self.analyzer.analyze_health(acc_id=acc_id, trd_env=trd_env)
        current_sector_allocation = current_health.get("sector_allocation", {})
        total_market_value = current_health.get("total_market_value", 0)
        # Use simulated market value if none in account (for testing with empty SIMULATE portfolio)
        if total_market_value == 0:
            total_market_value = 100000.0  # Simulated portfolio for testing
            logger.info("Using simulated portfolio value for rebalancing")
        current_positions = self.mcp_client.get_account_summary(acc_id=acc_id, trd_env=trd_env).get("positions", [])

        rebalancing_actions = []
        # Determine target values for each sector
        target_values = {
            sector: (percentage / 100) * total_market_value
            for sector, percentage in target_allocation.items()
        }

        # Assess each sector
        for sector, target_value in target_values.items():
            current_value = current_sector_allocation.get(sector, 0) / 100 * total_market_value
            delta = target_value - current_value

            if abs(delta) < total_market_value * 0.01: # Ignore small deviations (1% tolerance)
                logger.info(f"Sector {sector}: Within tolerance. No rebalancing needed.")
                continue

            if delta > 0: # Need to buy
                action = "BUY"
                amount = delta
                rationale = f"Underweight in {sector} by ${amount:.2f}. Need to increase exposure."
                rebalancing_actions.append({"sector": sector, "action": action, "amount": amount, "rationale": rationale})
            else: # Need to sell
                action = "SELL"
                amount = abs(delta)
                rationale = f"Overweight in {sector} by ${amount:.2f}. Need to reduce exposure."
                rebalancing_actions.append({"sector": sector, "action": action, "amount": amount, "rationale": rationale})
        
        # This is a simplified example. A real rebalancer would suggest specific stocks to buy/sell.
        # For demonstration, we just return the sector-level actions.
        
        logger.info("Portfolio Rebalancer: Generated rebalancing actions.")
        return {
            "status": "analysis_complete",
            "rebalancing_actions": rebalancing_actions,
            "current_health": current_health,
            "target_allocation": target_allocation,
            "rebalancing_status": "Pending Execution"
        }

if __name__ == "__main__":
    from src.api.mcp_client import MoomooMCPClient
    from src.agents.runtime.portfolio_analyzer import PortfolioHealthAnalyzer

    client = MoomooMCPClient()
    client.connect()
    analyzer = PortfolioHealthAnalyzer(client)
    rebalancer = PortfolioRebalancer(client, analyzer)

    # Example target allocation
    target_alloc = {"Tech": 60, "Finance": 20, "Healthcare": 10, "Other": 10}
    
    print("\n--- Rebalancing Portfolio ---")
    rebalance_plan = rebalancer.rebalance_portfolio(target_alloc, trd_env="SIMULATE")
    print(json.dumps(rebalance_plan, indent=4))
