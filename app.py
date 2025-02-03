import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Set page config
st.set_page_config(page_title="Laser Care Business Analysis", layout="wide")

# Title and description
st.title("Laser Care Business Analysis Dashboard")
st.markdown("Interactive analysis tool for laser care business financials")

# Sidebar - Business Parameters
st.sidebar.header("Business Parameters")

# Startup Costs
st.sidebar.subheader("One-Time Startup Costs")
legal_costs = st.sidebar.number_input(
    "Legal & Incorporation Fees ($)", min_value=0, max_value=10000, value=3700
)
renovation_costs = st.sidebar.number_input(
    "Renovation Costs ($)", min_value=0, max_value=50000, value=15000
)
equipment_deposit = st.sidebar.number_input(
    "Equipment Security Deposit ($)", min_value=0, max_value=10000, value=5000
)
initial_supplies = st.sidebar.number_input(
    "Initial Supplies & Inventory ($)", min_value=0, max_value=10000, value=3000
)
website_setup = st.sidebar.number_input(
    "Website & Booking System Setup ($)", min_value=0, max_value=5000, value=3000
)
security_deposit = st.sidebar.number_input(
    "Rent Security Deposit ($)", min_value=0, max_value=15000, value=7500
)
other_startup = st.sidebar.number_input(
    "Other Startup Costs ($)", min_value=0, max_value=10000, value=2000
)

# Calculate total startup costs
total_startup_costs = (
    legal_costs
    + renovation_costs
    + equipment_deposit
    + initial_supplies
    + website_setup
    + security_deposit
    + other_startup
)

# Revenue Parameters
st.sidebar.subheader("Revenue Parameters")
clients_per_month = st.sidebar.number_input(
    "Target Clients per Month", min_value=1, max_value=200, value=40
)
average_fee = st.sidebar.number_input(
    "Average Service Fee ($)", min_value=100, max_value=1000, value=300
)

# Fixed Costs
st.sidebar.subheader("Monthly Fixed Costs")
rent_cost = st.sidebar.number_input(
    "Rent ($)", min_value=0, max_value=10000, value=2500
)
equipment_lease = st.sidebar.number_input(
    "Equipment Lease ($)", min_value=0, max_value=5000, value=2500
)
insurance_cost = st.sidebar.number_input(
    "Insurance ($)", min_value=0, max_value=2000, value=300
)
marketing_cost = st.sidebar.number_input(
    "Marketing ($)", min_value=0, max_value=3000, value=500
)
software_cost = st.sidebar.number_input(
    "Software/Booking Systems ($)", min_value=0, max_value=500, value=150
)

# Annual Costs
st.sidebar.subheader("Annual Costs")
accounting_fees = st.sidebar.number_input(
    "Annual Accounting & Tax Preparation ($)", min_value=0, max_value=10000, value=2400
)
monthly_accounting = accounting_fees / 12  # Convert to monthly for cash flow

# Variable Costs
st.sidebar.subheader("Variable Costs")
supplies_per_client = st.sidebar.number_input(
    "Supplies Cost per Client ($)", min_value=0, max_value=100, value=20
)
utilities_per_month = st.sidebar.number_input(
    "Monthly Utilities ($)", min_value=0, max_value=1000, value=400
)
credit_card_fee_percent = st.sidebar.slider(
    "Credit Card Processing Fee (%)", 1.5, 4.0, 2.9, 0.1
)

# Loan Parameters
st.sidebar.subheader("Loan Parameters")
loan_amount = st.sidebar.number_input(
    "Loan Amount ($)", min_value=10000, max_value=200000, value=total_startup_costs
)
interest_rate = st.sidebar.slider("Interest Rate (%)", 5.0, 15.0, 9.0, 0.5)
loan_term_years = st.sidebar.selectbox("Loan Term (Years)", [3, 5, 7, 10], 1)
down_payment_percent = st.sidebar.slider("Down Payment (%)", 10, 50, 30, 5)

# Display Startup Costs Breakdown
st.subheader("Startup Costs Breakdown")
startup_costs_data = {
    "Category": [
        "Legal & Incorporation",
        "Renovations",
        "Equipment Deposit",
        "Initial Supplies",
        "Website Setup",
        "Rent Deposit",
        "Other Costs",
    ],
    "Amount": [
        legal_costs,
        renovation_costs,
        equipment_deposit,
        initial_supplies,
        website_setup,
        security_deposit,
        other_startup,
    ],
}

fig_startup = px.pie(
    startup_costs_data,
    values="Amount",
    names="Category",
    title=f"Total Startup Costs: ${total_startup_costs:,.2f}",
)
st.plotly_chart(fig_startup)

# Calculate derived values
monthly_revenue = clients_per_month * average_fee
credit_card_fees = monthly_revenue * (credit_card_fee_percent / 100)
monthly_variable_costs = (
    (supplies_per_client * clients_per_month) + utilities_per_month + credit_card_fees
)
monthly_fixed_costs = (
    rent_cost
    + equipment_lease
    + insurance_cost
    + marketing_cost
    + software_cost
    + monthly_accounting
)

# Loan calculations
loan_amount = total_startup_costs * (1 - down_payment_percent / 100)
monthly_interest_rate = interest_rate / (12 * 100)
number_of_payments = loan_term_years * 12
monthly_loan_payment = (
    loan_amount
    * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
    / ((1 + monthly_interest_rate) ** number_of_payments - 1)
)


# Function to calculate monthly data
def calculate_monthly_data(months=24):
    data = []
    cumulative_cash_flow = -total_startup_costs

    for month in range(months):
        total_costs = (
            monthly_fixed_costs + monthly_variable_costs + monthly_loan_payment
        )
        monthly_profit = monthly_revenue - total_costs
        cumulative_cash_flow += monthly_profit

        data.append(
            {
                "month": month + 1,
                "revenue": monthly_revenue,
                "fixed_costs": monthly_fixed_costs,
                "variable_costs": monthly_variable_costs,
                "loan_payment": monthly_loan_payment,
                "total_costs": total_costs,
                "profit": monthly_profit,
                "cumulative_cash_flow": cumulative_cash_flow,
            }
        )

    return pd.DataFrame(data)


# Calculate financial metrics
monthly_data = calculate_monthly_data()
payback_period = (
    monthly_data[monthly_data["cumulative_cash_flow"] > 0].iloc[0]["month"]
    if any(monthly_data["cumulative_cash_flow"] > 0)
    else ">24"
)
roi_2year = (
    (monthly_data.iloc[-1]["cumulative_cash_flow"] + total_startup_costs)
    / total_startup_costs
    * 100
)

# Display key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Monthly Revenue", f"${monthly_revenue:,.2f}")
with col2:
    st.metric(
        "Monthly Costs",
        f"${(monthly_fixed_costs + monthly_variable_costs + monthly_loan_payment):,.2f}",
    )
with col3:
    st.metric("Payback Period", f"{payback_period} months")
with col4:
    st.metric("2-Year ROI", f"{roi_2year:.1f}%")

# Loan Details
st.subheader("Loan Details")
loan_col1, loan_col2, loan_col3 = st.columns(3)
with loan_col1:
    st.metric("Total Loan Amount", f"${loan_amount:,.2f}")
with loan_col2:
    st.metric("Monthly Payment", f"${monthly_loan_payment:,.2f}")
with loan_col3:
    st.metric(
        "Total Interest",
        f"${(monthly_loan_payment * number_of_payments - loan_amount):,.2f}",
    )

# Monthly Cost Breakdown
st.subheader("Monthly Operating Costs")
operating_costs_data = {
    "Category": ["Fixed Costs", "Variable Costs", "Loan Payment"],
    "Amount": [monthly_fixed_costs, monthly_variable_costs, monthly_loan_payment],
}
fig_costs = px.pie(
    operating_costs_data,
    values="Amount",
    names="Category",
    title="Monthly Cost Distribution",
)
st.plotly_chart(fig_costs)

# Cash flow chart
st.subheader("Monthly Cash Flow Projection")
fig_cash_flow = go.Figure()

fig_cash_flow.add_trace(
    go.Scatter(
        x=monthly_data["month"], y=monthly_data["revenue"], name="Revenue", mode="lines"
    )
)

fig_cash_flow.add_trace(
    go.Scatter(
        x=monthly_data["month"],
        y=monthly_data["total_costs"],
        name="Total Costs",
        mode="lines",
    )
)

fig_cash_flow.add_trace(
    go.Scatter(
        x=monthly_data["month"],
        y=monthly_data["cumulative_cash_flow"],
        name="Cumulative Cash Flow",
        mode="lines",
    )
)

fig_cash_flow.update_layout(xaxis_title="Month", yaxis_title="Amount ($)", height=500)

st.plotly_chart(fig_cash_flow, use_container_width=True)

# Break-even analysis
total_fixed_costs = monthly_fixed_costs + monthly_loan_payment
break_even_clients = np.ceil(
    total_fixed_costs
    / (
        average_fee
        - supplies_per_client
        - (average_fee * credit_card_fee_percent / 100)
    )
)

st.subheader("Break-even Analysis")
col1, col2 = st.columns(2)
with col1:
    st.metric("Break-even Clients per Month", f"{break_even_clients:.0f}")
with col2:
    st.metric(
        "Current Monthly Profit",
        f"${(monthly_revenue - monthly_fixed_costs - monthly_variable_costs - monthly_loan_payment):,.2f}",
    )

# Financial details
st.subheader("Financial Details")
with st.expander("View Detailed Analysis"):
    st.write(
        f"""
    ### Initial Investment
    - Total Startup Costs: ${total_startup_costs:,.2f}
    - Down Payment: ${(total_startup_costs * down_payment_percent / 100):,.2f}
    - Loan Amount: ${loan_amount:,.2f}
    
    ### Annual Costs
    - Accounting & Tax Preparation: ${accounting_fees:,.2f}
    
    ### Monthly Financials
    - Revenue: ${monthly_revenue:,.2f}
    - Fixed Costs: ${monthly_fixed_costs:,.2f}
    - Variable Costs: ${monthly_variable_costs:,.2f}
    - Loan Payment: ${monthly_loan_payment:,.2f}
    
    ### Key Metrics
    - Gross Margin per Client: ${(average_fee - supplies_per_client - (average_fee * credit_card_fee_percent / 100)):,.2f}
    - Operating Margin: {((monthly_revenue - monthly_fixed_costs - monthly_variable_costs) / monthly_revenue * 100):,.1f}%
    - Debt Service Coverage Ratio: {((monthly_revenue - monthly_fixed_costs - monthly_variable_costs) / monthly_loan_payment):,.2f}
    """
    )

# Warning messages
if payback_period == ">24":
    st.warning(
        "⚠️ At current settings, the payback period extends beyond 24 months. Consider adjusting number of clients, pricing, or costs."
    )

if clients_per_month < break_even_clients:
    st.error(
        f"⚠️ Current clients per month ({clients_per_month}) is below break-even point ({break_even_clients:.0f}). The business will operate at a loss under these conditions."
    )

# Download data option
if st.sidebar.button("Download Financial Projections"):
    csv = monthly_data.to_csv(index=False)
    st.sidebar.download_button(
        label="Download CSV",
        data=csv,
        file_name="laser_business_projections.csv",
        mime="text/csv",
    )
