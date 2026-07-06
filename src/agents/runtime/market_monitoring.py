from typing import Dict, Any, List, Optional
import logging
import time
from src.api.mcp_client import MoomooMCPClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketMonitoringAgent")

class MarketMonitoringAgent:
    """
    Feature 6: Market Monitoring
    Performs autonomous background monitoring for price and portfolio triggers.
    """
    
    def __init__(self, mcp_client: MoomooMCPClient):
        self.mcp_client = mcp_client
        self.monitoring_active = False
        self.monitored_triggers: List[Dict[str, Any]] = []

    def add_price_trigger(self, code: str, target_price: float, trigger_type: str = "ABOVE_OR_EQUAL", action_if_triggered: Optional[Dict[str, Any]] = None):
        """
        Adds a price-based monitoring trigger.
        
        Args:
            code: Stock code (e.g., "US.AAPL").
            target_price: The price that triggers the alert/action.
            trigger_type: "ABOVE_OR_EQUAL" or "BELOW_OR_EQUAL".
            action_if_triggered: Optional dictionary describing an action to take (e.g., place a trade).
        """
        self.monitored_triggers.append({
            "type": "price",
            "code": code,
            "target_price": target_price,
            "trigger_type": trigger_type,
            "action_if_triggered": action_if_triggered,
            "status": "active"
        })
        logger.info(f"Added price trigger for {code} at {target_price} ({trigger_type})")

    def start_monitoring(self, interval_seconds: int = 60, duration_seconds: int = 300):
        """
        Starts background monitoring for defined triggers for a specified duration.
        
        Args:
            interval_seconds: How often to check triggers.
            duration_seconds: How long to monitor before stopping.
        """
        if not self.mcp_client.connected:
            raise ConnectionError("MarketMonitoringAgent: Not connected to MCP server.")

        logger.info(f"Market Monitoring Agent: Starting monitoring for {duration_seconds} seconds (interval: {interval_seconds}s).")
        self.monitoring_active = True
        start_time = time.time()

        while self.monitoring_active and (time.time() - start_time < duration_seconds):
            logger.debug("Market Monitoring Agent: Checking triggers...")
            active_codes = list(set([t["code"] for t in self.monitored_triggers if t["status"] == "active" and t["type"] == "price"]))
            if active_codes:
                snapshots = self.mcp_client.get_market_snapshot(active_codes)
                for snapshot in snapshots:
                    code = snapshot.get("code")
                    current_price = snapshot.get("last_price")
                    
                    for trigger in self.monitored_triggers:
                        if trigger["type"] == "price" and trigger["code"] == code and trigger["status"] == "active":
                            triggered = False
                            if trigger["trigger_type"] == "ABOVE_OR_EQUAL" and current_price >= trigger["target_price"]:
                                triggered = True
                            elif trigger["trigger_type"] == "BELOW_OR_EQUAL" and current_price <= trigger["target_price"]:
                                triggered = True

                            if triggered:
                                logger.warning(f"Market Monitoring Agent: TRIGGER ACTIVATED for {code} at {current_price} (Target: {trigger["target_price"]})")
                                trigger["status"] = "triggered"
                                # Execute action_if_triggered in a real scenario (e.g., call TradeExecutionAgent)
                                # For now, just log the action.
                                if trigger["action_if_triggered"]:
                                    logger.info(f"Market Monitoring Agent: Executing triggered action: {trigger["action_if_triggered"]}")

            time.sleep(interval_seconds)

        self.monitoring_active = False
        logger.info("Market Monitoring Agent: Monitoring stopped.")

    def stop_monitoring(self):
        """
        Stops any active background monitoring process.
        """
        self.monitoring_active = False
        logger.info("Market Monitoring Agent: Stopping monitoring.")

if __name__ == "__main__":
    from src.api.mcp_client import MoomooMCPClient
    client = MoomooMCPClient()
    client.connect()
    monitor = MarketMonitoringAgent(client)
    
    # Add a trigger to buy if AAPL goes below 170
    monitor.add_price_trigger("US.AAPL", 170.0, "BELOW_OR_EQUAL", {"action": "buy", "qty": 5})
    # Add a trigger to sell if GOOGL goes above 150
    monitor.add_price_trigger("US.GOOGL", 150.0, "ABOVE_OR_EQUAL", {"action": "sell", "qty": 2})
    
    print("\n--- Starting Market Monitoring (will run for 10 seconds) ---")
    monitor.start_monitoring(interval_seconds=2, duration_seconds=10)
    print("--- Market Monitoring Finished ---")
