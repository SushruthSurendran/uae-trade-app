import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Indo-UAE Trade Pro", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetric"] { 
        background-color: rgba(128, 128, 128, 0.1); 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .conversion-text {
        color: #888888;
        font-size: 0.85rem;
        margin-top: -10px;
        margin-bottom: 15px;
    }
    .section-header {
        color: #4CAF50;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .total-cost-box {
        padding: 15px; 
        border-radius: 8px; 
        background-color: rgba(128, 128, 128, 0.15); 
        border-left: 5px solid #ff9800; 
        margin-top: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA INITIALIZATION ---
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame(columns=[
        'Date', 'Sale ID', 'Customer', 'Item', 'Channel', 'Payment', 'Status', 
        'Cost (INR)', 'Sale (AED)', 'Profit (INR)', 'Margin %'
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
    
    # --- SECTION: ORDER DETAILS ---
    st.markdown("<h4 class='section-header'>📝 Order & Customer Details</h4>", unsafe_allow_html=True)
    sd1, sd2, sd3 = st.columns(3)
    
    with sd1:
        default_inv = f"INV-{len(st.session_state.sales_data) + 1:03d}"
        sale_id = st.text_input("Sale Number / Invoice ID", value=default_inv)
        customer = st.text_input("Customer Name", placeholder="e.g., Aisha M.")
        
    with sd2:
        item_name = st.text_input("Item Label", placeholder="e.g., Green Silk Kurti")
        channel = st.selectbox("Sales Channel", ["WhatsApp", "Instagram", "In-Person", "Website", "Other"])
        
    with sd3:
        payment = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Payment Link", "Other"])
        status = st.selectbox("Fulfillment Status", ["Delivered", "Shipped (Transit)", "Pending"])

    st.divider()
    
    # --- SECTION: FINANCIALS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 class='section-header'>📉 Costing (INR)</h4>", unsafe_allow_html=True)
        
        buy_price = st.number_input("Purchase Price (INR)", min_value=0.0, step=100.0)
        st.markdown(f"<div class='conversion-text'>🔄 ≈ {(buy_price / rate):.2f} AED</div>", unsafe_allow_html=True)
        
        ship_price = st.number_input("Shipping / Packaging (INR)", min_value=0.0, step=50.0)
        st.markdown(f"<div class='conversion-text'>🔄 ≈ {(ship_price / rate):.2f} AED</div>", unsafe_allow_html=True)
        
        customs = st.number_input("Customs / Misc (INR)", min_value=0.0, step=10.0)
        st.markdown(f"<div class='conversion-text'>🔄 ≈ {(customs / rate):.2f} AED</div>", unsafe_allow_html=True)
        
        total_cost = buy_price + ship_price + customs
        
        # --- NEW: BIG TOTAL COST DISPLAY ---
        st.markdown(f"""
            <div class="total-cost-box">
                <div style="font-size: 0.9rem; opacity: 0.8; font-weight: 600; margin-bottom: 5px;">TOTAL COST PRICE:</div>
                <div style="line-height: 1.1;">
                    <span style="font-size: 2.2rem; font-weight: 700;">₹{total_cost:,.2f}</span>
                    <span style="font-size: 1.3rem; opacity: 0.7; margin-left: 10px;">(≈ {(total_cost / rate):.2f} AED)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h4 class='section-header'>📈 Sale (AED)</h4>", unsafe_allow_html=True)
        
        sale_aed = st.number_input("Sale Price in UAE (AED)", min_value=0.0, step=10.0)
        st.markdown(f"<div class='conversion-text'>🔄 ≈ ₹{(sale_aed * rate):,.2f}</div>", unsafe_allow_html=True)
        
        revenue_inr = sale_aed * rate
        profit = revenue_inr - total_cost
        margin = (profit / revenue_inr * 100) if revenue_inr > 0 else 0

    st.divider()
    
    # Results Dashboard
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Investment (INR)", f"₹{total_cost:,.2f}")
    m2.metric("Net Profit (INR)", f"₹{profit:,.2f}", delta=f"{margin:.1f}% Margin")
    m3.metric("Profit (AED)", f"{profit/rate:.2f} د.إ")

    # The "Integrator" Button
    if st.button("✅ Record Sale to Bookkeeping", use_container_width=True, type="primary"):
        new_entry = {
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'Sale ID': sale_id,
            'Customer': customer if customer else "Unknown",
            'Item': item_name if item_name else "Unnamed Item",
            'Channel': channel,
            'Payment': payment,
            'Status': status,
            'Cost (INR)': total_cost,
            'Sale (AED)': sale_aed,
            'Profit (INR)': profit,
            'Margin %': round(margin, 2)
        }
        st.session_state.sales_data = pd.concat([st.session_state.sales_data, pd.DataFrame([new_entry])], ignore_index=True)
        st.success(f"Logged {sale_id} ({item_name}) successfully!")

# --- PAGE 2: BOOKKEEPING & ANALYTICS ---
else:
    st.header("📈 Sales Records & Bookkeeping")
    
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

        # --- DATA TABLE ---
        st.subheader("Detailed Logs")
        
        st.dataframe(
            df.sort_values('Date', ascending=False), 
            use_container_width=True,
            column_config={
                "Profit (INR)": st.column_config.NumberColumn(format="₹%.2f"),
                "Sale (AED)": st.column_config.NumberColumn(format="%.2f د.إ"),
                "Cost (INR)": st.column_config.NumberColumn(format="₹%.2f"),
                "Margin %": st.column_config.NumberColumn(format="%.1f%%")
            }
        )

        # --- MANAGE / DELETE RECORDS ---
        st.divider()
        st.subheader("🗑️ Manage Records")
        
        delete_options = [
            f"{i}: [{row['Sale ID']}] {row['Item']} to {row['Customer']} - {row['Sale (AED)']} AED" 
            for i, row in df.iterrows()
        ]
        
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            selected_to_delete = st.selectbox("Select a specific record to delete:", delete_options)
        with col_del2:
            st.write("") 
            st.write("")
            if st.button("Delete Specific Record", type="primary"):
                if selected_to_delete:
                    idx_to_drop = int(selected_to_delete.split(":")[0])
                    st.session_state.sales_data = st.session_state.sales_data.drop(idx_to_drop).reset_index(drop=True)
                    st.success(f"Record deleted successfully!")
                    st.rerun()

        # Download & Wipe All Options
        st.divider()
        c_dl, c_wipe = st.columns(2)
        with c_dl:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Records as CSV", data=csv, file_name="clothing_sales_records.csv", mime="text/csv", use_container_width=True)
        with c_wipe:
            if st.button("⚠️ Clear ALL Records", use_container_width=True):
                st.session_state.sales_data = pd.DataFrame(columns=st.session_state.sales_data.columns)
                st.rerun()
