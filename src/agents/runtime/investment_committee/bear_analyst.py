from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BearAnalyst")

class BearAnalyst:
    """
    Part of Feature 7: Investment Committee - Bear Analyst
    Arguments against candidate investments.
    """
    
    def analyze_for_bear_case(self, security_research: Dict[str, Any]) -> Optional[str]:
        """
        Analyzes research data to build a bearish argument for a security.
        
        Args:
            security_research: Research data for a specific security (from MarketResearchAgent).
        """
        logger.info(f"Bear Analyst: Building bear case for {security_research.get("code")}")
        
        recommendation = security_research.get("recommendation")
        pe_ratio = security_research.get("pe_ratio", 0)
        
        if recommendation == "Sell" or (recommendation == "Hold" and pe_ratio > 35):
            bear_argument = f"The Bear Analyst identifies significant risks in {security_research.get("name")}. " \
                            f"With a high P/E ratio of {pe_ratio:.2f} and a less than favorable recommendation, " \
                            f"the company may be overvalued or face headwinds. " \
                            f"Potential downside is a concern."
            return bear_argument
        
        logger.info(f"Bear Analyst: No strong bear case found for {security_research.get("code")}")
        return None

if __name__ == "__main__":
    bear_analyst = BearAnalyst()
    
    # Example research data
    aapl_research = {"code": "US.AAPL", "name": "Apple Inc.", "recommendation": "Buy", "pe_ratio": 18.5}
    googl_research = {"code": "US.GOOGL", "name": "Alphabet Inc.", "recommendation": "Sell", "pe_ratio": 40.0}
    
    print("\n--- Bear Analyst ---")
    print(f"AAPL Bear Case: {bear_analyst.analyze_for_bear_case(aapl_research)}")
    print(f"GOOGL Bear Case: {bear_analyst.analyze_for_bear_case(googl_research)}")
