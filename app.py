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
    /* Make the conversion captions pop a bit more */
    .conversion-text {
        color: #888888;
        font-size: 0.85rem;
        margin-top: -10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA INITIALIZATION ---
if 'sales_data' not in st.session_state:
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
        
        buy_price = st.number_input("Purchase Price (INR)", min_value=0.0, step=100.0)
        st.markdown(f"<div class='conversion-text'>🔄 ≈ {(buy_price / rate):.2f} AED</div>", unsafe_allow_html=True)
        
        ship_price = st.number_input("Shipping / Packaging (INR)", min_value=0.0, step=50.0)
        st.markdown(f"<div class='conversion-text'>🔄 ≈ {(ship_price / rate):.2f} AED</div>", unsafe_allow_html=True)
        
        customs = st.number_input("Customs / Misc (INR)", min_value=0.0, step=10.0)
        st.markdown(f"<div class='conversion-text'>🔄 ≈ {(customs / rate):.2f} AED</div>", unsafe_allow_html=True)
        
        total_cost = buy_price + ship_price + customs

    with col2:
        st.subheader("Sale (AED)")
        
        sale_aed = st.number_input("Sale Price in UAE (AED)", min_value=0.0, step=10.0)
        st.markdown(f"<div class='conversion-text'>🔄 ≈ ₹{(sale_aed * rate):,.2f}</div>", unsafe_allow_html=True)
        
        revenue_inr = sale_aed * rate
        profit = revenue_inr - total_cost
        margin = (profit / revenue_inr * 100) if revenue_inr > 0 else 0

    st.divider()
    
    # Results Dashboard
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Cost (INR)", f"₹{total_cost:,.2f}")
    m2.metric("Net Profit (INR)", f"₹{profit:,.2f}", delta=f"{margin:.1f}% Margin")
    m3.metric("Profit (AED)", f"{profit/rate:.2f} د.إ")

    # The "Integrator" Button
    if st.button("✅ Record Sale to Bookkeeping", use_container_width=True):
        new_entry = {
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M"), # Added time for uniqueness
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

        # --- DATA TABLE ---
        st.subheader("Detailed Logs")
        st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

        # --- MANAGE / DELETE RECORDS ---
        st.divider()
        st.subheader("🗑️ Manage Records")
        
        # Create a formatted list of options for the dropdown
        # e.g., "0: Silk Saree A1 - 150 AED (2026-05-14)"
        delete_options = [f"{i}: {row['Item Name']} - {row['Sale (AED)']} AED ({row['Date'].strftime('%Y-%m-%d')})" for i, row in df.iterrows()]
        
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            selected_to_delete = st.selectbox("Select a specific record to delete:", delete_options)
        with col_del2:
            st.write("") # Spacing to align button with dropdown
            st.write("")
            if st.button("Delete Specific Record", type="primary"):
                if selected_to_delete:
                    # Extract the index (the number before the colon)
                    idx_to_drop = int(selected_to_delete.split(":")[0])
                    # Drop from the session state dataframe
                    st.session_state.sales_data = st.session_state.sales_data.drop(idx_to_drop).reset_index(drop=True)
                    st.success("Record deleted successfully!")
                    st.rerun()

        # Download & Wipe All Options
        st.divider()
        c_dl, c_wipe = st.columns(2)
        with c_dl:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Records as CSV", data=csv, file_name="sales_records.csv", mime="text/csv", use_container_width=True)
        with c_wipe:
            if st.button("⚠️ Clear ALL Records", use_container_width=True):
                st.session_state.sales_data = pd.DataFrame(columns=st.session_state.sales_data.columns)
                st.rerun()
