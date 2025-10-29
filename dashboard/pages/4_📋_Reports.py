"""Generate and download reports"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Reports", page_icon="📋", layout="wide")

# Header
st.title("📋 Reports & Export")
st.markdown("Generate comprehensive reports and export your analysis results.")

# Check if data is loaded
if st.session_state.get('uploaded_data') is None:
    st.warning("⚠️ No data loaded. Please upload data first!")
    st.info("👈 Go to 'Upload Data' page to load your data.")
    st.stop()

data = st.session_state.uploaded_data

# Report generation
st.markdown("## 📄 Generate Report")

col1, col2 = st.columns(2)

with col1:
    report_type = st.selectbox(
        "Report Type",
        ["Comprehensive Analysis", "Data Summary", "Forecast Report", "Valuation Report"]
    )

with col2:
    report_format = st.selectbox(
        "Format",
        ["CSV", "Excel", "JSON"]
    )

# Report sections
st.markdown("### Report Sections")

include_data_summary = st.checkbox("Data Summary & Statistics", value=True)
include_utility_detection = st.checkbox("Utility Type Detection", value=True)
include_validation = st.checkbox("Data Validation Results", value=True)

if 'forecast' in st.session_state:
    include_forecast = st.checkbox("Forecast Results", value=True)
else:
    include_forecast = False
    st.info("Generate a forecast first to include forecast results in report")

if 'valuation_results' in st.session_state:
    include_valuation = st.checkbox("Valuation Results", value=True)
else:
    include_valuation = False
    st.info("Run valuation first to include valuation results in report")

# Generate report
if st.button("📄 Generate Report", type="primary"):
    with st.spinner("Generating report..."):
        try:
            report_data = {}

            # Data summary
            if include_data_summary:
                report_data['data_summary'] = {
                    'total_records': len(data),
                    'start_date': str(data.index.min().date()),
                    'end_date': str(data.index.max().date()),
                    'date_range_days': (data.index.max() - data.index.min()).days,
                    'mean_price': float(data['price'].mean()),
                    'median_price': float(data['price'].median()),
                    'std_price': float(data['price'].std()),
                    'min_price': float(data['price'].min()),
                    'max_price': float(data['price'].max()),
                }

            # Utility detection
            if include_utility_detection and 'utility_type' in st.session_state:
                utility = st.session_state.utility_type
                report_data['utility_detection'] = {
                    'detected_type': utility['utility_type'],
                    'confidence': float(utility['confidence']),
                    'characteristics': utility['characteristics']
                }

            # Forecast
            if include_forecast and 'forecast' in st.session_state:
                forecast = st.session_state.forecast
                report_data['forecast'] = forecast.to_dict()

            # Valuation
            if include_valuation and 'valuation_results' in st.session_state:
                valuation = st.session_state.valuation_results
                report_data['valuation'] = {
                    'contract_value': float(valuation['contract_value']),
                    'std_deviation': float(valuation['std']),
                    'var_95': float(valuation['var_95']),
                    'cvar_95': float(valuation['cvar_95']),
                }

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if report_format == "CSV":
                # Convert to DataFrame and save as CSV
                if include_forecast and 'forecast' in st.session_state:
                    csv_data = st.session_state.forecast.to_csv()
                    filename = f"report_{timestamp}.csv"
                else:
                    csv_data = data.to_csv()
                    filename = f"data_summary_{timestamp}.csv"

                st.download_button(
                    label="📥 Download CSV Report",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                )

            elif report_format == "JSON":
                import json
                json_data = json.dumps(report_data, indent=2)
                filename = f"report_{timestamp}.json"

                st.download_button(
                    label="📥 Download JSON Report",
                    data=json_data,
                    file_name=filename,
                    mime="application/json",
                )

            elif report_format == "Excel":
                st.info("Excel export requires openpyxl package. CSV format recommended.")

            st.success("✅ Report generated successfully!")

        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")

# Quick exports
st.markdown("---")
st.markdown("## 🚀 Quick Exports")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Raw Data")
    csv_data = data.to_csv()
    st.download_button(
        label="📥 Download Data (CSV)",
        data=csv_data,
        file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

with col2:
    if 'forecast' in st.session_state:
        st.markdown("### 📈 Forecast")
        forecast_csv = st.session_state.forecast.to_csv()
        st.download_button(
            label="📥 Download Forecast (CSV)",
            data=forecast_csv,
            file_name=f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.markdown("### 📈 Forecast")
        st.info("No forecast available")

with col3:
    if 'valuation_results' in st.session_state:
        st.markdown("### 💰 Valuation")
        valuation_data = pd.DataFrame({
            'metric': ['Contract Value', 'Std Dev', 'VaR 95%', 'CVaR 95%'],
            'value': [
                st.session_state.valuation_results['contract_value'],
                st.session_state.valuation_results['std'],
                st.session_state.valuation_results['var_95'],
                st.session_state.valuation_results['cvar_95'],
            ]
        })
        valuation_csv = valuation_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Valuation (CSV)",
            data=valuation_csv,
            file_name=f"valuation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.markdown("### 💰 Valuation")
        st.info("No valuation available")

# Session summary
st.markdown("---")
st.markdown("## 📊 Session Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Data Status")
    st.success("✅ Data loaded")
    st.metric("Records", len(data))

with col2:
    st.markdown("### Forecast Status")
    if 'forecast' in st.session_state:
        st.success("✅ Forecast generated")
        st.metric("Horizon", f"{len(st.session_state.forecast)} days")
    else:
        st.info("⏳ Not generated")

with col3:
    st.markdown("### Valuation Status")
    if 'valuation_results' in st.session_state:
        st.success("✅ Valuation complete")
        value = st.session_state.valuation_results['contract_value']
        st.metric("Contract Value", f"${value:,.0f}")
    else:
        st.info("⏳ Not run")

# Analysis summary table
st.markdown("### 📋 Analysis Summary")

summary_data = []

# Data info
summary_data.append({
    'Component': 'Data Upload',
    'Status': '✅ Complete',
    'Details': f"{len(data)} records from {data.index.min().date()} to {data.index.max().date()}"
})

# Utility detection
if 'utility_type' in st.session_state:
    utility = st.session_state.utility_type
    summary_data.append({
        'Component': 'Utility Detection',
        'Status': '✅ Complete',
        'Details': f"{utility['utility_type'].replace('_', ' ').title()} ({utility['confidence']:.1%} confidence)"
    })

# Forecast
if 'forecast' in st.session_state:
    summary_data.append({
        'Component': 'Forecasting',
        'Status': '✅ Complete',
        'Details': f"{st.session_state.forecaster} model - {len(st.session_state.forecast)} day forecast"
    })
else:
    summary_data.append({
        'Component': 'Forecasting',
        'Status': '⏳ Not run',
        'Details': 'Generate forecast in Forecast page'
    })

# Valuation
if 'valuation_results' in st.session_state:
    value = st.session_state.valuation_results['contract_value']
    summary_data.append({
        'Component': 'Valuation',
        'Status': '✅ Complete',
        'Details': f"Contract value: ${value:,.0f}"
    })
else:
    summary_data.append({
        'Component': 'Valuation',
        'Status': '⏳ Not run',
        'Details': 'Run valuation in Value Contract page'
    })

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Tips
st.markdown("---")
st.markdown("### 💡 Tips")

st.markdown("""
- **CSV format** works with Excel, Google Sheets, and most data tools
- **JSON format** is best for programmatic access and API integration
- Save your reports regularly during analysis
- Include timestamps in filenames for version control
- Export forecasts before making new predictions to compare results
""")
