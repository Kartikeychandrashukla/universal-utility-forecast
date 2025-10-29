"""
Universal Utility Risk Analytics Platform - Streamlit Dashboard
Main application entry point
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config_loader import load_config
from src.utils.logger import get_logger

# Page configuration
st.set_page_config(
    page_title="Universal Utility Risk Analytics Platform",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
@st.cache_resource
def get_config():
    return load_config()

config = get_config()
logger = get_logger(__name__)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        padding-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Main page
def main():
    # Header
    st.markdown('<div class="main-header">🔋 Universal Utility Risk Analytics Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">From historical data to optimized storage strategies - for any utility</div>', unsafe_allow_html=True)

    # Welcome message
    st.markdown("---")

    # Key Features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📊 Data Analysis
        - Auto-detect utility type
        - Data validation & cleaning
        - Comprehensive statistics
        - Quality assessment
        """)

    with col2:
        st.markdown("""
        ### 📈 Forecasting
        - Multiple models (ARIMA, Prophet)
        - Ensemble predictions
        - Confidence intervals
        - Model comparison
        """)

    with col3:
        st.markdown("""
        ### 💰 Valuation
        - Storage contract pricing
        - Monte Carlo simulation
        - Strategy optimization
        - Risk metrics
        """)

    st.markdown("---")

    # Quick Start Guide
    st.markdown("## 🚀 Quick Start Guide")

    st.markdown("""
    ### Getting Started

    1. **Upload Your Data** 📤
       - Navigate to the "Upload Data" page
       - Upload your CSV file with price data
       - Review data quality and statistics

    2. **Create Forecasts** 📈
       - Go to the "Forecast" page
       - Select forecast horizon
       - Choose your preferred model
       - View predictions and confidence intervals

    3. **Value Contracts** 💰
       - Visit the "Value Contract" page
       - Input storage contract parameters
       - Run Monte Carlo simulation
       - Get optimal strategy and valuation

    4. **Generate Reports** 📋
       - Access the "Reports" page
       - Download comprehensive analysis
       - Export charts and data
    """)

    # Data Format Info
    with st.expander("📄 Data Format Requirements"):
        st.markdown("""
        ### Required Columns
        - **date**: Date in YYYY-MM-DD format
        - **price**: Numeric price values

        ### Optional Columns
        - volume, demand, temperature, storage_level, etc.

        ### Example CSV Format
        ```
        date,price,volume
        2022-01-01,3.45,12500
        2022-01-02,3.52,13200
        2022-01-03,3.48,12800
        ```

        ### Supported Utilities
        - Natural Gas
        - Electricity
        - Crude Oil
        - Water
        - Coal
        - And more...
        """)

    # Sample Data
    with st.expander("📦 Sample Data"):
        st.markdown("""
        Sample datasets are available in the `data/sample_data/` directory:

        - `natural_gas_sample.csv` - Natural gas price data
        - `electricity_sample.csv` - Electricity price data
        - `crude_oil_sample.csv` - Crude oil price data

        Use these to test the platform features!
        """)

    # Technical Info
    st.markdown("---")
    st.markdown("## 🛠️ Technical Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Forecasting Models
        - **ARIMA**: Auto-regressive models for time series
        - **Prophet**: Facebook's forecasting tool
        - **Regression**: Feature-based prediction
        - **Ensemble**: Combined model predictions
        """)

    with col2:
        st.markdown("""
        ### Valuation Methods
        - **Monte Carlo**: Stochastic price simulation
        - **Dynamic Programming**: Optimal strategy
        - **Real Options**: Contract flexibility value
        - **Risk Metrics**: VaR, CVaR, Greeks
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Universal Utility Risk Analytics Platform v1.0.0</p>
        <p>Built with Streamlit, FastAPI, and Python</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 Navigation")
        st.markdown("""
        Use the sidebar menu to navigate between pages:

        - 📊 **Upload Data**: Import and validate data
        - 📈 **Forecast**: Generate price predictions
        - 💰 **Value Contract**: Price storage contracts
        - 📋 **Reports**: Download results
        """)

        st.markdown("---")

        st.markdown("### ⚙️ Settings")
        st.markdown(f"**Version**: {config.get('app', {}).get('version', '1.0.0')}")
        st.markdown(f"**Log Level**: {config.get('app', {}).get('log_level', 'INFO')}")

        st.markdown("---")

        st.markdown("### 📖 Resources")
        st.markdown("""
        - [User Guide](../docs/USER_GUIDE.md)
        - [API Documentation](../docs/API_DOCUMENTATION.md)
        - [CSV Format Guide](../data/sample_data/data_format_guide.md)
        """)

        st.markdown("---")

        st.markdown("### 🐛 Support")
        st.markdown("""
        Having issues?
        - Check the documentation
        - Review sample data format
        - Open a GitHub issue
        """)

if __name__ == "__main__":
    main()
