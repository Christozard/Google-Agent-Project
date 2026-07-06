from typing import Dict, Any, List, Optional
import logging
from src.agents.runtime.portfolio_analyzer import PortfolioHealthAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RiskManager")

class RiskManager:
    """
    Part of Feature 7: Investment Committee - Risk Manager
    Evaluates downside risk and portfolio impact of a potential investment.
    """
    
    def __init__(self, analyzer: PortfolioHealthAnalyzer):
        self.analyzer = analyzer

    def evaluate_investment_risk(self, security_research: Dict[str, Any], proposed_qty: int = 1, acc_id: str = "0", trd_env: str = "REAL") -> Dict[str, Any]:
        """
        Evaluates the risk of a proposed investment and its impact on the portfolio.
        
        Args:
            security_research: Research data for the security.
            proposed_qty: The quantity of the security being considered.
            acc_id: Account ID.
            trd_env: Trading environment (
        """
        logger.info(f"Risk Manager: Evaluating investment risk for {security_research.get("code")}")
        
        # 1. Get current portfolio health
        current_health = self.analyzer.analyze_health(acc_id=acc_id, trd_env=trd_env)
        current_total_market_value = current_health.get("total_market_value", 0)
        current_sector_allocation = current_health.get("sector_allocation", {})

        code = security_research.get("code")
        last_price = security_research.get("last_price", 0)
        proposed_investment_value = last_price * proposed_qty

        # 2. Assess concentration risk impact
        # This is a simplified check. A real system would need to know the sector of the new stock.
        # For now, we assume adding a new stock increases overall concentration if it's large.
        new_total_market_value = current_total_market_value + proposed_investment_value
        
        # Simulate new concentration of this stock if added
        simulated_new_concentration_percent = (proposed_investment_value / new_total_market_value) * 100

        # Check if adding this investment would make it a major concentration
        concentration_impact = "Low"
        if simulated_new_concentration_percent > 15: # Arbitrary threshold for impact
            concentration_impact = "Moderate"
        if simulated_new_concentration_percent > 25:
            concentration_impact = "High"

        # 3. Assess overall portfolio diversification impact (simplified)
        diversification_impact = "Neutral"
        if proposed_investment_value > (current_total_market_value * 0.1): # Large investment
            diversification_impact = "Potentially Negative (if undiversified sector)"

        # 4. Downside risk factors (qualitative for now)
        downside_risks = []
        if security_research.get("recommendation") == "Sell":
            downside_risks.append("Analyst 'Sell' recommendation - significant downside risk.")
        if security_research.get("pe_ratio", 0) > 50: # Example of high PE as risk
            downside_risks.append("Very high P/E ratio, indicating potential overvaluation.")

        return {
            "status": "risk_evaluated",
            "security": code,
            "proposed_investment_value": proposed_investment_value,
            "concentration_impact": concentration_impact,
            "diversification_impact": diversification_impact,
            "downside_risks": downside_risks,
            "current_portfolio_health": current_health
        }

if __name__ == "__main__":
    from src.api.mcp_client import MoomooMCPClient
    client = MoomooMCPClient()
    client.connect()
    analyzer = PortfolioHealthAnalyzer(client)
    risk_manager = RiskManager(analyzer)

    # Example research data for AAPL and a proposed quantity
    aapl_research = {"code": "US.AAPL", "name": "Apple Inc.", "recommendation": "Buy", "pe_ratio": 18.5, "last_price": 180.0}
    googl_research = {"code": "US.GOOGL", "name": "Alphabet Inc.", "recommendation": "Sell", "pe_ratio": 40.0, "last_price": 140.0}
    
    print("\n--- Risk Manager ---")
    print(f"AAPL Risk Evaluation: {risk_manager.evaluate_investment_risk(aapl_research, proposed_qty=50, trd_env="SIMULATE")}")
    print(f"GOOGL Risk Evaluation: {risk_manager.evaluate_investment_risk(googl_research, proposed_qty=10, trd_env="SIMULATE")}")
