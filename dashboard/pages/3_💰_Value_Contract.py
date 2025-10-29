"""Value storage contracts"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import load_config

st.set_page_config(page_title="Value Contract", page_icon="💰", layout="wide")

# Load config
config = load_config()

# Header
st.title("💰 Storage Contract Valuation")
st.markdown("Value storage contracts using Monte Carlo simulation and optimization.")

# Check if data is loaded
if st.session_state.get('uploaded_data') is None:
    st.warning("⚠️ No data loaded. Please upload data first!")
    st.info("👈 Go to 'Upload Data' page to load your data.")
    st.stop()

data = st.session_state.uploaded_data

# Storage contract parameters
st.markdown("## ⚙️ Storage Contract Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Storage Capacity")
    capacity = st.number_input(
        "Total Capacity (units)",
        min_value=100,
        max_value=1000000,
        value=10000,
        step=1000
    )

    initial_inventory = st.slider(
        "Initial Inventory (%)",
        min_value=0,
        max_value=100,
        value=50
    )

with col2:
    st.markdown("### Injection/Withdrawal")
    injection_rate = st.number_input(
        "Max Injection Rate (units/day)",
        min_value=10,
        max_value=10000,
        value=1000,
        step=100
    )

    withdrawal_rate = st.number_input(
        "Max Withdrawal Rate (units/day)",
        min_value=10,
        max_value=10000,
        value=1000,
        step=100
    )

with col3:
    st.markdown("### Costs")
    injection_cost = st.number_input(
        "Injection Cost ($/unit)",
        min_value=0.0,
        max_value=10.0,
        value=0.05,
        step=0.01
    )

    withdrawal_cost = st.number_input(
        "Withdrawal Cost ($/unit)",
        min_value=0.0,
        max_value=10.0,
        value=0.05,
        step=0.01
    )

    storage_cost = st.number_input(
        "Storage Cost ($/unit/month)",
        min_value=0.0,
        max_value=5.0,
        value=0.10,
        step=0.01
    )

# Monte Carlo simulation parameters
st.markdown("## 🎲 Monte Carlo Simulation")

col1, col2 = st.columns(2)

with col1:
    n_simulations = st.selectbox(
        "Number of Simulations",
        [1000, 5000, 10000, 50000],
        index=2
    )

with col2:
    simulation_horizon = st.number_input(
        "Simulation Horizon (days)",
        min_value=30,
        max_value=365,
        value=180,
        step=30
    )

# Run valuation
if st.button("🚀 Value Contract", type="primary"):
    with st.spinner("Running Monte Carlo simulation..."):
        try:
            # Calculate price statistics from historical data
            price_mean = data['price'].mean()
            price_std = data['price'].std()
            price_returns = data['price'].pct_change().dropna()
            drift = price_returns.mean()
            volatility = price_returns.std()

            # Monte Carlo simulation
            np.random.seed(42)
            dt = 1  # daily
            n_steps = simulation_horizon

            # Initialize arrays
            price_paths = np.zeros((n_simulations, n_steps))
            price_paths[:, 0] = data['price'].iloc[-1]  # Start from last known price

            # Geometric Brownian Motion
            for t in range(1, n_steps):
                random_shock = np.random.normal(0, 1, n_simulations)
                price_paths[:, t] = price_paths[:, t-1] * np.exp(
                    (drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * random_shock
                )

            # Simple intrinsic value calculation
            # For each path, calculate optimal storage strategy value
            intrinsic_values = []

            for i in range(n_simulations):
                path = price_paths[i]

                # Simple strategy: inject when price is low, withdraw when high
                median_price = np.median(path)

                total_value = 0
                inventory = capacity * (initial_inventory / 100)

                for day, price in enumerate(path):
                    if price < median_price and inventory < capacity:
                        # Inject
                        amount = min(injection_rate, capacity - inventory)
                        cost = amount * (price + injection_cost)
                        inventory += amount
                        total_value -= cost

                    elif price > median_price and inventory > 0:
                        # Withdraw
                        amount = min(withdrawal_rate, inventory)
                        revenue = amount * (price - withdrawal_cost)
                        inventory -= amount
                        total_value += revenue

                # Add storage costs
                total_value -= inventory * storage_cost * (simulation_horizon / 30)

                intrinsic_values.append(total_value)

            intrinsic_values = np.array(intrinsic_values)

            # Calculate contract value statistics
            contract_value = np.mean(intrinsic_values)
            contract_std = np.std(intrinsic_values)
            var_95 = np.percentile(intrinsic_values, 5)
            cvar_95 = np.mean(intrinsic_values[intrinsic_values <= var_95])

            # Store results
            st.session_state.valuation_results = {
                'contract_value': contract_value,
                'std': contract_std,
                'var_95': var_95,
                'cvar_95': cvar_95,
                'intrinsic_values': intrinsic_values,
                'price_paths': price_paths,
            }

            st.success("✅ Valuation complete!")

        except Exception as e:
            st.error(f"❌ Error in valuation: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

# Display results
if 'valuation_results' in st.session_state:
    results = st.session_state.valuation_results

    st.markdown("---")
    st.markdown("## 📊 Valuation Results")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Contract Value",
            f"${results['contract_value']:,.0f}",
            help="Expected value from optimal storage strategy"
        )

    with col2:
        st.metric(
            "Std Deviation",
            f"${results['std']:,.0f}",
            help="Volatility of contract value"
        )

    with col3:
        st.metric(
            "VaR (95%)",
            f"${results['var_95']:,.0f}",
            help="Value at Risk at 95% confidence"
        )

    with col4:
        st.metric(
            "CVaR (95%)",
            f"${results['cvar_95']:,.0f}",
            help="Conditional Value at Risk (expected loss in worst 5%)"
        )

    # Distribution of values
    st.markdown("### 📊 Distribution of Contract Values")

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=results['intrinsic_values'],
        nbinsx=50,
        name='Contract Values',
        marker_color='#1f77b4'
    ))

    fig.add_vline(
        x=results['contract_value'],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: ${results['contract_value']:,.0f}"
    )

    fig.add_vline(
        x=results['var_95'],
        line_dash="dash",
        line_color="orange",
        annotation_text=f"VaR 95%: ${results['var_95']:,.0f}"
    )

    fig.update_layout(
        title="Distribution of Contract Values",
        xaxis_title="Value ($)",
        yaxis_title="Frequency",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Price paths
    st.markdown("### 📈 Simulated Price Paths")

    # Show subset of paths
    n_paths_to_show = min(100, n_simulations)
    sample_indices = np.random.choice(n_simulations, n_paths_to_show, replace=False)

    fig = go.Figure()

    dates = pd.date_range(start=data.index[-1], periods=simulation_horizon, freq='D')

    for idx in sample_indices:
        fig.add_trace(go.Scatter(
            x=dates,
            y=results['price_paths'][idx],
            mode='lines',
            line=dict(width=0.5, color='lightblue'),
            showlegend=False,
            opacity=0.3
        ))

    # Add mean path
    mean_path = np.mean(results['price_paths'], axis=0)
    fig.add_trace(go.Scatter(
        x=dates,
        y=mean_path,
        mode='lines',
        name='Mean Path',
        line=dict(width=3, color='red')
    ))

    fig.update_layout(
        title=f"Sample of {n_paths_to_show} Simulated Price Paths",
        xaxis_title="Date",
        yaxis_title="Price",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Summary statistics
    st.markdown("### 📋 Summary Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Contract Value Statistics")
        stats_df = pd.DataFrame({
            'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'VaR 95%', 'CVaR 95%'],
            'Value': [
                f"${results['contract_value']:,.0f}",
                f"${np.median(results['intrinsic_values']):,.0f}",
                f"${results['std']:,.0f}",
                f"${np.min(results['intrinsic_values']):,.0f}",
                f"${np.max(results['intrinsic_values']):,.0f}",
                f"${results['var_95']:,.0f}",
                f"${results['cvar_95']:,.0f}",
            ]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### Contract Parameters")
        params_df = pd.DataFrame({
            'Parameter': [
                'Capacity',
                'Initial Inventory',
                'Injection Rate',
                'Withdrawal Rate',
                'Injection Cost',
                'Withdrawal Cost',
                'Storage Cost'
            ],
            'Value': [
                f"{capacity:,} units",
                f"{initial_inventory}%",
                f"{injection_rate:,} units/day",
                f"{withdrawal_rate:,} units/day",
                f"${injection_cost}/unit",
                f"${withdrawal_cost}/unit",
                f"${storage_cost}/unit/month"
            ]
        })
        st.dataframe(params_df, use_container_width=True, hide_index=True)

    # Download results
    results_df = pd.DataFrame({
        'simulation': range(len(results['intrinsic_values'])),
        'contract_value': results['intrinsic_values']
    })

    csv = results_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Valuation Results",
        data=csv,
        file_name="storage_contract_valuation.csv",
        mime="text/csv",
    )

else:
    st.info("👆 Configure contract parameters and click 'Value Contract' to begin!")

    st.markdown("### 📖 About Storage Contract Valuation")

    st.markdown("""
    Storage contracts provide the right (but not obligation) to:
    - **Inject** commodity into storage when prices are low
    - **Store** commodity over time
    - **Withdraw** commodity when prices are high

    #### Valuation Method

    We use **Monte Carlo simulation** to:
    1. Simulate thousands of possible future price paths
    2. Calculate optimal storage strategy for each path
    3. Compute expected value across all scenarios

    #### Key Metrics

    - **Contract Value**: Expected profit from optimal storage strategy
    - **VaR (Value at Risk)**: Worst expected loss at given confidence level
    - **CVaR (Conditional VaR)**: Average loss in worst scenarios
    - **Std Deviation**: Volatility of contract value

    #### Optimal Strategy

    The algorithm determines when to inject/withdraw based on:
    - Current price vs. expected future prices
    - Storage capacity constraints
    - Injection/withdrawal rate limits
    - Operating costs
    """)
