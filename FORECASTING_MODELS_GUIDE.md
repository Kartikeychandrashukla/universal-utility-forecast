# Forecasting Models Guide

## Current Status

### ✅ Working Models (Python 3.12 Compatible)

#### Simple Moving Average - **RECOMMENDED FOR PRODUCTION**
- **Status**: ✅ Fully functional with Python 3.12
- **No external dependencies required** (uses only numpy/pandas)
- **Features**:
  - Adaptive window sizing
  - Trend component for better accuracy
  - Confidence intervals based on historical volatility
  - Optional seasonality support
  - Full model evaluation metrics (RMSE, MAE, MAPE, R²)
- **Use Case**: Production-ready forecasting for any utility type
- **Performance**: Fast and reliable
- **Implementation**: [src/forecasting/simple_ma_model.py](src/forecasting/simple_ma_model.py)

### ⚠️ Advanced Models (Installation Required)

#### ARIMA (AutoRegressive Integrated Moving Average)
- **Status**: ⚠️ Packages installed but has numpy compatibility issues
- **Required Packages**: `statsmodels`, `pmdarima`
- **Issue**: The pmdarima package has binary incompatibility with numpy 2.x
- **Features**:
  - Auto-parameter selection
  - Handles trends and seasonality
  - Statistical forecasting
- **Installation Attempts Made**:
  ```bash
  pip install statsmodels  # ✅ Installed successfully
  pip install pmdarima     # ⚠️ Installed but has numpy conflict
  ```
- **Problem**: Multiple numpy versions causing conflicts (system has 2.3.4, pip shows 1.26.4)

#### Prophet (Facebook Prophet)
- **Status**: ⚠️ Package installed but not tested
- **Required Package**: `prophet`
- **Features**:
  - Business time series forecasting
  - Handles seasonality, holidays, outliers
  - Missing data support
- **Installation**:
  ```bash
  pip install prophet  # ✅ Installed successfully
  ```

## How to Use the Forecasting Page

### Quick Start (Recommended)

1. **Load your data** on the Upload Data page
2. **Go to Forecast page**
3. **Select "Simple Moving Average"** from the model dropdown
4. **Configure forecast horizon** (default: 90 days)
5. **Adjust confidence level** (default: 95%)
6. **Click "Generate Forecast"**

The Simple Moving Average model is production-ready and works perfectly with Python 3.12!

### Model Availability Display

The forecast page now shows which models are available:

```
📋 Model Availability
✅ Simple Moving Average (Python 3.12 compatible)
❌ ARIMA - Package not installed
❌ Prophet - Package not installed
```

If you see ❌ for ARIMA or Prophet, the page will show installation commands.

## Attempting to Use ARIMA and Prophet

### Current Situation

The packages `statsmodels`, `pmdarima`, and `prophet` have been installed in your Python environment, but there are some compatibility issues:

1. **Numpy Version Conflict**:
   - System has numpy 2.3.4 installed globally
   - pmdarima was built against numpy 1.26.4
   - This causes a binary incompatibility error

2. **Path Priority Issue**:
   - Python is loading numpy 2.3.4 from `C:\Python312\Lib\site-packages`
   - Even though pip shows 1.26.4 is installed

### To Fix ARIMA/Prophet (Advanced Users)

If you really need ARIMA or Prophet, try these steps:

#### Option 1: Clean Environment (Recommended)

1. **Create a virtual environment**:
   ```bash
   cd "c:\Users\umesh\OneDrive\Desktop\universal detector"
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install all packages in the virtual environment**:
   ```bash
   pip install -r requirements-minimal.txt
   pip install statsmodels pmdarima prophet
   ```

3. **Run the dashboard from the virtual environment**:
   ```bash
   streamlit run dashboard/app.py
   ```

#### Option 2: Fix Numpy Conflict (Advanced)

1. **Remove all numpy versions**:
   ```bash
   pip uninstall numpy -y
   pip cache purge
   ```

2. **Install compatible numpy first**:
   ```bash
   pip install "numpy<2.0"
   ```

3. **Reinstall forecasting packages**:
   ```bash
   pip install statsmodels pmdarima prophet
   ```

## Model Comparison

| Feature | Simple MA | ARIMA | Prophet |
|---------|-----------|-------|---------|
| **Python 3.12 Compatible** | ✅ Yes | ⚠️ Complex | ⚠️ Complex |
| **No Dependencies** | ✅ Yes | ❌ No | ❌ No |
| **Speed** | ⚡ Very Fast | 🐌 Slow | 🐌 Very Slow |
| **Accuracy** | 🎯 Good | 🎯 Very Good | 🎯 Excellent |
| **Seasonality** | ✅ Optional | ✅ Yes | ✅ Advanced |
| **Trend** | ✅ Yes | ✅ Yes | ✅ Advanced |
| **Auto-tuning** | ✅ Adaptive | ✅ auto_arima | ✅ Automatic |
| **Confidence Intervals** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Evaluation Metrics** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Production Ready** | ✅ Yes | ⚠️ Setup Required | ⚠️ Setup Required |

## Recommendations

### For Production Use
- **Use Simple Moving Average**: It's reliable, fast, and has no dependency issues

### For Research/Testing
- **Try ARIMA or Prophet**: Follow the virtual environment setup above

### For Best Accuracy
1. Start with Simple MA to get baseline results
2. If needed, set up a virtual environment for ARIMA/Prophet
3. Compare results and choose the best model for your data

## Example: Using Simple MA Forecaster

The Simple MA model provides excellent results for most use cases:

```python
from src.forecasting.simple_ma_model import SimpleMAForecaster

# Initialize
forecaster = SimpleMAForecaster(
    window_size=30,           # 30-day moving average
    confidence_level=0.95,    # 95% confidence intervals
    seasonality_periods=7     # Weekly seasonality (optional)
)

# Fit and predict
forecaster.fit(train_data)
forecast_df = forecaster.predict(steps=90)

# Evaluate
metrics = forecaster.evaluate(test_data)
print(f"RMSE: {metrics['rmse']:.2f}")
print(f"MAPE: {metrics['mape']:.2f}%")
```

## Dashboard Features

The Forecast page now includes:

1. **✅ Automatic model availability detection**
2. **✅ Clear installation instructions**
3. **✅ Graceful handling of missing packages**
4. **✅ Full functionality with Simple MA**
5. **✅ Model evaluation metrics**
6. **✅ Visual forecast charts**
7. **✅ Confidence intervals**
8. **✅ Export to CSV**

## Troubleshooting

### "Simple Moving Average" is the only option
- This is normal if ARIMA/Prophet packages aren't installed
- Simple MA is production-ready and works great!

### ARIMA/Prophet errors
- Check the "Model Availability" expander on the Forecast page
- Follow the installation commands shown
- Consider using a virtual environment (see Option 1 above)

### Import errors
- The dashboard handles these gracefully now
- Missing packages won't crash the app
- You can still use available models

## Summary

**You now have a fully functional forecasting system** with the Simple Moving Average model that:

- ✅ Works perfectly with Python 3.12
- ✅ Requires no complex dependencies
- ✅ Provides confidence intervals
- ✅ Includes evaluation metrics
- ✅ Supports optional seasonality
- ✅ Is production-ready

**ARIMA and Prophet** are available but require additional setup due to numpy compatibility issues. For most use cases, the Simple MA model will provide excellent results without the complexity.
