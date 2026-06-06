import streamlit as st

if not st.session_state.get("logged_in"):
    st.error("Please Login First")
    st.stop()

st.title("🛒 Shopping Cart")

cart = st.session_state.get("cart", [])
if st.button("🗑 Clear Cart"):
    st.session_state.cart = []
    st.rerun()

if len(cart) == 0:

    st.warning("Your Cart is Empty")

else:

    total = 0

    for item in cart:

        st.write(f"📦 {item['name']} - ₹{item['price']:,}")

        total += item["price"]

    st.divider()

    st.subheader(f"💰 Total Amount: ₹{total:,}")

    st.session_state.total_amount = total

    if st.button("Proceed to Payment"):
        st.switch_page("pages/payment.py")
