import streamlit as st

st.set_page_config(page_title="Cart", page_icon="🛒", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

if "cart" not in st.session_state:
    st.session_state.cart = []

total = sum(item["price"] for item in st.session_state.cart)
count = len(st.session_state.cart)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0d1117; }
.cart-title { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: #f1f5f9; margin-bottom: 24px; }
.cart-item {
    background: linear-gradient(135deg, #1a1f2e 0%, #161b2a 100%);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 12px;
    border: 1px solid rgba(99,102,241,0.18);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.cart-item-name { color: #f1f5f9; font-weight: 600; font-size: 1rem; }
.cart-item-price { color: #818cf8; font-weight: 800; font-size: 1.1rem; font-family: 'Syne', sans-serif; }
.cart-total {
    background: linear-gradient(135deg, #1a1f2e 0%, #161b2a 100%);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(99,102,241,0.3);
    margin-top: 24px;
}
.cart-total-text { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #FFD700; }
.empty-cart {
    text-align: center;
    padding: 80px 20px;
    color: #94a3b8;
}
.empty-cart .icon { font-size: 4rem; margin-bottom: 16px; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="cart-title">🛒 Your Cart</div>', unsafe_allow_html=True)

if count == 0:
    st.markdown(
        """
    <div class="empty-cart">
        <div class="icon">🛒</div>
        <div style="font-size:1.3rem;font-weight:700;color:#e2e8f0;margin-bottom:8px;">Your cart is empty</div>
        <div style="color:#94a3b8;">Add some products to get started!</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("🛍️ Continue Shopping", use_container_width=True):
        st.switch_page("pages/products.py")
    st.stop()

# Show cart items
for i, item in enumerate(st.session_state.cart):
    c1, c2, c3 = st.columns([5, 2, 1])
    with c1:
        st.markdown(
            f'<div class="cart-item-name">{item["name"]}</div>', unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="color:#94a3b8;font-size:0.8rem;">{item["desc"]}</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="cart-item-price">₹{item["price"]:,}</div>',
            unsafe_allow_html=True,
        )
    with c3:
        if st.button("❌", key=f"remove_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

# Total section
st.markdown(
    f"""
<div class="cart-total">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div style="color:#e2e8f0;font-size:1rem;font-weight:600;">Total ({count} items)</div>
        <div class="cart-total-text">₹{total:,}</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Action buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🛍️ Continue Shopping", use_container_width=True):
        st.switch_page("pages/products.py")
with col2:
    if st.button("🗑️ Clear Cart", use_container_width=True):
        st.session_state.cart = []
        st.rerun()
with col3:
    if st.button("💳 Checkout", type="primary", use_container_width=True):
        st.switch_page("pages/payment.py")
