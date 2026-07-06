from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BullAnalyst")

class BullAnalyst:
    """
    Part of Feature 7: Investment Committee - Bull Analyst
    Arguments supporting candidate investments.
    """
    
    def analyze_for_bull_case(self, security_research: Dict[str, Any]) -> Optional[str]:
        """
        Analyzes research data to build a bullish argument for a security.
        
        Args:
            security_research: Research data for a specific security (from MarketResearchAgent).
        """
        logger.info(f"Bull Analyst: Building bull case for {security_research.get("code")}")
        
        recommendation = security_research.get("recommendation")
        pe_ratio = security_research.get("pe_ratio", float("inf"))
        
        if recommendation == "Buy" or (recommendation == "Hold" and pe_ratio < 25):
            bull_argument = f"The Bull Analyst sees strong potential in {security_research.get("name")}. " \
                            f"With a P/E ratio of {pe_ratio:.2f} and a positive recommendation, " \
                            f"the company exhibits robust fundamentals and growth prospects. " \
                            f"Further upside is expected due to market conditions."
            return bull_argument
        
        logger.info(f"Bull Analyst: No strong bull case found for {security_research.get("code")}")
        return None

if __name__ == "__main__":
    bull_analyst = BullAnalyst()
    
    # Example research data
    aapl_research = {"code": "US.AAPL", "name": "Apple Inc.", "recommendation": "Buy", "pe_ratio": 18.5}
    googl_research = {"code": "US.GOOGL", "name": "Alphabet Inc.", "recommendation": "Hold", "pe_ratio": 28.0}
    
    print("\n--- Bull Analyst ---")
    print(f"AAPL Bull Case: {bull_analyst.analyze_for_bull_case(aapl_research)}")
    print(f"GOOGL Bull Case: {bull_analyst.analyze_for_bull_case(googl_research)}")
