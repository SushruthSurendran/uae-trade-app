import streamlit as st
import requests

# App Configuration
st.set_page_config(page_title="Indo-UAE Trade Companion", layout="centered")

def get_exchange_rate():
    # Using a free API for real-time rates
    url = "https://api.exchangerate-api.com/v4/latest/AED"
    try:
        response = requests.get(url)
        data = response.json()
        return data['rates']['INR']
    except:
        return 22.70  # Fallback rate

st.title("🧵 Indo-UAE Apparel Calc")
st.markdown("---")

# --- 1. Currency Section ---
rate = get_exchange_rate()
st.metric(label="Current Rate (1 AED to INR)", value=f"₹{rate:.2f}")

# --- 2. Cost Inputs (INR) ---
with st.expander("Step 1: Indian Costs (INR)", expanded=True):
    item_cost = st.number_input("Item Purchase Price (INR)", min_value=0.0, step=100.0)
    shipping_inr = st.number_input("Shipping & Logistics (INR)", min_value=0.0, step=50.0)
    customs_misc = st.number_input("Customs & Other Fees (INR)", min_value=0.0, step=10.0)
    
    total_cost_inr = item_cost + shipping_inr + customs_misc
    st.info(f"Total Investment: ₹{total_cost_inr:,.2f}")

# --- 3. Sales Inputs (AED) ---
with st.expander("Step 2: UAE Sale Price (AED)", expanded=True):
    sale_price_aed = st.number_input("Selling Price in Dubai (AED)", min_value=0.0, step=5.0)
    revenue_inr = sale_price_aed * rate

# --- 4. Profit Analysis ---
st.markdown("### 📊 Business Summary")
profit_inr = revenue_inr - total_cost_inr

if sale_price_aed > 0:
    margin = (profit_inr / revenue_inr) * 100
else:
    margin = 0.0

col1, col2 = st.columns(2)
with col1:
    st.metric("Net Profit (INR)", f"₹{profit_inr:,.2f}", delta=f"{margin:.1f}% Margin")
with col2:
    profit_aed = profit_inr / rate
    st.metric("Net Profit (AED)", f"{profit_aed:.2f} د.إ")

# --- 5. Insights ---
if profit_inr > 0:
    st.success(f"Nice! You are making ₹{profit_inr:,.2f} per unit.")
elif profit_inr < 0:
    st.error(f"Warning: Loss of ₹{abs(profit_inr):,.2f} at this price point.")

# Break-even calculation
break_even_aed = total_cost_inr / rate
st.write(f"**Break-even Price:** {break_even_aed:.2f} AED")
