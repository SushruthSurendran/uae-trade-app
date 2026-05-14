import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Indo-UAE Trade Pro", layout="wide")

# Minimalistic CSS for mobile optimization
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- DATA INITIALIZATION ---
if 'sales_data' not in st.session_state:
    # Initialize empty dataframe with columns
    st.session_state.sales_data = pd.DataFrame(columns=[
        'Date', 'Item Name', 'Cost (INR)', 'Sale (AED)', 'Profit (INR)', 'Margin %'
    ])

# --- HELPER FUNCTIONS ---
def get_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/AED"
        return requests.get(url).json()['rates']['INR']
    except:
        return 22.75 # Default fallback

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("📊 Menu")
page = st.sidebar.radio("Go to", ["Calculator & Log", "Bookkeeping & Analytics"])
rate = get_rate()
st.sidebar.metric("Live AED ➔ INR", f"₹{rate:.2f}")

# --- PAGE 1: CALCULATOR & LOGGING ---
if page == "Calculator & Log":
    st.header("🛒 New Sale Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Costing (INR)")
        item_name = st.text_input("Item Label", placeholder="e.g., Silk Saree A1")
        buy_price = st.number_input("Purchase Price", min_value=0.0, step=100.0)
        ship_price = st.number_input("Shipping / Packaging", min_value=0.0, step=50.0)
        customs = st.number_input("Customs / Misc", min_value=0.0, step=10.0)
        total_cost = buy_price + ship_price + customs

    with col2:
        st.subheader("Sale (AED)")
        sale_aed = st.number_input("Sale Price in UAE", min_value=0.0, step=10.0)
        revenue_inr = sale_aed * rate
        profit = revenue_inr - total_cost
        margin = (profit / revenue_inr * 100) if revenue_inr > 0 else 0

    st.divider()
    
    # Results Dashboard
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Cost (INR)", f"₹{total_cost:,.2f}")
    m2.metric("Net Profit (INR)", f"₹{profit:,.2f}", delta=f"{margin:.1f}%")
    m3.metric("Profit (AED)", f"{profit/rate:.2f} د.إ")

    # The "Integrator" Button
    if st.button("✅ Record Sale to Bookkeeping", use_container_width=True):
        new_entry = {
            'Date': datetime.now().strftime("%Y-%m-%d"),
            'Item Name': item_name if item_name else "Unnamed Item",
            'Cost (INR)': total_cost,
            'Sale (AED)': sale_aed,
            'Profit (INR)': profit,
            'Margin %': round(margin, 2)
        }
        st.session_state.sales_data = pd.concat([st.session_state.sales_data, pd.DataFrame([new_entry])], ignore_index=True)
        st.success(f"Logged {item_name} successfully!")

# --- PAGE 2: BOOKKEEPING & ANALYTICS ---
else:
    st.header("📈 Sales Records")
    
    if st.session_state.sales_data.empty:
        st.info("No sales recorded yet. Head to the Calculator to add some!")
    else:
        df = st.session_state.sales_data.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.strftime('%B %Y')

        # --- SUMMARY SECTION ---
        total_rev = (df['Sale (AED)'] * rate).sum()
        total_prof = df['Profit (INR)'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Lifetime Revenue", f"₹{total_rev:,.0f}")
        c2.metric("Lifetime Profit", f"₹{total_prof:,.0f}")
        c3.metric("Total Items Sold", len(df))

        # --- MONTHLY BREAKDOWN ---
        st.subheader("Monthly Earnings")
        monthly_stats = df.groupby('Month')['Profit (INR)'].sum().reset_index()
        st.bar_chart(monthly_stats.set_index('Month'))

        # --- DATA TABLE ---
        st.subheader("Detailed Logs")
        st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

        # Download Option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Records as CSV", data=csv, file_name="sales_records.csv", mime="text/csv")

        if st.button("🗑️ Clear All Records"):
            st.session_state.sales_data = pd.DataFrame(columns=st.session_state.sales_data.columns)
            st.rerun()
