from typing import Dict, Any, List
import logging
from src.api.mcp_client import MoomooMCPClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PortfolioHealthAnalyzer")

class PortfolioHealthAnalyzer:
    """
    Runtime agent that computes diversification score, sector allocation, 
    and concentration risk using real Moomoo MCP data.
    """
    
    def __init__(self, mcp_client: MoomooMCPClient):
        self.mcp_client = mcp_client

    def analyze_portfolio(self, acc_id: str = "0", trd_env: str = "REAL") -> Dict[str, Any]:
        """
        Analyzes the health of the portfolio using real data from the MCP client.
        
        Args:
            acc_id: Account ID to analyze.
            trd_env: Trading environment (\"REAL\" or \"SIMULATE\").
        """
        logger.info(f"Analyzing portfolio health for account {acc_id} in {trd_env} environment...")
        
        # 1. Fetch real data from MCP
        try:
            summary = self.mcp_client.get_account_summary(acc_id=acc_id)
        except Exception as e:
            logger.error(f"Failed to fetch account summary: {e}")
            return {"error": f"MCP Error: {str(e)}"}

        positions = summary.get("positions", [])
        assets = summary.get("assets", {})
        total_market_val = assets.get("market_val", 0)

        # For empty portfolios (SIMULATE mode with no positions), return simulated demo data
        if not positions or total_market_val == 0:
            logger.info("No positions in account - returning simulated demo data for testing")
            return {
                "diversification_score": 50.0,
                "sector_allocation": {"Tech": 40.0, "Finance": 30.0, "Healthcare": 20.0, "Energy": 10.0},
                "concentration_risk": "Low",
                "max_position_weight": 25.0,
                "total_positions": 4,
                "total_market_value": 100000.0,
                "analysis_status": "Simulated (No positions)"
            }

        # 2. Calculate Sector Allocation
        sector_allocation = {}
        
        # In a real implementation, we would fetch sector info per stock from a research tool.
        # For now, we use a more comprehensive hardcoded mapping for demonstration.
        sector_map = {
            "US.AAPL": "Tech", "US.MSFT": "Tech", "US.GOOGL": "Tech", "US.AMZN": "Tech",
            "US.JPM": "Finance", "US.BAC": "Finance", "US.GS": "Finance",
            "US.UNH": "Healthcare", "US.PFE": "Healthcare", "US.JNJ": "Healthcare",
            "US.XOM": "Energy", "US.CVX": "Energy",
            "US.TSLA": "Consumer Discretionary", "US.WMT": "Consumer Staples",
            "US.VTI": "Diversified ETF" # Example for an ETF
        }

        for pos in positions:
            code = pos.get("code", "Unknown")
            sector = sector_map.get(code, "Other")
            
            val = pos.get("market_price", 0) * pos.get("qty", 0)
            sector_allocation[sector] = sector_allocation.get(sector, 0) + val

        # Convert sector values to percentages
        sector_percentages = {
            sector: round((val / total_market_val) * 100, 2) 
            for sector, val in sector_allocation.items()
        }

        # 3. Calculate Diversification Score
        # Heuristic: Score based on number of unique positions and sector spread.
        num_positions = len(positions)
        num_sectors = len(sector_percentages)
        
        pos_score = min(50, num_positions * 5) # Up to 10 positions for max 50 points
        sec_score = min(50, num_sectors * 10) # Up to 5 sectors for max 50 points
        diversification_score = pos_score + sec_score

        # 4. Determine Concentration Risk
        # High risk if any single position is > 25% of the portfolio
        max_concentration = 0
        for pos in positions:
            pos_val = pos.get("market_price", 0) * pos.get("qty", 0)
            concentration = (pos_val / total_market_val) * 100
            max_concentration = max(max_concentration, concentration)

        concentration_risk = "Low"
        if max_concentration > 25:
            concentration_risk = "High"
        elif max_concentration > 15:
            concentration_risk = "Moderate"

        return {
            "diversification_score": diversification_score,
            "sector_allocation": sector_percentages,
            "concentration_risk": concentration_risk,
            "max_position_weight": round(max_concentration, 2),
            "total_positions": num_positions,
            "total_market_value": total_market_val,
            "analysis_status": "Complete (Real Data)"
        }

if __name__ == "__main__":
    from src.api.mcp_client import MoomooMCPClient
    client = MoomooMCPClient()
    client.connect()
    analyzer = PortfolioHealthAnalyzer(client)
    print(f"Portfolio Health: {analyzer.analyze_portfolio()}")
