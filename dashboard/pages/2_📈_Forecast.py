"""Forecast future prices"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import forecasting models
from src.forecasting.xgboost_model import XGBoostForecaster
from src.forecasting.exponential_smoothing_model import ExponentialSmoothingForecaster
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
    # Available models (Python 3.12/3.13 compatible)
    available_models = ["XGBoost", "Exponential Smoothing", "Simple Moving Average"]

    model_type = st.selectbox(
        "Forecast Model",
        available_models,
        index=0,
        help="Select forecasting algorithm (all models are Python 3.12+ compatible)"
    )

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
                else:  # Simple Moving Average
                    forecaster_eval = SimpleMAForecaster(confidence_level=confidence_level)

                forecaster_eval.fit(train_data)

                # Evaluate model
                if model_type == "Simple Moving Average":
                    metrics = forecaster_eval.evaluate(test_data)
                    rmse = metrics['rmse']
                    mae = metrics['mae']
                    mape = metrics['mape']
                else:
                    # For XGBoost/Exponential Smoothing, calculate metrics manually
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
    st.markdown("All models are **Python 3.12+ and 3.13+ compatible** and deployment-ready!")

    tab1, tab2, tab3 = st.tabs(["XGBoost", "Exponential Smoothing", "Simple MA"])

    with tab1:
        st.markdown("""
        **XGBoost (Gradient Boosting)** ⚡ Recommended

        XGBoost is a powerful machine learning model that:
        - Uses gradient boosting with lag features for accurate predictions
        - Automatically captures complex patterns and non-linear relationships
        - Handles trend, seasonality, and volatility in time series data
        - Provides excellent accuracy for short to medium-term forecasts
        - Fully compatible with Python 3.12 and 3.13
        - Production-ready with confidence intervals

        **How it works:**
        - Creates lag features (previous 7 days by default)
        - Adds rolling statistics (mean, std) for additional context
        - Trains gradient boosting model on historical patterns
        - Generates predictions with uncertainty bounds

        **Best for:**
        - Utility price forecasting with complex patterns
        - Non-linear trends and seasonal variations
        - Production deployments requiring high accuracy
        """)

    with tab2:
        st.markdown("""
        **Exponential Smoothing (Holt-Winters)** 📈 Recommended

        Exponential Smoothing is a proven statistical method that:
        - Captures trend and seasonal patterns automatically
        - Uses weighted averages giving more importance to recent data
        - Handles additive and multiplicative seasonality
        - Works excellently for utility price data
        - Fully compatible with Python 3.12 and 3.13
        - Production-ready with confidence intervals

        **How it works:**
        - Automatically detects seasonality (default: 7-day weekly pattern)
        - Fits trend component for long-term direction
        - Applies seasonal adjustments for recurring patterns
        - Generates smooth, reliable forecasts

        **Best for:**
        - Utility prices with weekly/monthly patterns
        - Data with clear trends and seasonality
        - Reliable medium-term forecasts (30-365 days)
        """)

    with tab3:
        st.markdown("""
        **Simple Moving Average** ⚡ Fast & Reliable

        A lightweight, production-ready forecasting model that:
        - Uses moving average with trend component
        - Calculates confidence intervals based on historical volatility
        - Optional seasonality support for recurring patterns
        - Minimal dependencies (no external ML packages)
        - Fully compatible with Python 3.12 and 3.13
        - Provides full model evaluation metrics

        **How it works:**
        - Calculates moving average of recent prices
        - Estimates trend from recent data points
        - Projects forward: MA + trend × time_step
        - Adds seasonal component if requested

        **Best for:**
        - Quick baseline forecasts
        - Simple trends without complex patterns
        - Testing and validation
        """)
