import streamlit as st
import json
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Sovereign AI ROI Calculator", 
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for UI polish
st.markdown("""
    <style>
    .metric-container {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        with open('hardware_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

all_hardware = load_data()

# Filter data into categories
compute_options = [item for item in all_hardware if item.get('category') == 'compute']
storage_options = [item for item in all_hardware if item.get('category') == 'storage']

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("1. Your Cloud Bill")
    cloud_cost = st.number_input(
        "Monthly Cloud Spend ($)", 
        value=200, 
        step=20,
        help="Total spent on ChatGPT Plus, Claude, Midjourney, or API credits."
    )
    
    st.subheader("2. Your Environment")
    kwh_cost = st.number_input(
        "Electricity Rate ($/kWh)", 
        value=0.18, 
        format="%.2f",
        help="Check your utility bill. Average US rate is ~$0.16."
    )
    st.markdown("[Find your local rate ↗](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a)", unsafe_allow_html=True)
    
    st.divider()
    st.caption("v3.0 - Sovereign Builder Edition")

# --- MAIN PAGE INTRO ---
st.title("🛡️ Sovereign AI ROI Calculator")

st.info("""
**What is this tool?** This calculator helps you decide if you should **Rent** AI (Cloud APIs) or **Own** AI (Local Hardware).  
By inputting your monthly cloud spend and building a virtual 'Local Stack' below, you can see exactly how many months it takes for the hardware to pay for itself.
""")

st.divider()

# --- HARDWARE BUILDER ---
st.subheader("🛠️ Build Your Local Stack")

col1, col2 = st.columns([1, 1])

# Column 1: Compute (The Brain)
with col1:
    st.markdown("### 1. Select Compute Node")
    compute_titles = [item['title'] for item in compute_options]
    selected_compute_title = st.selectbox("Choose GPU/System:", compute_titles)
    
    # Get Compute Details
    compute_item = next(i for i in compute_options if i['title'] == selected_compute_title)
    
    st.caption(f"**Specs:** {compute_item.get('description')}")
    st.write(f"**Watts:** {compute_item['watts']}W | **Price:** ${compute_item['price']:,.2f}")

# Column 2: Storage (The Body)
with col2:
    st.markdown("### 2. Add Storage")
    storage_titles = [item['title'] for item in storage_options]
    selected_storage_title = st.selectbox("Choose Storage Drive:", storage_titles)
    
    # Get Storage Details
    storage_item = next(i for i in storage_options if i['title'] == selected_storage_title)
    
    if storage_item['price'] > 0:
        st.caption(f"**Specs:** {storage_item.get('description')}")
        st.write(f"**Watts:** {storage_item['watts']}W | **Price:** ${storage_item['price']:,.2f}")

# Calculate Totals
total_hardware_cost = compute_item['price'] + storage_item['price']
total_watts = compute_item['watts'] + storage_item['watts']
monthly_power_cost = (total_watts / 1000) * 24 * 30 * kwh_cost

st.divider()

# --- FINANCIAL RESULTS ---
st.subheader("💸 Financial Analysis")

results_col1, results_col2, results_col3 = st.columns(3)

# Metrics
results_col1.metric("Total Build Cost", f"${total_hardware_cost:,.2f}", delta="One-time Capex", delta_color="inverse")
results_col2.metric("Monthly Power Cost", f"${monthly_power_cost:.2f}", delta="Recurring Opex", delta_color="off")

# ROI Math
monthly_savings = cloud_cost - monthly_power_cost
if monthly_savings <= 0:
    break_even_months = 999
    results_col3.metric("Net Monthly Savings", f"${monthly_savings:.2f}", delta="Negative ROI", delta_color="inverse")
    st.error(f"⚠️ **Not Profitable:** Your power costs (${monthly_power_cost:.2f}) exceed your cloud budget (${cloud_cost}). You need cheaper power or a smaller rig.")
else:
    break_even_months = total_hardware_cost / monthly_savings
    results_col3.metric("Net Monthly Savings", f"${monthly_savings:.2f}", delta="Profit", delta_color="normal")
    
    if break_even_months < 18:
        st.success(f"✅ **Great Investment:** This build pays for itself in **{break_even_months:.1f} Months**.")
    else:
        st.warning(f"⚖️ **Long Term Play:** Break-even is **{break_even_months:.1f} Months**.")

# --- CHART ---
st.subheader("📈 The Break-Even Chart")
months = list(range(1, 37))
cloud_cum = [cloud_cost * m for m in months]
local_cum = [total_hardware_cost + (monthly_power_cost * m) for m in months]

chart_df = pd.DataFrame({
    "Month": months,
    "Cloud Rent (Burned)": cloud_cum,
    "Local Hardware (Owned)": local_cum
})

st.line_chart(
    chart_df, 
    x="Month", 
    y=["Cloud Rent (Burned)", "Local Hardware (Owned)"],
    color=["#FF4B4B", "#00FF00"]
)

# --- BUY BUTTONS ---
st.subheader("🛒 Ready to Build?")
b1, b2 = st.columns(2)
with b1:
    st.link_button(f"Buy {compute_item['title']} on Amazon", compute_item['link'])
with b2:
    if storage_item['price'] > 0:
        st.link_button(f"Buy {storage_item['title']} on Amazon", storage_item['link'])
