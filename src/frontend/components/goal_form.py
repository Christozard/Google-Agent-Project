import streamlit as st
from src.frontend.config import RISK_PROFILES

def render_goal_form():
    """Render the investment goal planning form."""
    st.subheader("🎯 Investment Goal Planner")
    
    with st.form(key="goal_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.slider("Your Age", 18, 80, 30)
            time_horizon = st.slider("Investment Time Horizon (years)", 1, 40, 10)
        
        with col2:
            risk_appetite = st.slider(
                "Risk Appetite",
                1, 10, 5,
                format_func=lambda x: f"{x} - {RISK_PROFILES.get(x, 'Unknown')}"
            )
            goals = st.text_area(
                "Investment Goals",
                value="Balanced growth",
                placeholder="e.g., Retirement planning, wealth building, capital preservation..."
            )
        
        submitted = st.form_submit_button("Generate Investment Plan", type="primary")
    
    if submitted:
        return {
            "age": age,
            "time_horizon": time_horizon,
            "risk_appetite": risk_appetite,
            "goals": goals
        }
    return None