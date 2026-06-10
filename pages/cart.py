import streamlit as st

if not st.session_state.get("logged_in"):
    st.error("Please Login First")
    st.stop()

st.set_page_config(page_title="Shopping Cart", page_icon="🛒", layout="wide")

st.markdown(
    """
<style>
.stApp { background-color: #0B1120 !important; color: #F3F4F6 !important; }
h1, h2, h3, h4, h5, h6, span, p, label { color: #F3F4F6 !important; }
[data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1E293B; }
[data-testid="stSidebarNav"] span { color: #F3F4F6 !important; font-weight: 500 !important; }
[data-testid="stMetricLabel"] div, [data-testid="stMetricValue"] div { color: #F3F4F6 !important; }
.checkout-box {
    background-color: #1E293B !important; border: 1px solid #334155 !important; border-radius: 12px;
    padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
}
.cart-item {
    background-color: #1E293B !important; border-left: 4px solid #38BDF8 !important; border-radius: 6px;
    padding: 1.2rem; margin-bottom: 0.8rem; display: flex; justify-content: space-between;
    align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.stButton>button {
    background-color: #111827 !important; color: #38BDF8 !important; border: 1px solid #38BDF8 !important;
    border-radius: 8px !important; padding: 0.5rem 1rem !important; width: 100%; font-weight: bold !important;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #38BDF8 !important; color: #0B1120 !important; box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
}
.remove-btn .stButton>button {
    background-color: #ef4444 !important; color: white !important;
    border: 1px solid #ef4444 !important; font-size: 0.8rem !important;
    padding: 0.3rem 0.6rem !important; width: auto !important;
}
.remove-btn .stButton>button:hover {
    background-color: #dc2626 !important; box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("🛒 Your Shopping Cart")

cart = st.session_state.get("cart", [])

if len(cart) == 0:
    st.warning("Your Cart is Empty")
    if st.button("🛍 Go to Products"):
        st.switch_page("pages/products.py")
else:
    total = sum(item["price"] for item in cart)
    st.session_state.total_amount = total

    st.markdown('<div class="checkout-box">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric(label="Total Items Selected", value=len(cart))
        st.subheader(f"💰 Total Amount: ₹{total:,}")
    with col2:
        st.write(" ")
        if st.button("🚀 Proceed to Payment", key="top_checkout"):
            st.switch_page("pages/payment.py")
        if st.button("🗑 Clear Cart", key="clear_cart"):
            st.session_state.cart = []
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📦 Items in your cart")
    for idx, item in enumerate(cart):
        col_item, col_remove = st.columns([4, 1])
        with col_item:
            st.markdown(
                f"""
            <div class="cart-item">
                <span style="font-weight: 600; font-size: 1.1rem; color: #FFFFFF !important;">📦 {item['name']}</span>
                <span style="color: #38BDF8 !important; font-weight: bold; font-size: 1.1rem;">₹{item['price']:,}</span>
            </div>
        """,
                unsafe_allow_html=True,
            )
        with col_remove:
            st.markdown('<div class="remove-btn">', unsafe_allow_html=True)
            if st.button("❌ Remove", key=f"remove_{idx}"):
                st.session_state.cart.pop(idx)
                st.toast(f"Removed {item['name']} from cart", icon="🗑️")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
