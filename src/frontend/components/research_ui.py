import streamlit as st

def render_market_research():
    """Render market research input and results."""
    st.subheader("🔍 Market Research")
    
    # Input for securities to research
    tickers_input = st.text_area(
        "Stock Tickers (comma-separated)",
        value="US.AAPL, US.MSFT",
        placeholder="e.g., US.AAPL, US.GOOGL, US.MSFT"
    )
    
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
    
    if st.button("Research Securities") and tickers:
        with st.spinner("Analyzing securities..."):
            return tickers
    
    return None

def display_research_results(results: list):
    """Display research results in a card format."""
    st.subheader("Research Results")
    
    for i, result in enumerate(results):
        with st.expander(f"{result.get('code', 'Unknown')} - {result.get('recommendation', 'N/A')}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Last Price", f"${result.get('last_price', 0):.2f}")
                st.metric("P/E Ratio", f"{result.get('pe_ratio', 0):.2f}")
            with col2:
                st.metric("Volume", f"{result.get('volume', 0):,}")
                st.metric("Turnover", f"${result.get('turnover', 0):,.0f}")
            
            if result.get("recommendation"):
                rec_color = {"Buy": "🟢", "Hold": "🟡", "Sell": "🔴"}.get(result["recommendation"], "⚪")
                st.write(f"**Recommendation:** {rec_color} {result['recommendation']}")