from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DecisionAgent")

class DecisionAgent:
    """
    Part of Feature 7: Investment Committee - Decision Agent
    Collates arguments from Bull, Bear, and Risk Manager, computes confidence,
    and produces a final investment recommendation.
    """
    
    def make_recommendation(self, security_research: Dict[str, Any], bull_case: Optional[str], bear_case: Optional[str], risk_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collates all information and makes a final investment recommendation.
        
        Args:
            security_research: Original research data for the security.
            bull_case: Bullish argument string (or None).
            bear_case: Bearish argument string (or None).
            risk_evaluation: Result from the RiskManager.
        """
        logger.info(f"Decision Agent: Collating information for {security_research.get("code")}")

        final_recommendation = security_research.get("recommendation", "Hold")
        confidence_score = 50 # Base confidence
        rationale_points = []

        # Adjust confidence based on bull/bear cases
        if bull_case:
            confidence_score += 20
            rationale_points.append("Strong bullish sentiment identified.")
        if bear_case:
            confidence_score -= 20
            rationale_points.append("Significant bearish factors noted.")

        # Adjust confidence based on risk evaluation
        concentration_impact = risk_evaluation.get("concentration_impact")
        if concentration_impact == "High":
            confidence_score -= 25
            final_recommendation = "Hold" # Override strong buy if risk is too high
            rationale_points.append("High concentration risk identified, reducing enthusiasm.")
        elif concentration_impact == "Moderate":
            confidence_score -= 10
            rationale_points.append("Moderate concentration risk, proceed with caution.")

        downside_risks = risk_evaluation.get("downside_risks", [])
        if downside_risks:
            confidence_score -= (len(downside_risks) * 10)
            rationale_points.append(f"Downside risks noted: {', '.join(downside_risks)}.")
        
        confidence_score = max(0, min(100, confidence_score)) # Clamp between 0 and 100

        # Final recommendation logic
        if confidence_score >= 75 and final_recommendation != "Sell":
            final_recommendation = "Strong Buy"
        elif confidence_score >= 55 and final_recommendation != "Sell":
            final_recommendation = "Buy"
        elif confidence_score < 30:
            final_recommendation = "Strong Sell"
        elif confidence_score < 45:
            final_recommendation = "Sell"

        return {
            "security": security_research.get("code"),
            "final_recommendation": final_recommendation,
            "confidence_score": confidence_score,
            "rationale": ". ".join(rationale_points) or "Based on available data.",
            "detailed_research": security_research,
            "risk_summary": risk_evaluation
        }

if __name__ == "__main__":
    decision_agent = DecisionAgent()
    
    # Example data
    aapl_research = {"code": "US.AAPL", "name": "Apple Inc.", "recommendation": "Buy", "pe_ratio": 18.5, "last_price": 180.0}
    aapl_bull = "Strong growth prospects."
    aapl_bear = None
    aapl_risk = {"concentration_impact": "Low", "downside_risks": []}
    
    googl_research = {"code": "US.GOOGL", "name": "Alphabet Inc.", "recommendation": "Sell", "pe_ratio": 40.0, "last_price": 140.0}
    googl_bull = None
    googl_bear = "High P/E and market saturation."
    googl_risk = {"concentration_impact": "Moderate", "downside_risks": ["Analyst Sell rating"]}

    print("\n--- Decision Agent ---")
    print(f"AAPL Decision: {decision_agent.make_recommendation(aapl_research, aapl_bull, aapl_bear, aapl_risk)}")
    print(f"GOOGL Decision: {decision_agent.make_recommendation(googl_research, googl_bull, googl_bear, googl_risk)}")
