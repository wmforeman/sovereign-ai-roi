import streamlit as st
import json
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Sovereign AI ROI Calculator", 
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
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

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        with open('hardware_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

systems = load_data()

# --- SIDEBAR ---
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
        help="Average US rate is ~$0.16. California is ~$0.32."
    )
    st.markdown("[Find your local rate ↗](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a)")
    
    st.divider()
    st.caption("v4.0 - Systems Edition")

# --- MAIN PAGE ---
st.title("🛡️ Sovereign AI ROI Calculator")

st.info("""
**Rent vs. Buy:** This tool compares the cost of renting AI (OpenAI/Anthropic) vs. building your own **Private AI Lab**.
Select a system below to see how fast it pays for itself.
""")

st.divider()

# --- SYSTEM SELECTOR ---
st.subheader("🖥️ Choose Your Sovereign System")

col_left, col_right = st.columns([1, 1])

with col_left:
    system_titles = [item['title'] for item in systems]
    selected_system = st.selectbox("Select a Turnkey Rig:", system_titles)
    
    # Get Details
    item = next(i for i in systems if i['title'] == selected_system)
    
    st.markdown(f"#### {item['title']}")
    st.caption(f"**Best For:** {item.get('description')}")
    st.write(f"**Power Draw:** {item['watts']}W | **Est. Price:** ${item['price']:,.2f}")
    
    st.link_button(f"👉 Check Price / Buy on Amazon", item['link'])

# --- FINANCIAL MATH ---
monthly_power_cost = (item['watts'] / 1000) * 24 * 30 * kwh_cost
monthly_savings = cloud_cost - monthly_power_cost

if monthly_savings <= 0:
    break_even_months = 999
else:
    break_even_months = item['price'] / monthly_savings

# --- RESULTS ---
with col_right:
    st.markdown("### 💸 ROI Analysis")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("System Cost", f"${item['price']:,.0f}", delta="One-time", delta_color="inverse")
    r2.metric("Monthly Power", f"${monthly_power_cost:.2f}", delta="Recurring", delta_color="off")
    
    if monthly_savings > 0:
        r3.metric("Monthly Savings", f"${monthly_savings:.2f}", delta="Profit", delta_color="normal")
        
        if break_even_months < 12:
            st.success(f"✅ **Instant Win:** Pays off in **{break_even_months:.1f} Months**.")
        elif break_even_months < 24:
            st.info(f"⚖️ **Solid Investment:** Pays off in **{break_even_months:.1f} Months**.")
        else:
            st.warning(f"⏳ **Long Game:** Pays off in **{break_even_months:.1f} Months**.")
    else:
        r3.metric("Net Loss", f"${monthly_savings:.2f}", delta="Negative", delta_color="inverse")
        st.error("⚠️ **Not Profitable:** Your power costs are higher than your cloud budget.")

# --- CHART ---
st.divider()
st.subheader("📈 The Break-Even Chart")

months = list(range(1, 37))
cloud_cum = [cloud_cost * m for m in months]
local_cum = [item['price'] + (monthly_power_cost * m) for m in months]

chart_df = pd.DataFrame({
    "Month": months,
    "Cloud Rent (Burned)": cloud_cum,
    "Private AI (Asset)": local_cum
})

st.line_chart(
    chart_df, 
    x="Month", 
    y=["Cloud Rent (Burned)", "Private AI (Asset)"],
    color=["#FF4B4B", "#00FF00"]
)
