"""
Phase 3 Orchestrator - Coordinates the implementation and execution of all 7 core features.
This script demonstrates the complete multi-agent investment system in action.
"""
import json
import logging
from src.agents.runtime.investment_orchestrator import InvestmentOrchestrator

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Phase3Orchestrator")


def demo_feature_1_goal_planner(orchestrator: InvestmentOrchestrator):
    """Feature 1: Goal Planner - Risk inference & investment objectives."""
    print("\n" + "=" * 70)
    print("FEATURE 1: GOAL PLANNER")
    print("=" * 70)

    user_data = {
        "age": 30,
        "time_horizon": 20,
        "risk_appetite": 8,
        "goals": "Retire by 55 with $2M portfolio"
    }
    result = orchestrator.run_goal_planner(user_data)
    print(f"Risk Profile: {result.get('risk_profile')}")
    print(f"Risk Score: {result.get('risk_score')}")
    print(f"Target Allocation: {result.get('target_allocation')}")
    print(f"Expected Return: {result.get('expected_return')}")
    print(f"Objectives:")
    for obj in result.get("objectives", []):
        print(f"  - {obj}")
    return result


def demo_feature_2_portfolio_analyzer(orchestrator: InvestmentOrchestrator):
    """Feature 2: Portfolio Health Analyzer - Diversification & sector allocation."""
    print("\n" + "=" * 70)
    print("FEATURE 2: PORTFOLIO HEALTH ANALYZER")
    print("=" * 70)

    result = orchestrator.run_portfolio_analysis(trd_env="SIMULATE")
    print(f"Diversification Score: {result.get('diversification_score')}/100")
    print(f"Concentration Risk: {result.get('concentration_risk')}")
    print(f"Max Position Weight: {result.get('max_position_weight')}%")
    print(f"Total Positions: {result.get('total_positions')}")
    print(f"Sector Allocation:")
    for sector, pct in result.get("sector_allocation", {}).items():
        print(f"  {sector}: {pct}%")
    return result


def demo_feature_3_market_research(orchestrator: InvestmentOrchestrator):
    """Feature 3: Market Research Agent - Security comparison & ranking."""
    print("\n" + "=" * 70)
    print("FEATURE 3: MARKET RESEARCH AGENT")
    print("=" * 70)

    codes = ["US.AAPL", "US.MSFT", "US.GOOGL", "US.TSLA", "US.JPM"]
    result = orchestrator.run_market_research(codes)
    print(f"Ranked Recommendations:")
    for i, rec in enumerate(result.get("ranked_recommendations", []), 1):
        print(f"  {i}. {rec.get('code')} - {rec.get('recommendation')} (P/E: {rec.get('pe_ratio')})")
    return result


def demo_feature_4_rebalancer(orchestrator: InvestmentOrchestrator):
    """Feature 4: Portfolio Rebalancer - Buy/sell allocations."""
    print("\n" + "=" * 70)
    print("FEATURE 4: PORTFOLIO REBALANCER")
    print("=" * 70)

    target_allocation = {"Tech": 50, "Finance": 20, "Healthcare": 15, "Energy": 10, "Other": 5}
    result = orchestrator.run_portfolio_rebalancing(target_allocation, trd_env="SIMULATE")
    print(f"Rebalancing Actions:")
    for action in result.get("rebalancing_actions", []):
        print(f"  {action.get('action')} ${action.get('amount', 0):.2f} in {action.get('sector')}")
        print(f"    Rationale: {action.get('rationale')}")
    return result


def demo_feature_5_trade_execution(orchestrator: InvestmentOrchestrator):
    """Feature 5: Trade Execution Agent - Safety & approval gate."""
    print("\n" + "=" * 70)
    print("FEATURE 5: TRADE EXECUTION AGENT")
    print("=" * 70)

    # Test 1: Without approval (should be blocked)
    print("\n--- Test 1: Trade WITHOUT user approval (should be blocked) ---")
    order = {"code": "US.AAPL", "qty": 10, "price": 180.0, "trd_side": "BUY"}
    result = orchestrator.execute_trade(order, trd_env="SIMULATE", user_approved=False)
    print(f"Status: {result.get('status')}")
    print(f"Reason: {result.get('reason', 'N/A')}")

    # Test 2: With approval (should execute)
    print("\n--- Test 2: Trade WITH user approval (should execute) ---")
    result = orchestrator.execute_trade(order, trd_env="SIMULATE", user_approved=True)
    print(f"Status: {result.get('status')}")
    print(f"Order ID: {result.get('order_id', 'N/A')}")
    return result


def demo_feature_6_market_monitoring(orchestrator: InvestmentOrchestrator):
    """Feature 6: Market Monitoring - Autonomous background monitoring."""
    print("\n" + "=" * 70)
    print("FEATURE 6: MARKET MONITORING")
    print("=" * 70)

    triggers = [
        {
            "code": "US.AAPL",
            "target_price": 170.0,
            "trigger_type": "BELOW_OR_EQUAL",
            "action_if_triggered": {"action": "alert", "message": "AAPL dropped below $170"}
        },
        {
            "code": "US.GOOGL",
            "target_price": 150.0,
            "trigger_type": "ABOVE_OR_EQUAL",
            "action_if_triggered": {"action": "alert", "message": "GOOGL rose above $150"}
        }
    ]
    orchestrator.setup_market_monitoring(triggers)
    print(f"Set up {len(triggers)} monitoring triggers")
    for t in triggers:
        print(f"  {t['code']}: {t['trigger_type']} ${t['target_price']}")

    # Run monitoring for a short demo (10 seconds)
    print("\nStarting monitoring for 10 seconds...")
    orchestrator.start_monitoring(interval_seconds=2, duration_seconds=10)
    print("Monitoring complete.")
    return {"triggers_set": len(triggers)}


def demo_feature_7_investment_committee(orchestrator: InvestmentOrchestrator):
    """Feature 7: Investment Committee - Multi-agent collaboration."""
    print("\n" + "=" * 70)
    print("FEATURE 7: INVESTMENT COMMITTEE")
    print("=" * 70)

    codes = ["US.AAPL", "US.MSFT", "US.GOOGL"]
    result = orchestrator.run_investment_committee(codes)
    print(f"Committee Decisions:")
    for decision in result.get("committee_decisions", []):
        print(f"\n  Security: {decision.get('security')}")
        print(f"  Final Recommendation: {decision.get('final_recommendation')}")
        print(f"  Confidence Score: {decision.get('confidence_score')}/100")
        print(f"  Rationale: {decision.get('rationale')}")
    return result


def demo_full_investment_cycle(orchestrator: InvestmentOrchestrator):
    """Full end-to-end investment cycle across all 7 features."""
    print("\n" + "=" * 70)
    print("FULL INVESTMENT CYCLE (All 7 Features)")
    print("=" * 70)

    user_data = {
        "age": 35,
        "time_horizon": 25,
        "risk_appetite": 7,
        "goals": "Growth portfolio for retirement"
    }
    target_allocation = {"Tech": 45, "Finance": 20, "Healthcare": 15, "Energy": 10, "Consumer Discretionary": 10}
    codes = ["US.AAPL", "US.MSFT", "US.GOOGL", "US.TSLA", "US.JPM"]

    result = orchestrator.run_full_investment_cycle(
        user_data=user_data,
        target_allocation=target_allocation,
        codes_to_research=codes,
        trd_env="SIMULATE",
        user_approved=False  # No actual trades in demo
    )

    summary = result.get("summary", {})
    print(f"\nCycle Summary:")
    print(f"  Risk Profile: {summary.get('risk_profile')}")
    print(f"  Portfolio Health Score: {summary.get('portfolio_health_score')}/100")
    print(f"  Securities Analyzed: {summary.get('securities_analyzed')}")
    print(f"  Rebalancing Actions: {summary.get('rebalancing_actions')}")
    print(f"  Monitoring Triggers: {summary.get('monitoring_triggers_set')}")
    print(f"  Execution Status: {summary.get('execution_status')}")
    return result


def main():
    print("=" * 70)
    print("PHASE 3: CORE PROJECT FEATURES - DEMO")
    print("Agentic Investment Copilot")
    print("=" * 70)

    # Initialize the orchestrator
    orchestrator = InvestmentOrchestrator()
    orchestrator.connect()
    orchestrator.set_environment("SIMULATE")

    # Run all feature demos
    demo_feature_1_goal_planner(orchestrator)
    demo_feature_2_portfolio_analyzer(orchestrator)
    demo_feature_3_market_research(orchestrator)
    demo_feature_4_rebalancer(orchestrator)
    demo_feature_5_trade_execution(orchestrator)
    demo_feature_6_market_monitoring(orchestrator)
    demo_feature_7_investment_committee(orchestrator)

    # Full end-to-end cycle
    demo_full_investment_cycle(orchestrator)

    # Show audit report
    print("\n" + "=" * 70)
    print("AUDIT REPORT")
    print("=" * 70)
    report = orchestrator.get_audit_report()
    print(f"Total Audit Entries: {report.get('total_entries')}")
    print(f"Agent Activity:")
    for agent, count in report.get("agent_activity", {}).items():
        print(f"  {agent}: {count} actions")
    print(f"Level Breakdown: {report.get('level_breakdown')}")

    print("\n" + "=" * 70)
    print("PHASE 3 DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()