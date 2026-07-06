import streamlit as st
import sys
import os

# Add project root to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page config MUST be at top level
st.set_page_config(
    page_title="Moomoo Investment Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_sidebar():
    """Render sidebar and return config dict."""
    # Define config constants locally to avoid import errors
    SECURITY_FIRMS = {
        "FUTUSG": "Futu SG (Singapore)",
        "FUTUSECURITIES": "Futu Securities (US)",
        "FUTUINC": "Futu Inc (US)",
    }
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 11111
    
    with st.sidebar:
        st.title("📊 Moomoo Agent")
        st.caption("AI-Powered Investment Assistant")
        
        # Initialize session state
        if "config" not in st.session_state:
            st.session_state.config = {
                "trd_env": "SIMULATE",
                "security_firm": "FUTUSG",
                "host": DEFAULT_HOST,
                "port": DEFAULT_PORT,
                "trade_password": None
            }
        
        col1, col2 = st.columns(2)
        
        with col1:
            trd_env = st.radio(
                "Trading Mode",
                options=["SIMULATE", "REAL"],
                index=0,
                key="trd_env_radio"
            )
            if trd_env == "SIMULATE":
                st.info("ℹ️ Paper trading mode")
            else:
                st.warning("⚠️ REAL trading mode")
        
        with col2:
            firm_options = list(SECURITY_FIRMS.keys())
            selected_firm = st.selectbox(
                "Security Firm",
                options=firm_options,
                index=0,
                key="security_firm_select",
                format_func=lambda x: SECURITY_FIRMS[x]
            )
            host = st.text_input("OpenD Host", value=DEFAULT_HOST, key="opend_host")
            port = st.number_input("OpenD Port", value=DEFAULT_PORT, key="opend_port")
        
        trade_password = None
        if trd_env == "REAL":
            trade_password = st.text_input("Trading Password", type="password", key="trade_password")
        
        config = {
            "trd_env": trd_env,
            "security_firm": selected_firm,
            "host": host,
            "port": int(port),
            "trade_password": trade_password
        }
        
        if st.button("Connect to OpenD"):
            try:
                from src.agents.runtime.investment_orchestrator import InvestmentOrchestrator
                
                if "orchestrator" not in st.session_state:
                    st.session_state.orchestrator = InvestmentOrchestrator()
                
                success = st.session_state.orchestrator.connect()
                if success:
                    st.success("✅ Connected!")
                    st.session_state.config = config
                    os.environ["MOOMOO_SECURITY_FIRM"] = config["security_firm"]
                else:
                    st.error("❌ Failed to connect. Is OpenD running?")
            except Exception as e:
                st.error(f"Connection error: {e}")
        
        return config


def main():
    """Main app content."""
    st.title("📈 Moomoo Investment Agent")
    
    if "orchestrator" not in st.session_state or not st.session_state.orchestrator.mcp_client.connected:
        st.warning("👈 Please configure your trading environment in the sidebar and connect to OpenD.")
        return
    
    orchestrator = st.session_state.orchestrator
    config = st.session_state.get("config", {"trd_env": "SIMULATE"})
    
    # Import components lazily
    from src.frontend.components.goal_form import render_goal_form
    from src.frontend.components.portfolio_view import render_portfolio_health
    from src.frontend.components.research_ui import render_market_research, display_research_results
    from src.frontend.components.trade_gate import render_order_form, render_trade_approval
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 Goal Planner", "💼 Portfolio Health", "🔍 Market Research",
        "⚖️ Portfolio Rebalance", "💱 Trade Execution", "📊 Market Monitoring",
        "🏛️ Investment Committee"
    ])
    
    with tab1:
        goal_data = render_goal_form()
        if goal_data:
            with st.spinner("Generating investment plan..."):
                result = orchestrator.run_goal_planner(goal_data)
                st.success("Investment Plan Generated!")
                st.write(f"**Risk Profile:** {result.get('risk_profile', 'N/A')}")
                st.write(f"**Risk Score:** {result.get('risk_score', 'N/A')}/10")
    
    with tab2:
        if st.button("Analyze Portfolio"):
            with st.spinner("Analyzing..."):
                health = orchestrator.run_portfolio_analysis(trd_env=config["trd_env"])
                render_portfolio_health(health)
    
    with tab3:
        tickers = render_market_research()
        if tickers:
            with st.spinner("Researching..."):
                result = orchestrator.run_market_research(tickers)
                display_research_results(result.get("results", []))
    
    with tab4:
        st.subheader("⚖️ Portfolio Rebalancing")
        target_input = st.text_area("Target Allocation", value="Tech: 50, Finance: 30")
        if st.button("Generate Rebalancing Plan"):
            target = {}
            for item in target_input.split(","):
                if ":" in item:
                    sector, pct = item.split(":")
                    target[sector.strip()] = float(pct.strip())
            result = orchestrator.portfolio_rebalancer.rebalance_portfolio(target, trd_env=config["trd_env"])
            st.json(result)
    
    with tab5:
        order = render_order_form()
        if order:
            approved = render_trade_approval(order, config["trd_env"])
            if approved is True:
                result = orchestrator.execute_trade(order, trd_env=config["trd_env"], user_approved=True)
                st.success(f"✅ Order placed! ID: {result.get('order_id')}") if result.get("status") == "success" else st.error(result.get("reason", result.get("status")))
            elif approved is False:
                st.info("Trade cancelled.")
    
    with tab6:
        st.subheader("📊 Market Monitoring")
        trigger_code = st.text_input("Stock to Monitor", value="US.AAPL")
        trigger_price = st.number_input("Trigger Price", value=170.0)
        trigger_condition = st.selectbox("Condition", ["BELOW_OR_EQUAL", "ABOVE_OR_EQUAL"])
        if st.button("Add Price Trigger"):
            orchestrator.market_monitoring.add_price_trigger(trigger_code, trigger_price, trigger_condition)
            st.success(f"Added trigger for {trigger_code}")
    
    with tab7:
        st.subheader("🏛️ Investment Committee")
        committee_tickers = st.text_area("Securities", value="US.AAPL, US.MSFT")
        tickers_list = [t.strip() for t in committee_tickers.split(",") if t.strip()]
        if st.button("Run Investment Committee"):
            with st.spinner("Analyzing..."):
                result = orchestrator.run_investment_committee(tickers_list)
                st.json(result)


# Main execution
try:
    render_sidebar()
    main()
except Exception as e:
    st.error(f"App error: {e}")
    import traceback
    st.code(traceback.format_exc())