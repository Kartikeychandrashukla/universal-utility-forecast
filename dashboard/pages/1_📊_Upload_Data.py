"""Upload and validate utility data"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.data_handler import DataHandler
from src.core.utility_detector import UtilityDetector
from src.core.validators import DataValidator
from src.utils.config_loader import load_config

st.set_page_config(page_title="Upload Data", page_icon="📊", layout="wide")

# Load config
config = load_config()

# Initialize session state
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'utility_type' not in st.session_state:
    st.session_state.utility_type = None

# Header
st.title("📊 Upload & Validate Data")
st.markdown("Upload your utility price data and let us analyze it automatically.")

# File upload section
st.markdown("## 📤 Upload Data")

upload_col1, upload_col2 = st.columns([2, 1])

with upload_col1:
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a file containing at least 'date' and 'price' columns"
    )

with upload_col2:
    st.markdown("### Sample Data")
    sample_data = st.selectbox(
        "Or try sample data:",
        ["None", "Natural Gas", "Electricity", "Crude Oil"]
    )

    if sample_data != "None" and st.button("Load Sample"):
        sample_files = {
            "Natural Gas": "data/sample_data/natural_gas_sample.csv",
            "Electricity": "data/sample_data/electricity_sample.csv",
            "Crude Oil": "data/sample_data/crude_oil_sample.csv",
        }
        sample_path = Path(__file__).parent.parent.parent / sample_files[sample_data]

        if sample_path.exists():
            data_handler = DataHandler(config)
            try:
                data = data_handler.load_csv(sample_path)
                st.session_state.data_handler = data_handler
                st.session_state.uploaded_data = data
                st.session_state.sample_filename = sample_files[sample_data]  # Store filename for detection
                st.success(f"✅ Loaded {sample_data} sample data!")
            except Exception as e:
                st.error(f"❌ Error loading sample: {str(e)}")

# Process uploaded file
if uploaded_file is not None:
    try:
        data_handler = DataHandler(config)

        # Load data based on file type
        if uploaded_file.name.endswith('.csv'):
            data = data_handler.load_csv(uploaded_file)
        else:
            data = data_handler.load_excel(uploaded_file)

        st.session_state.data_handler = data_handler
        st.session_state.uploaded_data = data
        st.success(f"✅ Successfully loaded {len(data)} records!")

    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        st.info("💡 Make sure your file has 'date' and 'price' columns in the correct format.")

# Display data if loaded
if st.session_state.uploaded_data is not None:
    data = st.session_state.uploaded_data
    data_handler = st.session_state.data_handler

    st.markdown("---")

    # Data overview
    st.markdown("## 📋 Data Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", len(data))

    with col2:
        date_range = (data.index.max() - data.index.min()).days
        st.metric("Date Range (days)", date_range)

    with col3:
        st.metric("Start Date", str(data.index.min().date()))

    with col4:
        st.metric("End Date", str(data.index.max().date()))

    # Utility Detection
    st.markdown("## 🔍 Utility Type Detection")

    with st.spinner("Detecting utility type..."):
        detector = UtilityDetector(config)

        # Get filename from uploaded file or sample filename
        filename = None
        if uploaded_file:
            filename = uploaded_file.name
        elif 'sample_filename' in st.session_state:
            filename = st.session_state.sample_filename

        detection_result = detector.detect(
            data,
            filename=filename,
            columns=list(data.columns)
        )

        st.session_state.utility_type = detection_result

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Detected Type")
        st.markdown(f"### **{detection_result['utility_type'].replace('_', ' ').title()}**")
        st.metric("Confidence", f"{detection_result['confidence']:.1%}")

    with col2:
        st.markdown("### Characteristics")
        chars = detection_result['characteristics']
        char_col1, char_col2, char_col3 = st.columns(3)

        with char_col1:
            st.metric("Mean Price", f"${chars['mean_price']:.2f}")
            st.metric("Volatility", f"{chars['volatility']:.1%}")

        with char_col2:
            st.metric("Min Price", f"${chars['min_price']:.2f}")
            st.metric("Max Price", f"${chars['max_price']:.2f}")

        with char_col3:
            st.metric("Typical Unit", chars['typical_unit'])
            st.metric("Market", chars['market_name'])

    # Data Validation
    st.markdown("## ✅ Data Validation")

    with st.spinner("Validating data quality..."):
        validator = DataValidator(config)
        validation = validator.validate(data)
        quality_score = validator.get_data_quality_score(validation)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Data Quality Score",
            f"{quality_score}/100",
            delta="Good" if quality_score >= 80 else "Needs attention"
        )

    with col2:
        st.metric("Errors", len(validation['errors']))

    with col3:
        st.metric("Warnings", len(validation['warnings']))

    # Show validation details
    if validation['errors']:
        st.error("**Errors Found:**")
        for error in validation['errors']:
            st.error(f"❌ {error}")

    if validation['warnings']:
        with st.expander("⚠️ View Warnings"):
            for warning in validation['warnings']:
                st.warning(warning)

    # Validation checks
    with st.expander("📊 Detailed Validation Checks"):
        check_data = []
        for check_name, check_result in validation['checks'].items():
            check_data.append({
                'Check': check_name.replace('_', ' ').title(),
                'Status': '✅ Passed' if check_result['passed'] else '❌ Failed',
                'Details': check_result['message']
            })

        st.dataframe(pd.DataFrame(check_data), use_container_width=True)

    # Data Preview
    st.markdown("## 👀 Data Preview")

    tab1, tab2, tab3 = st.tabs(["📊 Chart", "📋 Table", "📈 Statistics"])

    with tab1:
        # Price chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['price'],
            mode='lines',
            name='Price',
            line=dict(color='#1f77b4', width=2)
        ))

        fig.update_layout(
            title="Price History",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode='x unified',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.dataframe(data, use_container_width=True)

        # Download button
        csv = data.to_csv()
        st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
        )

    with tab3:
        summary = data_handler.get_summary()

        st.markdown("### Price Statistics")
        stats_df = pd.DataFrame(summary['statistics']['price'], index=[0])
        st.dataframe(stats_df, use_container_width=True)

        # Distribution plot
        fig = px.histogram(
            data,
            x='price',
            nbins=50,
            title="Price Distribution",
            labels={'price': 'Price', 'count': 'Frequency'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Data Cleaning Options
    st.markdown("## 🧹 Data Cleaning")

    with st.expander("🔧 Cleaning Options"):
        col1, col2 = st.columns(2)

        with col1:
            remove_outliers = st.checkbox("Remove outliers", value=True)
            outlier_method = st.selectbox("Outlier method", ["iqr", "zscore"])

        with col2:
            fill_missing = st.checkbox("Fill missing values", value=True)
            fill_method = st.selectbox("Fill method", ["interpolate", "ffill", "bfill", "mean"])

        if st.button("🧹 Clean Data"):
            with st.spinner("Cleaning data..."):
                try:
                    cleaned_data = data_handler.clean_data(
                        remove_outliers_flag=remove_outliers,
                        fill_missing=fill_missing,
                        outlier_method=outlier_method,
                        fill_method=fill_method
                    )
                    st.session_state.uploaded_data = cleaned_data
                    st.success("✅ Data cleaned successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error cleaning data: {str(e)}")

    # Next steps
    st.markdown("---")
    st.markdown("### 🎯 Next Steps")
    st.info("✅ Data loaded and validated! Now you can:")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📈 Create Forecasts**")
        st.markdown("Generate future price predictions")

    with col2:
        st.markdown("**💰 Value Contracts**")
        st.markdown("Price storage contracts")

    with col3:
        st.markdown("**📋 Generate Reports**")
        st.markdown("Download comprehensive analysis")

else:
    # No data loaded
    st.info("👆 Please upload a CSV file or select sample data to get started!")

    st.markdown("### 📖 Data Format Requirements")
    st.markdown("""
    Your CSV file should contain at least:
    - **date** column: Dates in YYYY-MM-DD format
    - **price** column: Numeric price values

    Optional columns: volume, demand, temperature, etc.

    Example:
    ```
    date,price,volume
    2022-01-01,3.45,12500
    2022-01-02,3.52,13200
    ```
    """)
