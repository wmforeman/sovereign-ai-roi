import streamlit as st
import json
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Sovereign AI ROI Calculator", 
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS to make the UI pop
st.markdown("""
    <style>
    .metric-container {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        with open('hardware_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

hardware_list = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("1. Your Cloud Bill")
    cloud_cost = st.number_input(
        "Monthly AI Subscription/API Cost ($)", 
        value=200, 
        step=20,
        help="Total spent on ChatGPT Plus, Claude Pro, Midjourney, or API credits per month."
    )
    
    st.subheader("2. Your Environment")
    kwh_cost = st.number_input(
        "Electricity Cost ($/kWh)", 
        value=0.18, 
        format="%.2f",
        help="Check your utility bill. Average US rate is $0.16. California is ~$0.32."
    )
    
    st.info("📝 **Note:** This tool assumes you run the hardware 24/7. Actual savings may be higher if you turn it off!")

# --- MAIN APP ---
st.title("🛡️ Sovereign AI ROI Calculator")
st.markdown("### Stop renting intelligence. Own the hardware.")

# Introduction Expander
with st.expander("🤔 How does this work?"):
    st.write("""
    1. Enter your current **monthly spend** on AI tools in the sidebar.
    2. Select a **Local Hardware** option below.
    3. See exactly how many months it takes for the hardware to pay for itself.
    """)

st.divider()

# --- HARDWARE SELECTION ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Select Your Local 'Stack'")
    
    hardware_titles = [item['title'] for item in hardware_list]
    selected_title = st.selectbox("Choose Hardware Node:", hardware_titles)
    
    # Get selected item details
    item = next(i for i in hardware_list if i['title'] == selected_title)
    hardware_cost = float(item['price'].replace("$","").replace(",",""))
    
    st.image(item['image'], use_container_width=True)
    
    st.caption(f"**Best For:** {item.get('description', 'General AI Workloads')}")
    
    st.markdown(f"""
    <div style="background-color:#262730; padding:15px; border-radius:10px; text-align:center;">
        <h3 style="margin:0; color:#4CAF50;">{item['price']}</h3>
        <p style="margin:0; font-size:0.8em; color:#aaa;">Hardware Cost</p>
        <br>
        <a href="{item['link']}" target="_blank" style="background-color:#FF9900; color:black; padding:10px 20px; text-decoration:none; border-radius:5px; font-weight:bold;">👉 Check Price on Amazon</a>
    </div>
    """, unsafe_allow_html=True)

# --- CALCULATIONS ---
watts_usage = 450 # Avg for 4090 under load
monthly_power_cost = (watts_usage / 1000) * 24 * 30 * kwh_cost
monthly_cloud_burn = cloud_cost

# Avoid divide by zero
savings_per_month = monthly_cloud_burn - monthly_power_cost
if savings_per_month <= 0:
    break_even_months = 999
else:
    break_even_months = hardware_cost / savings_per_month

# --- RESULTS COLUMN ---
with col_right:
    st.subheader("💸 Financial Analysis")
    
    # 1. Metric Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Monthly Cloud Cost", f"${monthly_cloud_burn}", delta="Expense", delta_color="inverse")
    m2.metric("Est. Monthly Power", f"${monthly_power_cost:.2f}", delta="OpEx", delta_color="off")
    m3.metric("Net Monthly Savings", f"${savings_per_month:.2f}", delta="Profit", delta_color="normal")
    
    st.divider()
    
    # 2. The Verdict
    if break_even_months < 24:
        st.success(f"✅ **ROI Positive:** This setup pays for itself in **{break_even_months:.1f} Months**.")
    else:
        st.warning(f"⚠️ **Long Term Hold:** Break-even is **{break_even_months:.1f} Months**. Consider cheaper hardware or waiting for price drops.")

    # 3. Visualization (The "Crossover" Chart)
    st.subheader("📈 The Break-Even Chart")
    
    # Create projection data for 36 months
    months = list(range(1, 37))
    cloud_cumulative = [monthly_cloud_burn * m for m in months]
    local_cumulative = [hardware_cost + (monthly_power_cost * m) for m in months]
    
    chart_data = pd.DataFrame({
        "Month": months,
        "Cloud Rent (Cumulative)": cloud_cumulative,
        "Local Ownership (Cumulative)": local_cumulative
    })
    
    st.line_chart(
        chart_data, 
        x="Month", 
        y=["Cloud Rent (Cumulative)", "Local Ownership (Cumulative)"],
        color=["#FF4B4B", "#00FF00"]  # Red for Cloud (Burn), Green for Local (Asset)
    )
    st.caption("Where the green line crosses below the red line = You are making profit.")
