import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def render_portfolio_health(health_data: dict):
    """Render portfolio health analysis with charts."""
    st.subheader("💼 Portfolio Health Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Diversification Score Gauge
        diversification = health_data.get("diversification_score", 0)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=diversification,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Diversification Score"},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#1f77b4"},
                   "steps": [
                       {"range": [0, 30], "color": "#ff6b6b"},
                       {"range": [30, 70], "color": "#ffd93d"},
                       {"range": [70, 100], "color": "#6bcb77"}
                   ]}
        ))
        fig_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Total Positions
        st.metric("Total Positions", health_data.get("total_positions", 0))
        st.metric("Total Market Value", f"${health_data.get('total_market_value', 0):,.0f}")
    
    with col3:
        # Concentration Risk
        risk = health_data.get("concentration_risk", "Unknown")
        risk_color = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}.get(risk, "⚪")
        st.metric("Concentration Risk", f"{risk_color} {risk}")
    
    # Sector Allocation Pie Chart
    sector_allocation = health_data.get("sector_allocation", {})
    if sector_allocation:
        st.subheader("Sector Allocation")
        fig_pie = px.pie(
            values=list(sector_allocation.values()),
            names=list(sector_allocation.keys()),
            title="Current Sector Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)