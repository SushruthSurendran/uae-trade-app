import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Indo-UAE Trade Pro", layout="wide", initial_sidebar_state="expanded")

# --- GLOBAL STYLES ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── App background ── */
.stApp {
    background-color: #0f1117;
    color: #e8eaf0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #252d3d;
}
[data-testid="stSidebar"] .stRadio > label {
    color: #8a94a8 !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 8px 12px;
    color: #b0bac8 !important;
    font-size: 0.9rem;
    transition: all 0.15s ease;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(196, 161, 97, 0.08);
    border-color: rgba(196, 161, 97, 0.2);
    color: #c4a161 !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-testid*="selected"],
[data-testid="stSidebar"] .stRadio input:checked + div {
    background: rgba(196, 161, 97, 0.12) !important;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    padding: 8px 4px 24px;
    border-bottom: 1px solid #252d3d;
    margin-bottom: 24px;
}
.sidebar-brand h2 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e8eaf0;
    margin: 0;
    letter-spacing: -0.01em;
}
.sidebar-brand p {
    font-size: 0.72rem;
    color: #8a94a8;
    margin: 2px 0 0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Live rate badge ── */
.rate-badge {
    background: linear-gradient(135deg, rgba(196,161,97,0.15), rgba(196,161,97,0.05));
    border: 1px solid rgba(196, 161, 97, 0.3);
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 20px;
}
.rate-badge .label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #8a94a8;
    margin-bottom: 3px;
}
.rate-badge .value {
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem;
    font-weight: 500;
    color: #c4a161;
}
.rate-badge .sub {
    font-size: 0.7rem;
    color: #8a94a8;
    margin-top: 2px;
}

/* ── Page header ── */
.page-header {
    padding: 6px 0 28px;
    border-bottom: 1px solid #252d3d;
    margin-bottom: 28px;
}
.page-header h1 {
    font-size: 1.6rem;
    font-weight: 600;
    color: #e8eaf0;
    margin: 0 0 4px;
    letter-spacing: -0.02em;
}
.page-header p {
    font-size: 0.85rem;
    color: #8a94a8;
    margin: 0;
}

/* ── Section label ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8a94a8;
    margin: 0 0 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #252d3d;
}

/* ── Card ── */
.card {
    background: #161b27;
    border: 1px solid #252d3d;
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 16px;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    background-color: #1e2535 !important;
    border: 1px solid #2e3749 !important;
    border-radius: 7px !important;
    color: #e8eaf0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #c4a161 !important;
    box-shadow: 0 0 0 2px rgba(196,161,97,0.15) !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label {
    color: #8a94a8 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    margin-bottom: 4px !important;
}

/* ── Conversion hint ── */
.conv-hint {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #5a6478;
    margin-top: -8px;
    margin-bottom: 10px;
    padding-left: 2px;
}

/* ── Total cost panel ── */
.cost-panel {
    background: linear-gradient(135deg, #1a1f2e, #161b27);
    border: 1px solid #2e3749;
    border-left: 3px solid #c4a161;
    border-radius: 8px;
    padding: 16px 18px;
    margin-top: 8px;
}
.cost-panel .cp-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8a94a8;
    margin-bottom: 6px;
    font-weight: 600;
}
.cost-panel .cp-inr {
    font-family: 'DM Mono', monospace;
    font-size: 2rem;
    font-weight: 500;
    color: #e8eaf0;
    line-height: 1;
}
.cost-panel .cp-aed {
    font-family: 'DM Mono', monospace;
    font-size: 0.9rem;
    color: #8a94a8;
    margin-top: 4px;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #161b27 !important;
    border: 1px solid #252d3d !important;
    border-radius: 10px !important;
    padding: 18px 20px !important;
}
[data-testid="stMetricLabel"] {
    color: #8a94a8 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    color: #e8eaf0 !important;
    font-size: 1.5rem !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* ── Primary button ── */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #c4a161, #a8874a) !important;
    border: none !important;
    color: #0f1117 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.02em !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    transition: all 0.15s ease !important;
}
.stButton button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── Secondary button ── */
.stButton button[kind="secondary"] {
    background: #1e2535 !important;
    border: 1px solid #2e3749 !important;
    color: #b0bac8 !important;
    font-size: 0.88rem !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr {
    border-color: #252d3d !important;
    margin: 20px 0 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #252d3d !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── Alerts ── */
.stSuccess {
    background: rgba(72, 187, 120, 0.08) !important;
    border: 1px solid rgba(72, 187, 120, 0.25) !important;
    border-radius: 8px !important;
    color: #68d391 !important;
}
.stInfo {
    background: rgba(99, 179, 237, 0.08) !important;
    border: 1px solid rgba(99, 179, 237, 0.2) !important;
    border-radius: 8px !important;
}

/* ── Download button ── */
.stDownloadButton button {
    background: #1e2535 !important;
    border: 1px solid #2e3749 !important;
    color: #b0bac8 !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    width: 100% !important;
}
.stDownloadButton button:hover {
    border-color: #c4a161 !important;
    color: #c4a161 !important;
}

/* ── Selectbox dropdown ── */
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #1e2535 !important;
}

/* ── Subheader ── */
h2, h3 {
    color: #e8eaf0 !important;
    font-weight: 600 !important;
    letter-spacing: -0.015em !important;
}
</style>
""", unsafe_allow_html=True)


# --- DATA INITIALIZATION ---
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(columns=[
        'Date', 'Sale ID', 'Customer', 'Item', 'Channel', 'Payment', 'Status',
        'Cost (INR)', 'Sale (AED)', 'Profit (INR)', 'Margin %'
    ])


# --- HELPER ---
def get_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/AED"
        return requests.get(url).json()['rates']['INR']
    except:
        return 22.75


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>Indo-UAE Trade Pro</h2>
        <p>Sales & Bookkeeping</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", ["Calculator & Log", "Bookkeeping & Analytics"], label_visibility="collapsed")

    rate = get_rate()
    st.markdown(f"""
    <div class="rate-badge">
        <div class="label">Live Exchange Rate</div>
        <div class="value">₹{rate:.4f}</div>
        <div class="sub">per 1 AED · Updated now</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 1 — CALCULATOR & LOG
# ══════════════════════════════════════════════
if page == "Calculator & Log":

    st.markdown("""
    <div class="page-header">
        <h1>New Sale Entry</h1>
        <p>Fill in order details and costs to calculate profitability, then log the sale.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── ORDER DETAILS ──
    st.markdown("<p class='section-label'>Order & Customer Details</p>", unsafe_allow_html=True)

    sd1, sd2, sd3 = st.columns(3)
    with sd1:
        default_inv = f"INV-{len(st.session_state.sales_data) + 1:03d}"
        sale_id  = st.text_input("Invoice / Sale ID", value=default_inv)
        customer = st.text_input("Customer Name", placeholder="e.g. Aisha M.")
    with sd2:
        item_name = st.text_input("Item Label", placeholder="e.g. Green Silk Kurti")
        channel   = st.selectbox("Sales Channel", ["WhatsApp", "Instagram", "In-Person", "Website", "Other"])
    with sd3:
        payment = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Payment Link", "Other"])
        status  = st.selectbox("Fulfillment Status", ["Delivered", "Shipped (Transit)", "Pending"])

    st.divider()

    # ── FINANCIALS ──
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<p class='section-label'>Costing  ·  INR</p>", unsafe_allow_html=True)

        buy_price = st.number_input("Purchase Price (INR)", min_value=0.0, step=100.0)
        st.markdown(f"<div class='conv-hint'>≈ {(buy_price / rate):.2f} AED</div>", unsafe_allow_html=True)

        ship_price = st.number_input("Shipping / Packaging (INR)", min_value=0.0, step=50.0)
        st.markdown(f"<div class='conv-hint'>≈ {(ship_price / rate):.2f} AED</div>", unsafe_allow_html=True)

        customs = st.number_input("Customs / Misc (INR)", min_value=0.0, step=10.0)
        st.markdown(f"<div class='conv-hint'>≈ {(customs / rate):.2f} AED</div>", unsafe_allow_html=True)

        total_cost = buy_price + ship_price + customs

        st.markdown(f"""
        <div class="cost-panel">
            <div class="cp-label">Total Cost Price</div>
            <div class="cp-inr">₹{total_cost:,.2f}</div>
            <div class="cp-aed">≈ {(total_cost / rate):.2f} AED</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<p class='section-label'>Revenue  ·  AED</p>", unsafe_allow_html=True)

        sale_aed = st.number_input("Sale Price in UAE (AED)", min_value=0.0, step=10.0)
        st.markdown(f"<div class='conv-hint'>≈ ₹{(sale_aed * rate):,.2f}</div>", unsafe_allow_html=True)

        revenue_inr = sale_aed * rate
        profit  = revenue_inr - total_cost
        margin  = (profit / revenue_inr * 100) if revenue_inr > 0 else 0

    st.divider()

    # ── RESULTS ──
    st.markdown("<p class='section-label'>Profit Summary</p>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Investment", f"₹{total_cost:,.2f}", help="Sum of purchase + shipping + customs in INR")
    m2.metric("Net Profit (INR)", f"₹{profit:,.2f}", delta=f"{margin:.1f}% margin")
    m3.metric("Net Profit (AED)", f"{(profit / rate):.2f} د.إ")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✦  Record Sale to Bookkeeping", use_container_width=True, type="primary"):
        new_entry = {
            'Date':        datetime.now().strftime("%Y-%m-%d %H:%M"),
            'Sale ID':     sale_id,
            'Customer':    customer  if customer  else "Unknown",
            'Item':        item_name if item_name else "Unnamed Item",
            'Channel':     channel,
            'Payment':     payment,
            'Status':      status,
            'Cost (INR)':  total_cost,
            'Sale (AED)':  sale_aed,
            'Profit (INR)': profit,
            'Margin %':    round(margin, 2)
        }
        st.session_state.sales_data = pd.concat(
            [st.session_state.sales_data, pd.DataFrame([new_entry])],
            ignore_index=True
        )
        st.success(f"Sale {sale_id} — {item_name} — logged successfully.")


# ══════════════════════════════════════════════
# PAGE 2 — BOOKKEEPING & ANALYTICS
# ══════════════════════════════════════════════
else:
    st.markdown("""
    <div class="page-header">
        <h1>Bookkeeping & Analytics</h1>
        <p>Lifetime sales records, profit overview, and data management.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.sales_data.empty:
        st.info("No sales recorded yet. Head to the Calculator tab to log your first sale.")
    else:
        df = st.session_state.sales_data.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.strftime('%B %Y')

        total_rev  = (df['Sale (AED)'] * rate).sum()
        total_prof = df['Profit (INR)'].sum()
        avg_margin = df['Margin %'].mean()

        # ── SUMMARY ──
        st.markdown("<p class='section-label'>Lifetime Overview</p>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue",   f"₹{total_rev:,.0f}")
        c2.metric("Total Profit",    f"₹{total_prof:,.0f}")
        c3.metric("Avg. Margin",     f"{avg_margin:.1f}%")
        c4.metric("Items Sold",      str(len(df)))

        st.divider()

        # ── DATA TABLE ──
        st.markdown("<p class='section-label'>Detailed Sales Log</p>", unsafe_allow_html=True)

        st.dataframe(
            df.drop(columns=['Month']).sort_values('Date', ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date":        st.column_config.DatetimeColumn("Date", format="DD MMM YYYY, HH:mm"),
                "Profit (INR)": st.column_config.NumberColumn("Profit (INR)", format="₹%.2f"),
                "Sale (AED)":  st.column_config.NumberColumn("Sale (AED)",   format="%.2f د.إ"),
                "Cost (INR)":  st.column_config.NumberColumn("Cost (INR)",   format="₹%.2f"),
                "Margin %":    st.column_config.NumberColumn("Margin",       format="%.1f%%"),
            }
        )

        st.divider()

        # ── MANAGE RECORDS ──
        st.markdown("<p class='section-label'>Manage Records</p>", unsafe_allow_html=True)

        delete_options = [
            f"{i}:  [{row['Sale ID']}]  {row['Item']}  →  {row['Customer']}  ({row['Sale (AED)']} AED)"
            for i, row in df.iterrows()
        ]

        col_del1, col_del2 = st.columns([4, 1])
        with col_del1:
            selected_to_delete = st.selectbox("Select record to delete", delete_options, label_visibility="collapsed")
        with col_del2:
            if st.button("Delete", type="primary", use_container_width=True):
                if selected_to_delete:
                    idx_to_drop = int(selected_to_delete.split(":")[0])
                    st.session_state.sales_data = (
                        st.session_state.sales_data
                        .drop(idx_to_drop)
                        .reset_index(drop=True)
                    )
                    st.success("Record deleted.")
                    st.rerun()

        st.divider()

        # ── EXPORT / WIPE ──
        st.markdown("<p class='section-label'>Data Export & Reset</p>", unsafe_allow_html=True)

        c_dl, c_wipe = st.columns(2)
        with c_dl:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "↓  Download as CSV",
                data=csv,
                file_name="indo_uae_sales.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_wipe:
            if st.button("⚠  Clear All Records", use_container_width=True):
                st.session_state.sales_data = pd.DataFrame(columns=st.session_state.sales_data.columns)
                st.rerun()
