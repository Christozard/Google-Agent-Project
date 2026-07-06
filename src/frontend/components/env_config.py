import streamlit as st
from typing import Optional

# Define defaults locally to avoid import issues
SECURITY_FIRMS = {
    "FUTUSG": "Futu SG (Singapore)",
    "FUTUSECURITIES": "Futu Securities (US)",
    "FUTUINC": "Futu Inc (US)",
    "FUTUAU": "Futu AU (Australia)",
    "FUTUJP": "Futu JP (Japan)",
    "FUTUCA": "Futu CA (Canada)",
    "FUTUMY": "Futu MY (Malaysia)",
}

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11111


def render_environment_config():
    """Render the trading environment configuration UI."""
    st.subheader("📊 Trading Environment Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Trading Environment Selection
        trd_env = st.radio(
            "Trading Mode",
            options=["SIMULATE", "REAL"],
            index=0,
            key="trd_env_radio",
            help="SIMULATE: Paper trading with virtual money. REAL: Connect to your actual trading account (requires credentials)."
        )
        
        if trd_env == "SIMULATE":
            st.info("ℹ️ You're using paper trading (SIMULATE) mode. No real money will be traded.")
        else:
            st.warning("⚠️ REAL trading mode requires trading password and will execute actual trades.")
    
    with col2:
        # Security Firm Selection
        firm_options = list(SECURITY_FIRMS.keys())
        selected_firm = st.selectbox(
            "Security Firm",
            options=firm_options,
            index=0,
            key="security_firm_select",
            format_func=lambda x: SECURITY_FIRMS[x]
        )
        
        # OpenD Connection Settings
        host = st.text_input("OpenD Host", value=DEFAULT_HOST, key="opend_host")
        port = st.number_input("OpenD Port", value=DEFAULT_PORT, min_value=1, max_value=65535, step=1, key="opend_port")
    
    # Trading Password (for REAL mode)
    trade_password = None
    if trd_env == "REAL":
        trade_password = st.text_input(
            "Trading Password",
            type="password",
            key="trade_password",
            help="Your 6-digit trading password from the Moomoo app"
        )
        if not trade_password:
            st.warning("⚠️ Trading password required for REAL account access")
    
    return {
        "trd_env": trd_env,
        "security_firm": selected_firm,
        "host": host,
        "port": int(port),
        "trade_password": trade_password
    }

def get_filled_config() -> dict:
    """Get configuration from session state if available."""
    if "config" not in st.session_state:
        st.session_state.config = {
            "trd_env": "SIMULATE",
            "security_firm": "FUTUSG",
            "host": DEFAULT_HOST,
            "port": DEFAULT_PORT,
            "trade_password": None
        }
    
    return st.session_state.config

def store_config(config: dict):
    """Store configuration in session state and set environment variables."""
    import os as _os
    st.session_state.config = config
    
    # Set environment variables for MCP client
    if config["trd_env"] == "REAL" and config.get("trade_password"):
        _os.environ["MOOMOO_TRADE_PASSWORD"] = config["trade_password"]
    _os.environ["MOOMOO_SECURITY_FIRM"] = config["security_firm"]