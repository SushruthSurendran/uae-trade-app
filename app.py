import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Trade Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp { background: #ffffff; color: #1a1a1a; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stHeader"] { background: transparent; }

.topbar {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 20px 0 14px;
    border-bottom: 1.5px solid #1a1a1a;
    margin-bottom: 0;
}
.topbar-left { font-size: 0.95rem; font-weight: 600; letter-spacing: -0.01em; color: #1a1a1a; }
.topbar-right { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: #aaa; }
.topbar-right span { color: #1a1a1a; font-weight: 500; }

.lbl {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #aaa;
    margin: 28px 0 14px;
}

.stTextInput label, .stNumberInput label, .stSelectbox label {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #888 !important;
    margin-bottom: 5px !important;
}
.stTextInput input, .stNumberInput input {
    background: #f7f7f7 !important;
    border: 1px solid #e8e8e8 !important;
    border-radius: 6px !important;
    color: #1a1a1a !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #1a1a1a !important;
    background: #fff !important;
    box-shadow: none !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #f7f7f7 !important;
    border: 1px solid #e8e8e8 !important;
    border-radius: 6px !important;
    font-size: 0.9rem !important;
}

.hint {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #ccc;
    margin-top: -10px;
    margin-bottom: 14px;
}

.cost-strip {
    background: #f7f7f7;
    border-radius: 8px;
    padding: 16px 18px;
    margin-top: 6px;
}
.cost-strip .cs-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em; color: #888; margin-bottom: 4px; font-weight: 600; }
.cost-strip .cs-inr { font-family: 'IBM Plex Mono', monospace; font-size: 1.6rem; font-weight: 500; color: #1a1a1a; line-height: 1.1; }
.cost-strip .cs-aed { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #aaa; margin-top: 3px; }

hr { border: none; border-top: 1px solid #ebebeb !important; margin: 24px 0 !important; }

[data-testid="stMetric"] {
    background: #f7f7f7 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 16px 18px !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #888 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.35rem !important;
    font-weight: 500 !important;
    color: #1a1a1a !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

.stButton > button[kind="primary"] {
    background: #1a1a1a !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    transition: opacity 0.15s !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.75 !important; }

.stButton > button[kind="secondary"] {
    background: #fff !important;
    color: #1a1a1a !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stButton > button[kind="secondary"]:hover { border-color: #1a1a1a !important; }

.stDownloadButton > button {
    background: #fff !important;
    color: #1a1a1a !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    width: 100% !important;
}
.stDownloadButton > button:hover { border-color: #1a1a1a !important; }

[data-testid="stDataFrame"] {
    border: 1px solid #ebebeb !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

div[data-testid="stSuccess"] { background: #f2faf5 !important; border: 1px solid #c3e6cb !important; border-radius: 6px !important; color: #276740 !important; }
div[data-testid="stInfo"]    { background: #f7f7f7 !important; border: 1px solid #e0e0e0 !important; border-radius: 6px !important; color: #555 !important; }

h2, h3 { font-weight: 600 !important; color: #1a1a1a !important; letter-spacing: -0.01em !important; }
</style>
""", unsafe_allow_html=True)

# ── Init ──
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(columns=[
        'Date','Sale ID','Customer','Item','Channel','Payment','Status',
        'Quantity','Cost (INR)','Sale (AED)','Profit (INR)','Margin %'
    ])
if 'tab' not in st.session_state:
    st.session_state.tab = "calc"

def get_rate():
    try:
        return requests.get("https://api.exchangerate-api.com/v4/latest/AED").json()['rates']['INR']
    except:
        return 22.75

rate = get_rate()

# ── Top bar ──
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">Indo-UAE Trade Pro</div>
    <div class="topbar-right">1 AED = <span>₹{rate:.2f}</span> &nbsp;·&nbsp; live</div>
</div>
""", unsafe_allow_html=True)

# ── Tab row ──
tb1, tb2, _gap = st.columns([1.2, 1.2, 7.6])
with tb1:
    if st.button("Calculator & Log",
                 type="primary" if st.session_state.tab == "calc" else "secondary",
                 use_container_width=True):
        st.session_state.tab = "calc"; st.rerun()
with tb2:
    if st.button("Bookkeeping",
                 type="primary" if st.session_state.tab == "book" else "secondary",
                 use_container_width=True):
        st.session_state.tab = "book"; st.rerun()

st.markdown("<hr style='margin:16px 0 28px'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CALCULATOR
# ══════════════════════════════════════════════
if st.session_state.tab == "calc":

    st.markdown("<div class='lbl'>Order Details</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        sale_id  = st.text_input("Invoice ID", value=f"INV-{len(st.session_state.sales_data)+1:03d}")
        customer = st.text_input("Customer", placeholder="e.g. Aisha M.")
    with c2:
        item_name = st.text_input("Item", placeholder="e.g. Green Silk Kurti")
        channel   = st.selectbox("Channel", ["WhatsApp","Instagram","In-Person","Website","Other"])
    with c3:
        payment = st.selectbox("Payment", ["Cash","Bank Transfer","Payment Link","Other"])
        status  = st.selectbox("Status",  ["Delivered","Shipped (Transit)","Pending"])

    st.markdown("<hr>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='lbl'>Costs — INR</div>", unsafe_allow_html=True)
        quantity   = st.number_input("Quantity", min_value=1, step=1, value=1)
        buy_price  = st.number_input("Purchase Price (per item) (INR)", min_value=0.0, step=100.0)
        st.markdown(f"<div class='hint'>≈ {(buy_price * quantity)/rate:.2f} AED (Total Items)</div>", unsafe_allow_html=True)
        
        ship_price = st.number_input("Shipping / Packaging (Total INR)", min_value=0.0, step=50.0)
        st.markdown(f"<div class='hint'>≈ {ship_price/rate:.2f} AED</div>", unsafe_allow_html=True)

        total_cost = (buy_price * quantity) + ship_price
        st.markdown(f"""
        <div class="cost-strip">
            <div class="cs-label">Total Cost</div>
            <div class="cs-inr">₹{total_cost:,.2f}</div>
            <div class="cs-aed">≈ {total_cost/rate:.2f} AED</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='lbl'>Revenue — AED</div>", unsafe_allow_html=True)
        
        # --- NEW: Sale price is now PER ITEM ---
        unit_sale_aed = st.number_input("Sale Price (per item) (AED)", min_value=0.0, step=10.0)
        
        # Multiply by quantity to get total AED revenue
        total_sale_aed = unit_sale_aed * quantity
        
        # The hint now shows the Total AED and Total INR
        st.markdown(f"<div class='hint'>Total: {total_sale_aed:,.2f} AED ≈ ₹{total_sale_aed*rate:,.2f}</div>", unsafe_allow_html=True)
        
        revenue_inr = total_sale_aed * rate
        profit      = revenue_inr - total_cost
        margin      = (profit / revenue_inr * 100) if revenue_inr > 0 else 0

    st.markdown("<hr>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Investment", f"₹{total_cost:,.2f}")
    m2.metric("Net Profit (INR)", f"₹{profit:,.2f}", delta=f"{margin:.1f}% margin")
    m3.metric("Net Profit (AED)", f"{profit/rate:.2f} د.إ")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Record Sale →", use_container_width=True, type="primary"):
        entry = {
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'Sale ID': sale_id, 'Customer': customer or "Unknown",
            'Item': item_name or "Unnamed", 'Channel': channel,
            'Payment': payment, 'Status': status, 'Quantity': quantity,
            'Cost (INR)': total_cost, 
            'Sale (AED)': total_sale_aed, # Records the TOTAL AED amount to keep the bookkeeping revenue accurate
            'Profit (INR)': profit, 'Margin %': round(margin, 2)
        }
        st.session_state.sales_data = pd.concat(
            [st.session_state.sales_data, pd.DataFrame([entry])], ignore_index=True
        )
        st.success(f"{sale_id} logged successfully.")


# ══════════════════════════════════════════════
# BOOKKEEPING
# ══════════════════════════════════════════════
else:
    if st.session_state.sales_data.empty:
        st.info("No sales yet. Use the Calculator tab to log your first sale.")
    else:
        df = st.session_state.sales_data.copy()
        df['Date'] = pd.to_datetime(df['Date'])

        st.markdown("<div class='lbl'>Overview</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenue",    f"₹{(df['Sale (AED)']*rate).sum():,.0f}")
        c2.metric("Profit",     f"₹{df['Profit (INR)'].sum():,.0f}")
        c3.metric("Avg Margin", f"{df['Margin %'].mean():.1f}%")
        c4.metric("Items Sold", str(df['Quantity'].sum()))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='lbl'>Sales Log</div>", unsafe_allow_html=True)

        st.dataframe(
            df.sort_values('Date', ascending=False),
            use_container_width=True, hide_index=True,
            column_config={
                "Date":         st.column_config.DatetimeColumn("Date", format="DD MMM YYYY, HH:mm"),
                "Quantity":     st.column_config.NumberColumn("Qty"),
                "Profit (INR)": st.column_config.NumberColumn(format="₹%.2f"),
                "Sale (AED)":   st.column_config.NumberColumn(format="%.2f د.إ"),
                "Cost (INR)":   st.column_config.NumberColumn(format="₹%.2f"),
                "Margin %":     st.column_config.NumberColumn(format="%.1f%%"),
            }
        )

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='lbl'>Manage</div>", unsafe_allow_html=True)

        opts = [
            f"{i}  ·  [{r['Sale ID']}]  {r['Quantity']}x {r['Item']}  —  {r['Customer']}  ({r['Sale (AED)']} AED Total)"
            for i, r in df.iterrows()
        ]
        d1, d2 = st.columns([5, 1])
        with d1:
            sel = st.selectbox("Record", opts, label_visibility="collapsed")
        with d2:
            if st.button("Delete", type="primary", use_container_width=True):
                idx = int(sel.split("·")[0].strip())
                st.session_state.sales_data = (
                    st.session_state.sales_data.drop(idx).reset_index(drop=True)
                )
                st.success("Deleted.")
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        e1, e2 = st.columns(2)
        with e1:
            st.download_button("↓  Export CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="indo_uae_sales.csv", mime="text/csv",
                use_container_width=True)
        with e2:
            if st.button("Clear All Records", use_container_width=True):
                st.session_state.sales_data = pd.DataFrame(columns=st.session_state.sales_data.columns)
                st.rerun()
