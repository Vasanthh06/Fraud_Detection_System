import streamlit as st

# Login check
if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.switch_page("app.py")
    st.stop()

st.set_page_config(page_title="ShopZone", page_icon="🛍️", layout="wide")

if "cart" not in st.session_state:
    st.session_state.cart = []

total = sum(item["price"] for item in st.session_state.cart)
count = len(st.session_state.cart)

# ==================================
# MODERN UI CSS
# ==================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Top Bar */
.top-bar {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(92, 62, 245, 0.2);
}
.top-bar-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #fff;
}
.top-bar-title span { color: #FFD700; }
.top-bar-cart {
    background: rgba(92, 62, 245, 0.15);
    border: 1px solid rgba(92, 62, 245, 0.3);
    border-radius: 12px;
    padding: 10px 20px;
    color: #fff;
    font-weight: 600;
    font-size: 0.9rem;
}

/* Filter Bar */
.filter-bar {
    background: #fff;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 24px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* Product Card Container */
.product-card-container {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
    transition: all 0.3s ease;
    height: 100%;
}
.product-card-container:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(92, 62, 245, 0.12);
    border-color: #c4b5fd;
}
.product-image-area {
    position: relative;
    width: 100%;
    aspect-ratio: 4/3;
    overflow: hidden;
    background: #f8f9fa;
}
.product-badge {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    z-index: 10;
}
.badge-sale-bg { background: #ef4444; color: white; }
.badge-new-bg { background: #10b981; color: white; }
.product-info-area {
    padding: 16px 18px 18px;
}
.product-category {
    font-size: 0.7rem;
    color: #5c3ef5;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}
.product-name {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.3;
    margin-bottom: 6px;
    min-height: 2.6em;
}
.product-desc {
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 8px;
    line-height: 1.4;
}
.product-rating {
    font-size: 0.8rem;
    color: #f59e0b;
    font-weight: 600;
    margin-bottom: 10px;
}
.product-price-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 14px;
    flex-wrap: wrap;
}
.price-current {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    color: #5c3ef5;
}
.price-old {
    font-size: 0.85rem;
    color: #9ca3af;
    text-decoration: line-through;
}
.price-discount {
    font-size: 0.75rem;
    color: #ef4444;
    font-weight: 600;
    background: #fef2f2;
    padding: 2px 8px;
    border-radius: 6px;
}
.add-btn {
    width: 100%;
    background: linear-gradient(135deg, #5c3ef5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
}
.add-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(92, 62, 245, 0.3) !important;
}
.view-btn {
    width: 100%;
    background: #f3f4f6 !important;
    color: #4b5563 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    padding: 10px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}
.view-btn:hover {
    background: #e5e7eb !important;
}

/* Section headers */
.cat-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: #1a1a2e;
    margin: 32px 0 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.cat-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #e5e7eb, transparent);
    margin-left: 12px;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #9ca3af;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 12px; }

/* Bottom Cart Bar */
.bottom-cart-wrapper {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-top: 1px solid rgba(92, 62, 245, 0.3);
    padding: 16px 24px;
    z-index: 1000;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
}
.bottom-cart-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.bottom-cart-text {
    color: #fff;
    font-weight: 600;
    font-size: 1rem;
}
.bottom-cart-text span {
    color: #FFD700;
    font-weight: 800;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==================================
# TOP BAR
# ==================================
st.markdown(
    f"""
<div class="top-bar">
    <div class="top-bar-title">Shop<span>Zone</span> 🛍️</div>
    <div class="top-bar-cart">🛒 {count} items · ₹{total:,}</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==================================
# LOGOUT
# ==================================
_, col_logout = st.columns([11, 3])
with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.login_time = None
        st.session_state.admin_login = False
        st.session_state.cart = []
        st.session_state.total_amount = 0
        st.session_state.user_email = ""
        st.session_state.username = "User"
        st.session_state.payment_success = False
        st.switch_page("app.py")

# ==================================
# SEARCH & FILTER BAR
# ==================================
with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([3, 2, 1])
    with f1:
        search = st.text_input(
            "🔍 Search",
            placeholder="Search iPhone, sofa, rice...",
            label_visibility="collapsed",
            key="search_input",
        )
    with f2:
        # Placeholder - will be updated after products load
        cat_options = ["All Categories"]
        selected_cat = st.selectbox(
            "📂", cat_options, label_visibility="collapsed", key="cat_select"
        )
    with f3:
        sort_by = st.selectbox(
            "Sort",
            ["Default", "Price: Low→High", "Price: High→Low", "Rating"],
            label_visibility="collapsed",
            key="sort_select",
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================
# ALL PRODUCTS (Complete Original List)
# ==================================
all_products = [
    # ---- ELECTRONICS ----
    {
        "name": "Apple iPhone 16 Pro",
        "price": 129999,
        "old_price": 149999,
        "rating": "4.8",
        "desc": "256GB • A18 Pro Chip • Titanium",
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
        "category": "Electronics",
        "badge": "sale",
    },
    {
        "name": "Samsung Galaxy S25 Ultra",
        "price": 119999,
        "old_price": 134999,
        "rating": "4.7",
        "desc": "200MP Camera • Snapdragon Elite",
        "image": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
        "category": "Electronics",
        "badge": "",
    },
    {
        "name": "MacBook Air M4",
        "price": 99999,
        "old_price": 119999,
        "rating": "4.9",
        "desc": "M4 Chip • 16GB RAM • 512GB SSD",
        "image": "https://images.unsplash.com/photo-1517336714739-489689fd1ca8?w=400",
        "category": "Electronics",
        "badge": "new",
    },
    {
        "name": "Dell XPS 15",
        "price": 125000,
        "old_price": 145000,
        "rating": "4.7",
        "desc": "Intel Ultra 7 • RTX 4060",
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
        "category": "Electronics",
        "badge": "",
    },
    {
        "name": "Apple Watch Ultra 2",
        "price": 89999,
        "old_price": 99999,
        "rating": "4.8",
        "desc": "Titanium Body • GPS + Cellular",
        "image": "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400",
        "category": "Electronics",
        "badge": "",
    },
    {
        "name": "Sony WH-1000XM5",
        "price": 29999,
        "old_price": 34999,
        "rating": "4.9",
        "desc": "Industry Leading Noise Cancellation",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        "category": "Electronics",
        "badge": "sale",
    },
    {
        "name": "PlayStation 5 Slim",
        "price": 54999,
        "old_price": 59999,
        "rating": "4.9",
        "desc": "Ultra HD Gaming Console",
        "image": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400",
        "category": "Electronics",
        "badge": "",
    },
    {
        "name": "iPad Pro M4",
        "price": 109999,
        "old_price": 119999,
        "rating": "4.8",
        "desc": "M4 Chip • Liquid Retina XDR",
        "image": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400",
        "category": "Electronics",
        "badge": "new",
    },
    {
        "name": "AirPods Pro 2",
        "price": 24999,
        "old_price": 28999,
        "rating": "4.8",
        "desc": "ANC • Spatial Audio • H2 Chip",
        "image": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400",
        "category": "Electronics",
        "badge": "",
    },
    {
        "name": "Canon EOS R6 Mark II",
        "price": 229999,
        "old_price": 259999,
        "rating": "4.9",
        "desc": "40fps Burst • 6K Video",
        "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400",
        "category": "Electronics",
        "badge": "",
    },
    {
        "name": 'Samsung 65" QLED 4K',
        "price": 119999,
        "old_price": 149999,
        "rating": "4.7",
        "desc": "QLED • 120Hz • Smart TV",
        "image": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=400",
        "category": "Electronics",
        "badge": "sale",
    },
    {
        "name": "OnePlus 13",
        "price": 69999,
        "old_price": 79999,
        "rating": "4.6",
        "desc": "Snapdragon 8 Elite • 100W Charging",
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
        "category": "Electronics",
        "badge": "",
    },
    {
        "name": "Bose QuietComfort 45",
        "price": 27999,
        "old_price": 32999,
        "rating": "4.7",
        "desc": "22hr Battery • Noise Cancelling",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        "category": "Electronics",
        "badge": "",
    },
    {
        "name": "GoPro Hero 13",
        "price": 44999,
        "old_price": 49999,
        "rating": "4.7",
        "desc": "5.3K Video • HyperSmooth 7.0",
        "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400",
        "category": "Electronics",
        "badge": "",
    },
    # ---- COMPUTERS ----
    {
        "name": "Gaming Keyboard RGB",
        "price": 4999,
        "old_price": 6999,
        "rating": "4.5",
        "desc": "Mechanical • Cherry MX Red Switches",
        "image": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=400",
        "category": "Computers",
        "badge": "sale",
    },
    {
        "name": "Gaming Mouse Pro",
        "price": 2999,
        "old_price": 3999,
        "rating": "4.6",
        "desc": "16000 DPI • Optical Sensor",
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
        "category": "Computers",
        "badge": "",
    },
    {
        "name": '27" 4K Monitor',
        "price": 34999,
        "old_price": 42999,
        "rating": "4.7",
        "desc": "IPS Panel • 144Hz • HDR400",
        "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400",
        "category": "Computers",
        "badge": "",
    },
    {
        "name": "HP Pavilion Gaming Laptop",
        "price": 79999,
        "old_price": 94999,
        "rating": "4.5",
        "desc": "RTX 3050 • Ryzen 7 • 16GB RAM",
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
        "category": "Computers",
        "badge": "sale",
    },
    {
        "name": "Logitech MX Master 3S",
        "price": 8999,
        "old_price": 10999,
        "rating": "4.9",
        "desc": "8000 DPI • Quiet Clicks • Multi-Device",
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
        "category": "Computers",
        "badge": "",
    },
    {
        "name": "Corsair 32GB DDR5 RAM",
        "price": 12999,
        "old_price": 15999,
        "rating": "4.8",
        "desc": "6000MHz • RGB • Vengeance Series",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400",
        "category": "Computers",
        "badge": "new",
    },
    {
        "name": "Samsung 1TB NVMe SSD",
        "price": 7999,
        "old_price": 9999,
        "rating": "4.8",
        "desc": "7000MB/s Read • PCIe 4.0",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400",
        "category": "Computers",
        "badge": "",
    },
    {
        "name": "Webcam 4K Pro",
        "price": 5999,
        "old_price": 7999,
        "rating": "4.5",
        "desc": "4K 30fps • Auto Focus • HDR",
        "image": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400",
        "category": "Computers",
        "badge": "",
    },
    {
        "name": "USB-C Hub 10-in-1",
        "price": 2499,
        "old_price": 3499,
        "rating": "4.6",
        "desc": "HDMI 4K • PD 100W • Ethernet",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400",
        "category": "Computers",
        "badge": "",
    },
    # ---- FASHION ----
    {
        "name": "Men's Slim Fit Suit",
        "price": 8999,
        "old_price": 12999,
        "rating": "4.6",
        "desc": "Italian Wool • Navy Blue • Regular Fit",
        "image": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400",
        "category": "Fashion",
        "badge": "sale",
    },
    {
        "name": "Classic White Shirt",
        "price": 1299,
        "old_price": 1999,
        "rating": "4.5",
        "desc": "100% Cotton • Slim Fit • Formal",
        "image": "https://images.unsplash.com/photo-1603251579431-8041402bdeda?w=400",
        "category": "Fashion",
        "badge": "",
    },
    {
        "name": "Denim Jacket",
        "price": 2499,
        "old_price": 3499,
        "rating": "4.7",
        "desc": "Washed Denim • Street Style",
        "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400",
        "category": "Fashion",
        "badge": "",
    },
    {
        "name": "Chino Pants",
        "price": 1799,
        "old_price": 2499,
        "rating": "4.5",
        "desc": "Stretch Fabric • Multiple Colors",
        "image": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400",
        "category": "Fashion",
        "badge": "",
    },
    {
        "name": "Nike Air Max 270",
        "price": 12999,
        "old_price": 15995,
        "rating": "4.8",
        "desc": "Air Cushioning • Breathable Mesh",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "category": "Fashion",
        "badge": "sale",
    },
    {
        "name": "Leather Belt Premium",
        "price": 999,
        "old_price": 1499,
        "rating": "4.4",
        "desc": "Genuine Leather • Metal Buckle",
        "image": "https://images.unsplash.com/photo-1624222247344-550fb60fe8ff?w=400",
        "category": "Fashion",
        "badge": "",
    },
    {
        "name": "Hoodie Oversized",
        "price": 1999,
        "old_price": 2799,
        "rating": "4.6",
        "desc": "Fleece Inner • Drop Shoulder",
        "image": "https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=400",
        "category": "Fashion",
        "badge": "",
    },
    {
        "name": "Women's Floral Kurti",
        "price": 899,
        "old_price": 1299,
        "rating": "4.7",
        "desc": "Rayon Fabric • Ethnic Wear",
        "image": "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=400",
        "category": "Fashion",
        "badge": "new",
    },
    {
        "name": "Saree Silk Banarasi",
        "price": 5999,
        "old_price": 8999,
        "rating": "4.9",
        "desc": "Pure Silk • Zari Work • Festive",
        "image": "https://images.unsplash.com/photo-1610189352649-6a8e4938c059?w=400",
        "category": "Fashion",
        "badge": "",
    },
    {
        "name": "Women's Sneakers",
        "price": 3499,
        "old_price": 4999,
        "rating": "4.6",
        "desc": "Lightweight • Cushioned Sole",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "category": "Fashion",
        "badge": "",
    },
    {
        "name": "Sunglasses Aviator",
        "price": 1499,
        "old_price": 2499,
        "rating": "4.5",
        "desc": "UV400 Protection • Metal Frame",
        "image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400",
        "category": "Fashion",
        "badge": "sale",
    },
    {
        "name": "Tote Bag Canvas",
        "price": 799,
        "old_price": 1199,
        "rating": "4.4",
        "desc": "Large Capacity • Eco-Friendly",
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
        "category": "Fashion",
        "badge": "",
    },
    # ---- FURNITURE ----
    {
        "name": "Ergonomic Office Chair",
        "price": 18999,
        "old_price": 25999,
        "rating": "4.7",
        "desc": "Lumbar Support • Adjustable Arms",
        "image": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=400",
        "category": "Furniture",
        "badge": "sale",
    },
    {
        "name": "Solid Wood Dining Table",
        "price": 34999,
        "old_price": 44999,
        "rating": "4.8",
        "desc": "6-Seater • Sheesham Wood",
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400",
        "category": "Furniture",
        "badge": "",
    },
    {
        "name": "L-Shaped Sofa Set",
        "price": 49999,
        "old_price": 69999,
        "rating": "4.6",
        "desc": "5-Seater • Premium Fabric",
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400",
        "category": "Furniture",
        "badge": "sale",
    },
    {
        "name": "King Size Bed Frame",
        "price": 28999,
        "old_price": 38999,
        "rating": "4.7",
        "desc": "Engineered Wood • Hydraulic Storage",
        "image": "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=400",
        "category": "Furniture",
        "badge": "",
    },
    {
        "name": "Bookshelf 5-Tier",
        "price": 7999,
        "old_price": 10999,
        "rating": "4.5",
        "desc": "Metal Frame • Industrial Style",
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
        "category": "Furniture",
        "badge": "",
    },
    {
        "name": "Standing Desk Electric",
        "price": 24999,
        "old_price": 32999,
        "rating": "4.8",
        "desc": "Height Adjustable • Memory Settings",
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400",
        "category": "Furniture",
        "badge": "new",
    },
    {
        "name": "Wardrobe 3-Door",
        "price": 18999,
        "old_price": 24999,
        "rating": "4.6",
        "desc": "Mirror Sliding Door • Large Capacity",
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
        "category": "Furniture",
        "badge": "",
    },
    {
        "name": "Bean Bag XXL",
        "price": 3999,
        "old_price": 5999,
        "rating": "4.5",
        "desc": "Filled • Waterproof Cover • Washable",
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400",
        "category": "Furniture",
        "badge": "sale",
    },
    {
        "name": "TV Unit Modern",
        "price": 12999,
        "old_price": 17999,
        "rating": "4.6",
        "desc": "LED Lights • Multiple Compartments",
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400",
        "category": "Furniture",
        "badge": "",
    },
    {
        "name": "Coffee Table Glass",
        "price": 8999,
        "old_price": 11999,
        "rating": "4.5",
        "desc": "Tempered Glass • Metal Legs",
        "image": "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=400",
        "category": "Furniture",
        "badge": "",
    },
    # ---- GROCERIES ----
    {
        "name": "Organic Basmati Rice 5kg",
        "price": 699,
        "old_price": 849,
        "rating": "4.7",
        "desc": "Long Grain • Aged 2 Years",
        "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400",
        "category": "Groceries",
        "badge": "",
    },
    {
        "name": "Cold Pressed Olive Oil 1L",
        "price": 899,
        "old_price": 1199,
        "rating": "4.8",
        "desc": "Extra Virgin • Imported",
        "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400",
        "category": "Groceries",
        "badge": "",
    },
    {
        "name": "Mixed Dry Fruits 500g",
        "price": 599,
        "old_price": 799,
        "rating": "4.6",
        "desc": "Almonds, Cashews, Pistachios",
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400",
        "category": "Groceries",
        "badge": "",
    },
    {
        "name": "Himalayan Pink Salt 1kg",
        "price": 199,
        "old_price": 299,
        "rating": "4.5",
        "desc": "Natural • Mineral Rich",
        "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400",
        "category": "Groceries",
        "badge": "",
    },
    {
        "name": "Green Tea 100 Bags",
        "price": 299,
        "old_price": 399,
        "rating": "4.7",
        "desc": "Antioxidant Rich • Zero Calories",
        "image": "https://images.unsplash.com/photo-1556742393-d75f468bfcb0?w=400",
        "category": "Groceries",
        "badge": "",
    },
    {
        "name": "Whole Wheat Atta 10kg",
        "price": 449,
        "old_price": 549,
        "rating": "4.5",
        "desc": "Stone Ground • High Fibre",
        "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400",
        "category": "Groceries",
        "badge": "",
    },
    {
        "name": "Farm Fresh Honey 500g",
        "price": 349,
        "old_price": 499,
        "rating": "4.8",
        "desc": "Raw Unfiltered • Multifloral",
        "image": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400",
        "category": "Groceries",
        "badge": "",
    },
    {
        "name": "Protein Granola 800g",
        "price": 499,
        "old_price": 649,
        "rating": "4.6",
        "desc": "Oats, Nuts & Seeds • No Sugar Added",
        "image": "https://images.unsplash.com/photo-1517686469429-8bdb88b9f907?w=400",
        "category": "Groceries",
        "badge": "new",
    },
    {
        "name": "Cow Ghee Pure 1kg",
        "price": 799,
        "old_price": 999,
        "rating": "4.9",
        "desc": "A2 Milk • Traditional Bilona Method",
        "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400",
        "category": "Groceries",
        "badge": "",
    },
    {
        "name": "Assorted Pickle Set",
        "price": 399,
        "old_price": 549,
        "rating": "4.5",
        "desc": "Mango, Lemon, Chilli • No Preservatives",
        "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400",
        "category": "Groceries",
        "badge": "",
    },
    # ---- MAKEUP ----
    {
        "name": "Matte Lipstick Set 12pc",
        "price": 999,
        "old_price": 1499,
        "rating": "4.7",
        "desc": "Long-lasting • 12 Shades",
        "image": "https://images.unsplash.com/photo-1586495777744-4e6232bf2edd?w=400",
        "category": "Makeup",
        "badge": "sale",
    },
    {
        "name": "Foundation SPF 30",
        "price": 1299,
        "old_price": 1799,
        "rating": "4.6",
        "desc": "Full Coverage • 24hr Wear",
        "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400",
        "category": "Makeup",
        "badge": "",
    },
    {
        "name": "Eyeshadow Palette 18 Shades",
        "price": 1499,
        "old_price": 2199,
        "rating": "4.8",
        "desc": "Shimmer & Matte • Highly Pigmented",
        "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400",
        "category": "Makeup",
        "badge": "",
    },
    {
        "name": "Waterproof Kajal",
        "price": 299,
        "old_price": 449,
        "rating": "4.7",
        "desc": "12hr Wear • Smudge Proof",
        "image": "https://images.unsplash.com/photo-1571875257727-256c39da42af?w=400",
        "category": "Makeup",
        "badge": "",
    },
    {
        "name": "BB Cream SPF 40",
        "price": 799,
        "old_price": 1199,
        "rating": "4.5",
        "desc": "Moisturizes + Covers + Protects",
        "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400",
        "category": "Makeup",
        "badge": "",
    },
    {
        "name": "Blush Duo Palette",
        "price": 699,
        "old_price": 999,
        "rating": "4.6",
        "desc": "Buildable Color • Satin Finish",
        "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400",
        "category": "Makeup",
        "badge": "",
    },
    {
        "name": "Mascara Volume & Curl",
        "price": 499,
        "old_price": 699,
        "rating": "4.7",
        "desc": "Clump-Free • Volumizing Formula",
        "image": "https://images.unsplash.com/photo-1571875257727-256c39da42af?w=400",
        "category": "Makeup",
        "badge": "new",
    },
    {
        "name": "Setting Spray 150ml",
        "price": 599,
        "old_price": 849,
        "rating": "4.5",
        "desc": "Locks Makeup • Hydrating Mist",
        "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400",
        "category": "Makeup",
        "badge": "",
    },
    {
        "name": "Concealer Stick",
        "price": 449,
        "old_price": 649,
        "rating": "4.6",
        "desc": "Full Coverage • Crease Resistant",
        "image": "https://images.unsplash.com/photo-1586495777744-4e6232bf2edd?w=400",
        "category": "Makeup",
        "badge": "",
    },
    {
        "name": "Highlighter Powder",
        "price": 749,
        "old_price": 1099,
        "rating": "4.7",
        "desc": "Blinding Glow • Rose Gold Shade",
        "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400",
        "category": "Makeup",
        "badge": "",
    },
    # ---- PERFUMES ----
    {
        "name": "Chanel No.5 EDP 100ml",
        "price": 14999,
        "old_price": 17999,
        "rating": "4.9",
        "desc": "Floral Aldehyde • Iconic Fragrance",
        "image": "https://images.unsplash.com/photo-1590439471364-192aa70c0b53?w=400",
        "category": "Perfumes",
        "badge": "",
    },
    {
        "name": "Davidoff Cool Water 125ml",
        "price": 3499,
        "old_price": 4999,
        "rating": "4.7",
        "desc": "Fresh Aquatic • Men's Fragrance",
        "image": "https://images.unsplash.com/photo-1541643600914-78b084683702?w=400",
        "category": "Perfumes",
        "badge": "sale",
    },
    {
        "name": "Versace Eros EDP 100ml",
        "price": 8999,
        "old_price": 11999,
        "rating": "4.8",
        "desc": "Fresh Oriental • Long Lasting",
        "image": "https://images.unsplash.com/photo-1590439471364-192aa70c0b53?w=400",
        "category": "Perfumes",
        "badge": "",
    },
    {
        "name": "Forest Essentials Attar",
        "price": 1999,
        "old_price": 2799,
        "rating": "4.6",
        "desc": "Rose & Sandalwood • Alcohol-Free",
        "image": "https://images.unsplash.com/photo-1541643600914-78b084683702?w=400",
        "category": "Perfumes",
        "badge": "",
    },
    {
        "name": "Fogg Scent Marco 150ml",
        "price": 399,
        "old_price": 549,
        "rating": "4.5",
        "desc": "No Gas • Long Lasting 800 Sprays",
        "image": "https://images.unsplash.com/photo-1590439471364-192aa70c0b53?w=400",
        "category": "Perfumes",
        "badge": "",
    },
    {
        "name": "Armaf Club de Nuit 105ml",
        "price": 2499,
        "old_price": 3499,
        "rating": "4.7",
        "desc": "Woody Aromatic • Intense Edition",
        "image": "https://images.unsplash.com/photo-1541643600914-78b084683702?w=400",
        "category": "Perfumes",
        "badge": "new",
    },
    {
        "name": "Dior Sauvage EDP 100ml",
        "price": 13999,
        "old_price": 16999,
        "rating": "4.9",
        "desc": "Spicy Fresh • Men's Signature",
        "image": "https://images.unsplash.com/photo-1590439471364-192aa70c0b53?w=400",
        "category": "Perfumes",
        "badge": "",
    },
    {
        "name": "Engage Woman Body Mist",
        "price": 249,
        "old_price": 399,
        "rating": "4.4",
        "desc": "Floral Fruity • 150ml",
        "image": "https://images.unsplash.com/photo-1541643600914-78b084683702?w=400",
        "category": "Perfumes",
        "badge": "sale",
    },
    # ---- FACE WASH ----
    {
        "name": "Himalaya Purifying Neem",
        "price": 149,
        "old_price": 199,
        "rating": "4.6",
        "desc": "Anti-Acne • Deep Cleanse • 150ml",
        "image": "https://images.unsplash.com/photo-1556228578-567ba127e37f?w=400",
        "category": "Face Wash",
        "badge": "",
    },
    {
        "name": "Cetaphil Gentle Cleanser",
        "price": 499,
        "old_price": 699,
        "rating": "4.8",
        "desc": "Sensitive Skin • Soap Free • 250ml",
        "image": "https://images.unsplash.com/photo-1556228578-567ba127e37f?w=400",
        "category": "Face Wash",
        "badge": "",
    },
    {
        "name": "Mamaearth Vitamin C",
        "price": 299,
        "old_price": 399,
        "rating": "4.7",
        "desc": "Brightening • Toxin Free • 100ml",
        "image": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400",
        "category": "Face Wash",
        "badge": "new",
    },
    {
        "name": "Neutrogena Deep Clean",
        "price": 349,
        "old_price": 499,
        "rating": "4.6",
        "desc": "Pore Minimizing • Oil Control",
        "image": "https://images.unsplash.com/photo-1556228578-567ba127e37f?w=400",
        "category": "Face Wash",
        "badge": "",
    },
    {
        "name": "The Ordinary Salicylic 2%",
        "price": 699,
        "old_price": 999,
        "rating": "4.7",
        "desc": "Exfoliating • Acne-Prone Skin",
        "image": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400",
        "category": "Face Wash",
        "badge": "",
    },
    {
        "name": "Plum Bright Years",
        "price": 449,
        "old_price": 599,
        "rating": "4.5",
        "desc": "Anti-Ageing • Vegan • 100ml",
        "image": "https://images.unsplash.com/photo-1556228578-567ba127e37f?w=400",
        "category": "Face Wash",
        "badge": "sale",
    },
    {
        "name": "WOW Skin Science Apple",
        "price": 249,
        "old_price": 399,
        "rating": "4.6",
        "desc": "ACV • Brightening • 100ml",
        "image": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400",
        "category": "Face Wash",
        "badge": "",
    },
    {
        "name": "Garnier Micellar Gel",
        "price": 199,
        "old_price": 299,
        "rating": "4.5",
        "desc": "No-Rinse Cleansing • All Skin Types",
        "image": "https://images.unsplash.com/photo-1556228578-567ba127e37f?w=400",
        "category": "Face Wash",
        "badge": "",
    },
    # ---- HOME ----
    {
        "name": "LED Ceiling Light 36W",
        "price": 1499,
        "old_price": 2199,
        "rating": "4.6",
        "desc": "Cool White • Energy Saving • 4000K",
        "image": "https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=400",
        "category": "Home",
        "badge": "",
    },
    {
        "name": "Air Purifier HEPA",
        "price": 8999,
        "old_price": 12999,
        "rating": "4.7",
        "desc": "HEPA H13 • Coverage 400 sqft",
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
        "category": "Home",
        "badge": "sale",
    },
    {
        "name": "Robot Vacuum Cleaner",
        "price": 19999,
        "old_price": 27999,
        "rating": "4.8",
        "desc": "Auto Mapping • App Control • 2500Pa",
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
        "category": "Home",
        "badge": "",
    },
    {
        "name": "Scented Candle Set 6pc",
        "price": 999,
        "old_price": 1499,
        "rating": "4.6",
        "desc": "Soy Wax • 40hr Burn • Gift Ready",
        "image": "https://images.unsplash.com/photo-1535016120720-40c646be5580?w=400",
        "category": "Home",
        "badge": "new",
    },
    {
        "name": "Bed Sheet Set King",
        "price": 1999,
        "old_price": 2999,
        "rating": "4.7",
        "desc": "400 TC Cotton • 4-Piece Set",
        "image": "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=400",
        "category": "Home",
        "badge": "",
    },
    {
        "name": "Wall Clock Minimalist",
        "price": 899,
        "old_price": 1299,
        "rating": "4.5",
        "desc": "Silent Movement • 12 inch • Wooden",
        "image": "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=400",
        "category": "Home",
        "badge": "",
    },
    {
        "name": "Smart LED Strip 5m",
        "price": 1299,
        "old_price": 1999,
        "rating": "4.6",
        "desc": "RGB • App Control • Music Sync",
        "image": "https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=400",
        "category": "Home",
        "badge": "",
    },
    {
        "name": "Picture Frames Set 3pc",
        "price": 699,
        "old_price": 999,
        "rating": "4.4",
        "desc": "Wood & Glass • Multiple Sizes",
        "image": "https://images.unsplash.com/photo-1513519245088-0e12902e35ca?w=400",
        "category": "Home",
        "badge": "",
    },
    {
        "name": "Curtains Blackout 2pc",
        "price": 1499,
        "old_price": 2199,
        "rating": "4.6",
        "desc": "Thermal Insulated • 7ft • Multiple Colors",
        "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=400",
        "category": "Home",
        "badge": "",
    },
    {
        "name": "Bathroom Accessories Set",
        "price": 1199,
        "old_price": 1699,
        "rating": "4.5",
        "desc": "5-Piece • Stainless Steel",
        "image": "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=400",
        "category": "Home",
        "badge": "sale",
    },
    # ---- KITCHEN ----
    {
        "name": "Instant Pot Duo 6Qt",
        "price": 9999,
        "old_price": 13999,
        "rating": "4.8",
        "desc": "7-in-1 Electric Pressure Cooker",
        "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400",
        "category": "Kitchen",
        "badge": "sale",
    },
    {
        "name": "Non-Stick Cookware Set",
        "price": 4999,
        "old_price": 7499,
        "rating": "4.6",
        "desc": "5-Piece • Granite Coating",
        "image": "https://images.unsplash.com/photo-1585837146751-a7b3d4d0c56a?w=400",
        "category": "Kitchen",
        "badge": "",
    },
    {
        "name": "Stand Mixer 1000W",
        "price": 14999,
        "old_price": 19999,
        "rating": "4.7",
        "desc": "5L Bowl • 6 Speed • Dough Hook",
        "image": "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=400",
        "category": "Kitchen",
        "badge": "",
    },
    {
        "name": "Air Fryer 5L Digital",
        "price": 5999,
        "old_price": 8499,
        "rating": "4.8",
        "desc": "Digital Display • 8 Presets • 1800W",
        "image": "https://images.unsplash.com/photo-1629740067897-4a56dfc04e5e?w=400",
        "category": "Kitchen",
        "badge": "new",
    },
    {
        "name": "Coffee Machine Espresso",
        "price": 12999,
        "old_price": 17999,
        "rating": "4.7",
        "desc": "15 Bar Pressure • Milk Frother",
        "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400",
        "category": "Kitchen",
        "badge": "",
    },
    {
        "name": "Knife Set Professional 7pc",
        "price": 3999,
        "old_price": 5999,
        "rating": "4.8",
        "desc": "German Steel • Ergonomic Handle",
        "image": "https://images.unsplash.com/photo-1593618998160-e34014e67546?w=400",
        "category": "Kitchen",
        "badge": "",
    },
    {
        "name": "Blender High Speed 1200W",
        "price": 4499,
        "old_price": 6499,
        "rating": "4.6",
        "desc": "BPA Free • 1.5L Jar • 3 Speed",
        "image": "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400",
        "category": "Kitchen",
        "badge": "sale",
    },
    {
        "name": "Steel Tiffin Box 4-Tier",
        "price": 799,
        "old_price": 1199,
        "rating": "4.5",
        "desc": "Leak Proof • Insulated • With Bag",
        "image": "https://images.unsplash.com/photo-1606914501449-5a96b6ce24ca?w=400",
        "category": "Kitchen",
        "badge": "",
    },
    {
        "name": "Induction Cooktop 2000W",
        "price": 3499,
        "old_price": 4999,
        "rating": "4.7",
        "desc": "Touch Control • Auto Shutoff",
        "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400",
        "category": "Kitchen",
        "badge": "",
    },
    {
        "name": "Silicone Bakeware Set",
        "price": 1299,
        "old_price": 1899,
        "rating": "4.5",
        "desc": "6-Piece • Non-Stick • Oven Safe",
        "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400",
        "category": "Kitchen",
        "badge": "",
    },
    # ---- SPORTS ----
    {
        "name": "Yoga Mat Anti-Slip 6mm",
        "price": 799,
        "old_price": 1199,
        "rating": "4.6",
        "desc": "TPE Material • Eco-Friendly • Carry Strap",
        "image": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400",
        "category": "Sports",
        "badge": "",
    },
    {
        "name": "Dumbbell Set 20kg",
        "price": 3999,
        "old_price": 5999,
        "rating": "4.7",
        "desc": "Rubber Coated • Adjustable Pair",
        "image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400",
        "category": "Sports",
        "badge": "",
    },
    {
        "name": "Resistance Bands Set 5pc",
        "price": 599,
        "old_price": 899,
        "rating": "4.5",
        "desc": "Heavy Duty Latex • Multiple Levels",
        "image": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400",
        "category": "Sports",
        "badge": "sale",
    },
    {
        "name": "Cricket Bat English Willow",
        "price": 4999,
        "old_price": 6999,
        "rating": "4.8",
        "desc": "Grade 2 • Full Size • SH",
        "image": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=400",
        "category": "Sports",
        "badge": "",
    },
    {
        "name": "Jump Rope Speed 3m",
        "price": 399,
        "old_price": 599,
        "rating": "4.4",
        "desc": "Adjustable Length • Ball Bearings",
        "image": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400",
        "category": "Sports",
        "badge": "",
    },
    {
        "name": "Foam Roller Deep Tissue",
        "price": 999,
        "old_price": 1499,
        "rating": "4.5",
        "desc": "High Density • Grid Pattern • 33cm",
        "image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400",
        "category": "Sports",
        "badge": "",
    },
    # ---- BOOKS ----
    {
        "name": "Atomic Habits – James Clear",
        "price": 499,
        "old_price": 699,
        "rating": "4.9",
        "desc": "Bestseller • Self-Help • Paperback",
        "image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400",
        "category": "Books",
        "badge": "",
    },
    {
        "name": "The Alchemist – Paulo Coelho",
        "price": 299,
        "old_price": 399,
        "rating": "4.8",
        "desc": "Classic Fiction • Paperback",
        "image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400",
        "category": "Books",
        "badge": "",
    },
    {
        "name": "Rich Dad Poor Dad",
        "price": 349,
        "old_price": 499,
        "rating": "4.7",
        "desc": "Finance • Self-Help • Paperback",
        "image": "https://images.unsplash.com/photo-1526280760714-f9e8b26f318f?w=400",
        "category": "Books",
        "badge": "sale",
    },
    {
        "name": "The Psychology of Money",
        "price": 449,
        "old_price": 599,
        "rating": "4.8",
        "desc": "Morgan Housel • Personal Finance",
        "image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400",
        "category": "Books",
        "badge": "new",
    },
    {
        "name": "Zero to One – Peter Thiel",
        "price": 399,
        "old_price": 549,
        "rating": "4.7",
        "desc": "Startup • Business • Paperback",
        "image": "https://images.unsplash.com/photo-1526280760714-f9e8b26f318f?w=400",
        "category": "Books",
        "badge": "",
    },
    # ---- TOYS ----
    {
        "name": "LEGO City Police Set",
        "price": 3999,
        "old_price": 5499,
        "rating": "4.8",
        "desc": "374 Pieces • Age 6+ • Creative Build",
        "image": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400",
        "category": "Toys",
        "badge": "",
    },
    {
        "name": "RC Car 4WD Off-Road",
        "price": 2999,
        "old_price": 4499,
        "rating": "4.6",
        "desc": "1:16 Scale • 25km/h • 2.4GHz",
        "image": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400",
        "category": "Toys",
        "badge": "sale",
    },
    {
        "name": "Barbie Dreamhouse",
        "price": 5999,
        "old_price": 7999,
        "rating": "4.7",
        "desc": "3 Floors • 8 Rooms • Accessories",
        "image": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400",
        "category": "Toys",
        "badge": "",
    },
    {
        "name": "Rubik's Cube 3x3",
        "price": 299,
        "old_price": 449,
        "rating": "4.5",
        "desc": "Original • Smooth Turning • Speed Cube",
        "image": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400",
        "category": "Toys",
        "badge": "",
    },
    {
        "name": "Drone with HD Camera",
        "price": 8999,
        "old_price": 12999,
        "rating": "4.6",
        "desc": "1080p • Auto Return • 20min Flight",
        "image": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400",
        "category": "Toys",
        "badge": "new",
    },
]

# Clean products
all_products = [
    p
    for p in all_products
    if isinstance(p, dict)
    and all(k in p for k in ["name", "price", "rating", "desc", "image", "category"])
]

# Get actual categories for dropdown
categories = ["All Categories"] + sorted(list(set(p["category"] for p in all_products)))

# ==================================
# RE-RENDER FILTER BAR WITH REAL CATEGORIES
# ==================================
# We need to redraw the filter bar with correct categories
# Streamlit will use the cached widget values
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
f1, f2, f3 = st.columns([3, 2, 1])
with f1:
    search = st.text_input(
        "🔍 Search",
        placeholder="Search products...",
        label_visibility="collapsed",
        key="search_input_v2",
    )
with f2:
    selected_cat = st.selectbox(
        "📂", categories, label_visibility="collapsed", key="cat_select_v2"
    )
with f3:
    sort_by = st.selectbox(
        "Sort",
        ["Default", "Price: Low→High", "Price: High→Low", "Rating"],
        label_visibility="collapsed",
        key="sort_select_v2",
    )
st.markdown("</div>", unsafe_allow_html=True)

# Apply filters
filtered = all_products
if search:
    filtered = [
        p
        for p in filtered
        if search.lower() in p["name"].lower()
        or search.lower() in p["category"].lower()
        or search.lower() in p["desc"].lower()
    ]
if selected_cat != "All Categories":
    filtered = [p for p in filtered if p["category"] == selected_cat]
if sort_by == "Price: Low→High":
    filtered = sorted(filtered, key=lambda x: x["price"])
elif sort_by == "Price: High→Low":
    filtered = sorted(filtered, key=lambda x: x["price"], reverse=True)
elif sort_by == "Rating":
    filtered = sorted(filtered, key=lambda x: float(x["rating"]), reverse=True)

st.markdown(
    f"<p style='color:#6b7280;font-size:0.9rem;margin-bottom:20px;'>Showing <b style='color:#5c3ef5'>{len(filtered)}</b> products</p>",
    unsafe_allow_html=True,
)

# ==================================
# PRODUCT GRID RENDERER (Using st.image for reliability)
# ==================================
COLS = 4


def render_product_card(product, idx):
    """Render a single product card using Streamlit native components"""
    # Badge logic
    badge_html = ""
    if product.get("badge") == "sale":
        discount_pct = (
            round(
                ((product["old_price"] - product["price"]) / product["old_price"]) * 100
            )
            if product.get("old_price")
            else 0
        )
        badge_html = (
            f'<div class="product-badge badge-sale-bg">🔥 {discount_pct}% OFF</div>'
            if discount_pct > 0
            else '<div class="product-badge badge-sale-bg">SALE</div>'
        )
    elif product.get("badge") == "new":
        badge_html = '<div class="product-badge badge-new-bg">✨ NEW</div>'

    # Price logic
    old_price_html = (
        f'<span class="price-old">₹{product["old_price"]:,}</span>'
        if product.get("old_price")
        else ""
    )
    discount_html = ""
    if product.get("old_price") and product["old_price"] > product["price"]:
        pct = round(
            ((product["old_price"] - product["price"]) / product["old_price"]) * 100
        )
        discount_html = f'<span class="price-discount">{pct}% off</span>'

    # Card HTML (info only, image rendered separately via st.image)
    card_html = f"""
    <div class="product-card-container">
        <div class="product-image-area">
            {badge_html}
        </div>
        <div class="product-info-area">
            <div class="product-category">{product['category']}</div>
            <div class="product-name">{product['name']}</div>
            <div class="product-desc">{product['desc']}</div>
            <div class="product-rating">{'⭐' * int(float(product['rating']))} {product['rating']}</div>
            <div class="product-price-row">
                <span class="price-current">₹{product['price']:,}</span>
                {old_price_html}
                {discount_html}
            </div>
        </div>
    </div>
    """
    return card_html


def show_grid_modern(product_list):
    """Render products in a modern responsive grid using st.image()"""
    for row_start in range(0, len(product_list), COLS):
        row_items = product_list[row_start : row_start + COLS]
        cols = st.columns(COLS, gap="small")
        for col_idx, product in enumerate(row_items):
            with cols[col_idx]:
                # Use st.container(border=True) for the card frame
                with st.container(border=True):
                    # Render image using st.image (reliable)
                    try:
                        st.image(product["image"], use_container_width=True)
                    except:
                        st.image(
                            "https://via.placeholder.com/300x300?text=No+Image",
                            use_container_width=True,
                        )

                    # Badge
                    badge = product.get("badge", "")
                    if badge == "sale":
                        st.markdown(
                            "<span style='background:#ef4444;color:white;padding:2px 8px;border-radius:6px;font-size:0.7rem;font-weight:700;'>🔥 SALE</span>",
                            unsafe_allow_html=True,
                        )
                    elif badge == "new":
                        st.markdown(
                            "<span style='background:#10b981;color:white;padding:2px 8px;border-radius:6px;font-size:0.7rem;font-weight:700;'>✨ NEW</span>",
                            unsafe_allow_html=True,
                        )

                    # Product info
                    st.markdown(
                        f"<div style='font-size:0.7rem;color:#5c3ef5;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;'>{product['category']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='font-family:Syne,sans-serif;font-size:0.9rem;font-weight:700;color:#1a1a2e;line-height:1.3;margin-bottom:4px;'>{product['name']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='font-size:0.78rem;color:#6b7280;margin-bottom:4px;'>{product['desc']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='font-size:0.8rem;color:#f59e0b;font-weight:600;margin-bottom:8px;'>{'⭐' * int(float(product['rating']))} {product['rating']}</div>",
                        unsafe_allow_html=True,
                    )

                    # Price row
                    price_col1, price_col2 = st.columns([1, 1])
                    with price_col1:
                        st.markdown(
                            f"<div style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:#5c3ef5;'>₹{product['price']:,}</div>",
                            unsafe_allow_html=True,
                        )
                    with price_col2:
                        if product.get("old_price"):
                            st.markdown(
                                f"<div style='font-size:0.8rem;color:#9ca3af;text-decoration:line-through;'>₹{product['old_price']:,}</div>",
                                unsafe_allow_html=True,
                            )

                    # Buttons
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        btn_key = (
                            f"add_{abs(hash(product['name'] + str(product['price'])))}"
                        )
                        if st.button("🛒 Add", key=btn_key, use_container_width=True):
                            st.session_state.cart.append(product)
                            st.toast(f"✅ {product['name']} added to cart!", icon="🛒")
                            st.rerun()
                    with btn_col2:
                        st.link_button(
                            "👁️ View", "https://www.amazon.in", use_container_width=True
                        )


# ==================================
# RENDER BY CATEGORY OR SEARCH RESULTS
# ==================================
emoji_map = {
    "Electronics": "📱",
    "Computers": "💻",
    "Fashion": "👗",
    "Furniture": "🛋️",
    "Groceries": "🛒",
    "Makeup": "💄",
    "Perfumes": "🌸",
    "Face Wash": "🧴",
    "Home": "🏠",
    "Kitchen": "🍳",
    "Sports": "🏋️",
    "Books": "📚",
    "Toys": "🧸",
}

if selected_cat == "All Categories" and not search:
    for cat in sorted(set(p["category"] for p in all_products)):
        cat_prods = [p for p in filtered if p["category"] == cat]
        if cat_prods:
            icon = emoji_map.get(cat, "📦")
            st.markdown(
                f'<div class="cat-header">{icon} {cat}</div>', unsafe_allow_html=True
            )
            show_grid_modern(cat_prods)
else:
    if not filtered:
        st.markdown(
            """
        <div class="empty-state">
            <div class="icon">🔍</div>
            <div style="font-size:1.2rem;font-weight:700;color:#4b5563;margin-bottom:8px">No products found</div>
            <div style="color:#9ca3af">Try a different search or category</div>
        </div>""",
            unsafe_allow_html=True,
        )
    else:
        show_grid_modern(filtered)

# ==================================
# BOTTOM CART BAR
# ==================================
if count > 0:
    st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
    <div class="bottom-cart-wrapper">
        <div class="bottom-cart-inner">
            <div class="bottom-cart-text">🛒 <span>{count}</span> items · Total: <span>₹{total:,}</span></div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Streamlit buttons for functionality
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("🗑️ Clear Cart", key="bottom_clear"):
            st.session_state.cart = []
            st.rerun()
    with col3:
        if st.button("💳 Checkout", key="bottom_checkout", type="primary"):
            st.session_state.total_amount = total
            st.switch_page("cart.py")
