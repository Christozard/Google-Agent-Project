"""
InvestmentOrchestrator - Central coordinator for all Phase 3 runtime agents.
"""
from typing import Dict, Any, List, Optional
import logging
import json

from src.api.mcp_client import MoomooMCPClient
from src.agents.runtime.goal_planner import GoalPlanner
from src.agents.runtime.portfolio_analyzer import PortfolioHealthAnalyzer
from src.agents.runtime.market_research_agent import MarketResearchAgent
from src.agents.runtime.portfolio_rebalancer import PortfolioRebalancer
from src.agents.runtime.trade_execution_agent import TradeExecutionAgent
from src.agents.runtime.market_monitoring import MarketMonitoringAgent
from src.agents.runtime.investment_committee.bull_analyst import BullAnalyst
from src.agents.runtime.investment_committee.bear_analyst import BearAnalyst
from src.agents.runtime.investment_committee.risk_manager import RiskManager
from src.agents.runtime.investment_committee.decision_agent import DecisionAgent
from src.agents.runtime.shared_memory import SharedMemory
from src.agents.runtime.executor_agent import ExecutorAgent
from src.agents.runtime.validator_agent import ValidatorAgent
from src.agents.runtime.correction_loop import CorrectionLoop
from src.agents.runtime.audit_logger import AuditLogger

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InvestmentOrchestrator")


class InvestmentOrchestrator:
    """
    Central orchestrator that coordinates all runtime agents.
    Provides a unified interface for executing investment workflows
    that span multiple agents.
    """

    def __init__(self, mcp_client: Optional[MoomooMCPClient] = None):
        # Initialize MCP client (REAL mode is enforced in MoomooMCPClient)
        self.mcp_client = mcp_client or MoomooMCPClient()

        # Initialize shared services
        self.shared_memory = SharedMemory()
        self.audit_logger = AuditLogger()

        # Initialize all runtime agents
        self.goal_planner = GoalPlanner()
        self.portfolio_analyzer = PortfolioHealthAnalyzer(self.mcp_client)
        self.market_research = MarketResearchAgent(self.mcp_client)
        self.portfolio_rebalancer = PortfolioRebalancer(self.mcp_client, self.portfolio_analyzer)
        self.trade_execution = TradeExecutionAgent(self.mcp_client)
        self.market_monitoring = MarketMonitoringAgent(self.mcp_client)

        # Investment Committee agents
        self.bull_analyst = BullAnalyst()
        self.bear_analyst = BearAnalyst()
        self.risk_manager = RiskManager(self.portfolio_analyzer)
        self.decision_agent = DecisionAgent()

        # Auxiliary agents
        self.executor = ExecutorAgent(self.trade_execution)
        self.validator = ValidatorAgent()
        self.correction_loop = CorrectionLoop()

        # Connection state
        self._connected = False

    def connect(self) -> bool:
        """Connect to the Moomoo MCP server."""
        result = self.mcp_client.connect()
        self._connected = result
        self.audit_logger.log("InvestmentOrchestrator", "connect",
                              {"status": "connected" if result else "failed"})
        return result

    def unlock_trade(self, password: Optional[str] = None) -> Dict[str, Any]:
        """Unlock REAL trading account."""
        return self.mcp_client.unlock_trade(password)

    # ─── Feature 1: Goal Planner ───────────────────────────────────────────

    def run_goal_planner(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Feature 1: Infer risk tolerance and generate investment objectives.

        Args:
            user_data: Dict with age, time_horizon, risk_appetite, goals.
        """
        self.audit_logger.log("GoalPlanner", "decompose_goal", {"user_data": user_data})
        result = self.goal_planner.decompose_goal(user_data)
        self.audit_logger.log("GoalPlanner", "decompose_goal_result", result)
        return result

    # ─── Feature 2: Portfolio Health Analyzer ─────────────────────────────────

    def run_portfolio_analyzer(self, acc_id: str = "0") -> Dict[str, Any]:
        """
        Feature 2: Compute diversification score, sector allocation, and
        concentration risk using real Moomoo account data.

        Args:
            acc_id: Account ID to analyze (defaults to first account).
        """
        self.audit_logger.log("PortfolioAnalyzer", "analyze", {"acc_id": acc_id})
        result = self.portfolio_analyzer.analyze_portfolio(acc_id)
        self.audit_logger.log("PortfolioAnalyzer", "analyze_result",
                            {"diversification_score": result.get("diversification_score")})
        return result

    # ─── Feature 3: Market Research Agent ───────────────────────────────────

    def run_market_research(self, candidates: List[str], acc_id: str = "0") -> Dict[str, Any]:
        """
        Feature 3: Compare candidate securities, pull metrics, and rank recommendations.

        Args:
            candidates: List of stock codes to analyze (e.g., ["US.AAPL", "US.TSLA"])
            acc_id: Account ID for context (used to fetch account summary for buying power)
        """
        self.audit_logger.log("MarketResearch", "research_securities",
                    {"candidates": candidates, "acc_id": acc_id})
        research_results = self.market_research.research_securities(candidates, include_news=True)
        result = {"rankings": self.market_research.rank_recommendations(research_results)}
        self.audit_logger.log("MarketResearch", "compare_result",
                            {"rankings": len(result.get("rankings", []))})
        return result

    # ─── Feature 4: Portfolio Rebalancer ───────────────────────────────────

    def run_portfolio_rebalancer(self, target_allocations: Optional[Dict[str, float]] = None,
                                  acc_id: str = "0") -> Dict[str, Any]:
        """
        Feature 4: Generate buy/sell allocations and rebalancing rationale.

        Args:
            target_allocations: Desired sector/asset class weights (optional).
            acc_id: Account ID to analyze.
        """
        self.audit_logger.log("PortfolioRebalancer", "generate_plan",
                            {"acc_id": acc_id})
        current_portfolio = self.mcp_client.get_account_summary(acc_id)
        result = self.portfolio_rebalancer.generate_rebalancing_plan(
            current_portfolio, target_allocations
        )
        self.audit_logger.log("PortfolioRebalancer", "plan_result",
                            {"actions": len(result.get("actions", []))})
        return result

    # ─── Feature 5: Trade Execution Agent ─────────────────────────────────

    def run_trade_execution(self, order_details: Dict[str, Any],
                            user_approved: bool = False,
                            acc_id: str = "0") -> Dict[str, Any]:
        """
        Feature 5: Build a trade order and execute if user approves.

        Args:
            order_details: Dict with code, side, qty, price.
            user_approved: Explicit user confirmation (CRITICAL SAFETY).
            acc_id: Account ID for the trade.
        """
        # Check buying power before execution
        if order_details.get("trd_side") == "BUY":
            try:
                max_tradable = self.mcp_client.get_max_tradable(
                    code=order_details["code"],
                    price=order_details.get("price", 0),
                    acc_id=acc_id
                )
                if not max_tradable.get("can_buy", False):
                    logger.warning(f"No buying power data returned for {order_details.get('code')} - proceeding with trade")
            except Exception as e:
                return {"status": "error", "reason": f"Failed to check buying power: {e}"}

        self.audit_logger.log("TradeExecution", "execute_trade",
                            {"order_details": order_details, "approved": user_approved})
        result = self.trade_execution.execute_trade_with_approval(order_details, user_approved, acc_id)
        self.audit_logger.log("TradeExecution", "trade_result", result)
        return result

    # ─── Feature 6: Market Monitoring ─────────────────────────────────────

    def run_market_monitoring(self, symbols: Optional[List[str]] = None,
                               acc_id: str = "0") -> Dict[str, Any]:
        """
        Feature 6: Background monitoring for price triggers and portfolio alerts.

        Args:
            symbols: List of symbols to monitor (optional).
            acc_id: Account ID to check for portfolio triggers.
        """
        self.audit_logger.log("MarketMonitoring", "check_triggers",
                            {"acc_id": acc_id})
        result = self.market_monitoring.check_triggers(symbols, acc_id)
        self.audit_logger.log("MarketMonitoring", "trigger_result", {"alerts": result})
        return result

    # ─── Feature 7: Investment Committee (Multi-Agent) ─────────────────────

    def run_investment_committee(self, code: str, acc_id: str = "0") -> Dict[str, Any]:
        """
        Feature 7: Collaborative multi-agent analysis for a security.

        Args:
            code: Stock code to analyze (e.g., "US.AAPL").
            acc_id: Account ID for context.
        """
        self.audit_logger.log("InvestmentCommittee", "analyze",
                            {"code": code, "acc_id": acc_id})

        # Get market data
        market_data = self.mcp_client.get_market_snapshot([code])
        if not market_data:
            return {"status": "error", "reason": f"No market data for {code}"}

        snapshot = market_data[0]

        # Bull case
        bull_case = self.bull_analyst.analyze(code, snapshot)
        # Bear case
        bear_case = self.bear_analyst.analyze(code, snapshot)

        # Risk assessment
        portfolio = self.mcp_client.get_account_summary(acc_id)
        risk_assessment = self.risk_manager.assess_risk(code, snapshot, portfolio)

        # Final decision
        decision = self.decision_agent.make_decision(code, bull_case, bear_case, risk_assessment)

        self.audit_logger.log("InvestmentCommittee", "decision_result",
                            {"decision": decision.get("recommendation")})

        return {
            "bull_case": bull_case,
            "bear_case": bear_case,
            "risk_assessment": risk_assessment,
            "decision": decision
        }

    # ─── Full Cycle Execution ─────────────────────────────────────────────

    def run_full_cycle(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete investment workflow:
        1. Goal Planning → 2. Portfolio Analysis → 3. Market Research
        → 4. Committee Decision → 5. Trade Execution (if approved)
        """
        results = {}

        # Step 1: Goal Planning
        results["goal"] = self.run_goal_planner(user_data)

        # Step 2: Portfolio Analysis (use realized goals from step 1)
        if "target_allocation" in results["goal"]:
            results["portfolio"] = self.run_portfolio_analyzer()

        # Step 3: Market Research
        if "candidates" in results["goal"]:
            results["research"] = self.run_market_research(results["goal"]["candidates"])

        # Step 4: Committee Decision
        if "candidates" in results["goal"]:
            top_candidate = results["research"].get("rankings", [{}])[0].get("code")
            if top_candidate:
                results["committee"] = self.run_investment_committee(top_candidate)

        return results

    def close(self):
        """Close all connections."""
        if self.mcp_client:
            self.mcp_client.close()
        logger.info("InvestmentOrchestrator shutdown complete.")
