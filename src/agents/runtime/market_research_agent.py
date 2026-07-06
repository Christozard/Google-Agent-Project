from typing import Dict, Any, List, Optional
import logging
from src.api.mcp_client import MoomooMCPClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketResearchAgent")

class MarketResearchAgent:
    """
    Feature 3: Market Research Agent
    Compares candidate securities, pulls metrics (valuation, momentum, earnings),
    and ranks recommendations using real market data from the MCP client.
    """
    
    def __init__(self, mcp_client: MoomooMCPClient):
        self.mcp_client = mcp_client

    def research_securities(self, codes: List[str], include_news: bool = True) -> List[Dict[str, Any]]:
        """
        Conducts research on a list of securities and returns detailed metrics.
        
        Args:
            codes: A list of stock codes (e.g., ["US.AAPL", "US.MSFT"]).
            include_news: Whether to fetch news articles for each security.
            include_ma: Whether to calculate moving averages.
        """
        if not self.mcp_client.connected:
            raise ConnectionError("MarketResearchAgent: Not connected to MCP server.")

        logger.info(f"Market Research Agent: Researching securities: {codes}")
        all_snapshots = self.mcp_client.get_market_snapshot(codes)
        
        researched_data = []
        for snapshot in all_snapshots:
            code = snapshot.get("code")
            # Calculate momentum (price change from open)
            last_price = snapshot.get("last_price", 0)
            open_price = snapshot.get("open_price", 0)
            momentum = ((last_price - open_price) / open_price * 100) if open_price > 0 else 0
            
            # Simple scoring for recommendation based on P/E and P/B
            pe_ratio = snapshot.get("pe_ratio", 0)
            pb_ratio = snapshot.get("pb_ratio", 0)
            
            recommendation = "Hold"
            if pe_ratio > 0 and pe_ratio < 20 and pb_ratio > 0 and pb_ratio < 5:
                recommendation = "Buy" # Simplified logic
            elif pe_ratio > 50 or pb_ratio > 10:
                recommendation = "Sell" # Simplified logic

            # Fetch news
            news_items = []
            if include_news:
                try:
                    # Extract ticker symbol for news search
                    ticker = code.replace("US.", "").replace("HK.", "")
                    news_items = self.mcp_client.get_news(ticker, max_count=5)
                    # Fetch summaries for each news item
                    for news in news_items:
                        summary = self.mcp_client.fetch_news_summary(news.get("url", ""))
                        news["summary"] = summary
                except Exception as e:
                    logger.warning(f"Could not fetch news for {code}: {e}")

            researched_data.append({
                "code": code,
                "name": snapshot.get("name"),
                "last_price": last_price,
                "open_price": open_price,
                "high_price": snapshot.get("high_price"),
                "low_price": snapshot.get("low_price"),
                "prev_close_price": snapshot.get("prev_close_price"),
                "pe_ratio": pe_ratio,
                "pb_ratio": pb_ratio,
                "volume": snapshot.get("volume"),
                "turnover": snapshot.get("turnover"),
                "momentum": round(momentum, 2),
                "news": news_items,
                "recommendation": recommendation,
                "analysis_status": "Complete (Real Market Data)"
            })
        
        logger.info(f"Market Research Agent: Completed research for {len(codes)} securities.")
        return researched_data

    def rank_recommendations(self, research_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks securities based on their research results (e.g., recommendation, P/E).
        """
        logger.info("Market Research Agent: Ranking recommendations...")
        # Simple ranking: 'Buy' > 'Hold' > 'Sell', then by lower P/E for Buys
        def sort_key(item):
            rec_priority = {"Buy": 3, "Hold": 2, "Sell": 1}.get(item.get("recommendation"), 0)
            pe = item.get("pe_ratio", float("inf"))
            return (-rec_priority, pe) # Sort by priority (desc), then PE (asc)

        ranked_results = sorted(research_results, key=sort_key)
        logger.info("Market Research Agent: Recommendations ranked.")
        return ranked_results

if __name__ == "__main__":
    from src.api.mcp_client import MoomooMCPClient
    client = MoomooMCPClient()
    client.connect()
    research_agent = MarketResearchAgent(client)
    
    # Example usage
    codes_to_research = ["US.AAPL", "US.MSFT", "US.GOOGL"]
    results = research_agent.research_securities(codes_to_research)
    ranked_results = research_agent.rank_recommendations(results)
    
    print("\n--- Ranked Market Research Results ---")
    for res in ranked_results:
        print(f"Code: {res["code"]}, Recommendation: {res["recommendation"]}, P/E: {res["pe_ratio"]}")
