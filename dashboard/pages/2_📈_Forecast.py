"""Forecast future prices"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import forecasting models
try:
    from src.forecasting.xgboost_model import XGBoostForecaster
    XGBOOST_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    XGBOOST_AVAILABLE = False
    XGBOOST_ERROR = str(e)

try:
    from src.forecasting.exponential_smoothing_model import ExponentialSmoothingForecaster
    EXP_SMOOTH_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    EXP_SMOOTH_AVAILABLE = False
    EXP_SMOOTH_ERROR = str(e)

try:
    from src.forecasting.arima_model import ARIMAForecaster
    ARIMA_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    ARIMA_AVAILABLE = False
    ARIMA_ERROR = str(e)

try:
    from src.forecasting.prophet_model import ProphetForecaster
    PROPHET_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    PROPHET_AVAILABLE = False
    PROPHET_ERROR = str(e)

from src.forecasting.simple_ma_model import SimpleMAForecaster
from src.utils.config_loader import load_config

st.set_page_config(page_title="Forecast", page_icon="📈", layout="wide")

# Load config
config = load_config()

# Header
st.title("📈 Price Forecasting")
st.markdown("Generate future price predictions using advanced forecasting models.")

# Check if data is loaded
if st.session_state.get('uploaded_data') is None:
    st.warning("⚠️ No data loaded. Please upload data first!")
    st.info("👈 Go to 'Upload Data' page to load your data.")
    st.stop()

data = st.session_state.uploaded_data

# Forecast configuration
st.markdown("## ⚙️ Forecast Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    forecast_horizon = st.number_input(
        "Forecast Horizon (days)",
        min_value=1,
        max_value=365,
        value=90,
        help="Number of days to forecast into the future"
    )

with col2:
    # Build list of available models
    available_models = []
    if XGBOOST_AVAILABLE:
        available_models.append("XGBoost")
    if EXP_SMOOTH_AVAILABLE:
        available_models.append("Exponential Smoothing")
    if ARIMA_AVAILABLE:
        available_models.append("ARIMA")
    if PROPHET_AVAILABLE:
        available_models.append("Prophet")
    available_models.append("Simple Moving Average")  # Always available

    model_type = st.selectbox(
        "Forecast Model",
        available_models,
        index=0,  # Default to first available model
        help="Select forecasting algorithm"
    )

    # Show availability status
    if not ARIMA_AVAILABLE or not PROPHET_AVAILABLE:
        with st.expander("📋 Model Availability"):
            st.write("**Available Models:**")
            st.write(f"✅ Simple Moving Average (Python 3.12 compatible)")
            if ARIMA_AVAILABLE:
                st.write(f"✅ ARIMA")
            else:
                st.write(f"❌ ARIMA - Package not installed")
                st.code("pip install statsmodels pmdarima", language="bash")
            if PROPHET_AVAILABLE:
                st.write(f"✅ Prophet")
            else:
                st.write(f"❌ Prophet - Package not installed")
                st.code("pip install prophet", language="bash")

with col3:
    confidence_level = st.slider(
        "Confidence Level",
        min_value=0.80,
        max_value=0.99,
        value=0.95,
        step=0.01,
        help="Confidence level for prediction intervals"
    )

# Train/Test split
st.markdown("### 📊 Train/Test Split")
test_size = st.slider(
    "Test Set Size (%)",
    min_value=10,
    max_value=30,
    value=20,
    help="Percentage of data to use for testing"
) / 100

# Split data
split_idx = int(len(data) * (1 - test_size))
train_data = data['price'].iloc[:split_idx]
test_data = data['price'].iloc[split_idx:]

col1, col2 = st.columns(2)
with col1:
    st.metric("Training Records", len(train_data))
with col2:
    st.metric("Test Records", len(test_data))

# Forecast button
if st.button("🚀 Generate Forecast", type="primary"):
    with st.spinner(f"Generating {model_type} forecast..."):
        try:
            # Initialize forecaster
            if model_type == "XGBoost":
                forecaster = XGBoostForecaster(
                    n_lags=min(7, len(train_data) // 4),
                    confidence_level=confidence_level
                )
                forecaster.fit(train_data)
                forecast_df = forecaster.predict(forecast_horizon)

            elif model_type == "Exponential Smoothing":
                forecaster = ExponentialSmoothingForecaster(
                    confidence_level=confidence_level
                )
                forecaster.fit(train_data)
                forecast_df = forecaster.predict(forecast_horizon)

            elif model_type == "ARIMA":
                if not ARIMA_AVAILABLE:
                    st.error("❌ ARIMA model is not available.")
                    st.info("Install required packages: `pip install statsmodels pmdarima`")
                    st.stop()

                forecaster = ARIMAForecaster(config.get('forecasting', {}).get('models', {}).get('arima', {}))
                forecaster.fit(train_data)
                forecast_df = forecaster.predict(forecast_horizon)

            elif model_type == "Prophet":
                if not PROPHET_AVAILABLE:
                    st.error("❌ Prophet model is not available.")
                    st.info("Install required package: `pip install prophet`")
                    st.stop()

                forecaster = ProphetForecaster(config.get('forecasting', {}).get('models', {}).get('prophet', {}))
                forecaster.fit(train_data)
                forecast_df = forecaster.predict(forecast_horizon)

            else:  # Simple Moving Average
                forecaster = SimpleMAForecaster(
                    confidence_level=confidence_level
                )
                forecaster.fit(train_data)
                forecast_df = forecaster.predict(forecast_horizon)

            # Store forecast in session state
            st.session_state.forecast = forecast_df
            st.session_state.forecaster = model_type

            st.success(f"✅ {model_type} forecast generated successfully!")

        except Exception as e:
            st.error(f"❌ Error generating forecast: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

# Display forecast results
if 'forecast' in st.session_state:
    forecast_df = st.session_state.forecast

    st.markdown("---")
    st.markdown("## 📊 Forecast Results")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Forecast Mean", f"${forecast_df['forecast'].mean():.2f}")

    with col2:
        st.metric("Forecast Max", f"${forecast_df['forecast'].max():.2f}")

    with col3:
        st.metric("Forecast Min", f"${forecast_df['forecast'].min():.2f}")

    with col4:
        volatility = forecast_df['forecast'].std()
        st.metric("Forecast Std Dev", f"${volatility:.2f}")

    # Forecast chart
    st.markdown("### 📈 Forecast Visualization")

    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=train_data.index,
        y=train_data.values,
        mode='lines',
        name='Historical (Train)',
        line=dict(color='#1f77b4', width=2)
    ))

    # Test data
    fig.add_trace(go.Scatter(
        x=test_data.index,
        y=test_data.values,
        mode='lines',
        name='Historical (Test)',
        line=dict(color='#ff7f0e', width=2)
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['forecast'],
        mode='lines',
        name='Forecast',
        line=dict(color='#2ca02c', width=2, dash='dash')
    ))

    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['upper_bound'],
        mode='lines',
        name='Upper Bound',
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['lower_bound'],
        mode='lines',
        name='Lower Bound',
        fill='tonexty',
        fillcolor='rgba(44, 160, 44, 0.2)',
        line=dict(width=0),
        showlegend=True
    ))

    fig.update_layout(
        title=f"{st.session_state.forecaster} Price Forecast",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode='x unified',
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Forecast table
    st.markdown("### 📋 Forecast Data")

    # Show summary statistics
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### First 10 Days")
        st.dataframe(forecast_df.head(10).style.format("{:.2f}"))

    with col2:
        st.markdown("#### Last 10 Days")
        st.dataframe(forecast_df.tail(10).style.format("{:.2f}"))

    # Download forecast
    csv = forecast_df.to_csv()
    st.download_button(
        label="📥 Download Forecast Data",
        data=csv,
        file_name=f"forecast_{st.session_state.forecaster}.csv",
        mime="text/csv",
    )

    # Model evaluation on test set
    if len(test_data) > 0:
        st.markdown("---")
        st.markdown("## 📊 Model Evaluation on Test Set")

        try:
            # Backtest on test period
            with st.spinner("Evaluating model on test data..."):
                # Re-fit on train data and predict test period
                backtest_horizon = len(test_data)

                if model_type == "XGBoost":
                    forecaster_eval = XGBoostForecaster(
                        n_lags=min(7, len(train_data) // 4),
                        confidence_level=confidence_level
                    )
                elif model_type == "Exponential Smoothing":
                    forecaster_eval = ExponentialSmoothingForecaster(
                        confidence_level=confidence_level
                    )
                elif model_type == "ARIMA":
                    if not ARIMA_AVAILABLE:
                        st.info("ARIMA not available for evaluation")
                    else:
                        forecaster_eval = ARIMAForecaster(config.get('forecasting', {}).get('models', {}).get('arima', {}))
                elif model_type == "Prophet":
                    if not PROPHET_AVAILABLE:
                        st.info("Prophet not available for evaluation")
                    else:
                        forecaster_eval = ProphetForecaster(config.get('forecasting', {}).get('models', {}).get('prophet', {}))
                else:  # Simple Moving Average
                    forecaster_eval = SimpleMAForecaster(confidence_level=confidence_level)

                forecaster_eval.fit(train_data)

                # For Simple MA, use the evaluate method directly
                if model_type == "Simple Moving Average":
                    metrics = forecaster_eval.evaluate(test_data)
                    rmse = metrics['rmse']
                    mae = metrics['mae']
                    mape = metrics['mape']
                else:
                    # For ARIMA/Prophet, calculate metrics manually
                    from sklearn.metrics import mean_squared_error, mean_absolute_error

                    backtest_forecast = forecaster_eval.predict(backtest_horizon)
                    y_true = test_data.values
                    y_pred = backtest_forecast['forecast'].values[:len(y_true)]

                    mse = mean_squared_error(y_true, y_pred)
                    rmse = np.sqrt(mse)
                    mae = mean_absolute_error(y_true, y_pred)
                    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("RMSE", f"{rmse:.2f}")

                with col2:
                    st.metric("MAE", f"{mae:.2f}")

                with col3:
                    st.metric("MAPE", f"{mape:.2f}%")

                with col4:
                    accuracy = max(0, 100 - mape)
                    st.metric("Accuracy", f"{accuracy:.1f}%")

        except Exception as e:
            st.warning(f"Could not evaluate model: {str(e)}")

else:
    st.info("👆 Configure forecast parameters and click 'Generate Forecast' to begin!")

    st.markdown("### 📖 About Forecasting Models")

    tab1, tab2, tab3 = st.tabs(["ARIMA", "Prophet", "Simple MA"])

    with tab1:
        st.markdown("""
        **ARIMA (AutoRegressive Integrated Moving Average)**

        ARIMA is a statistical model for time series forecasting that:
        - Captures autocorrelations in the data
        - Handles trends through differencing
        - Works well for short to medium-term forecasts
        - Automatically selects optimal parameters

        Best for: Stationary or near-stationary time series
        """)

    with tab2:
        st.markdown("""
        **Prophet (Facebook Prophet)**

        Prophet is designed for business time series with:
        - Strong seasonal patterns
        - Holiday effects
        - Missing data
        - Outliers

        Best for: Data with clear seasonality and trends
        """)

    with tab3:
        st.markdown("""
        **Simple Moving Average** ✅ Python 3.12 Compatible

        A production-ready forecasting model that:
        - Uses moving average with trend component
        - Calculates confidence intervals based on volatility
        - Optional seasonality support
        - No external dependencies required (works with Python 3.12!)
        - Provides full model evaluation metrics

        Best for: Quick, reliable forecasts without complex dependencies
        """)
