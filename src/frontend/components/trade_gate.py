import streamlit as st

def render_trade_approval(order_details: dict, trd_env: str):
    """Render trade approval gate for safety."""
    st.subheader("⚠️ Trade Approval Required")
    
    # Display trade details
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Stock", order_details.get("code", "Unknown"))
        with col2:
            st.metric("Quantity", order_details.get("qty", 0))
        with col3:
            st.metric("Price", f"${order_details.get('price', 0):.2f}")
        
        st.write(f"**Side:** {order_details.get('trd_side', 'BUY')}")
        st.write(f"**Environment:** {trd_env}")
        
        if trd_env == "REAL":
            st.error("🚨 WARNING: This is a REAL trade that will execute with actual money!")
    
    # Approval buttons
    col1, col2 = st.columns(2)
    with col1:
        approve = st.button("✅ Approve Trade", type="primary", use_container_width=True)
    with col2:
        deny = st.button("❌ Deny Trade", use_container_width=True)
    
    if approve:
        return True
    elif deny:
        return False
    
    return None

def render_order_form():
    """Render order input form."""
    st.subheader("📝 Place Order")
    
    with st.form("order_form"):
        code = st.text_input("Stock Code", value="US.AAPL", help="Format: US.TICKER")
        qty = st.number_input("Quantity", value=10, min_value=1, step=1)
        price = st.number_input("Price", value=180.0, min_value=0.1, step=0.1)
        trd_side = st.selectbox("Side", options=["BUY", "SELL"])
        
        submitted = st.form_submit_button("Review Order")
    
    if submitted:
        return {
            "code": code,
            "qty": int(qty),
            "price": float(price),
            "trd_side": trd_side
        }
    return None