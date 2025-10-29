# 🐍 Python 3.12 Installation Guide

You're using Python 3.12 which has compatibility issues with some older packages. Follow these steps:

## ✅ Solution 1: Install Minimal Requirements (RECOMMENDED)

This installs only the core packages needed to run the dashboard:

```bash
pip install -r requirements-minimal.txt
```

This will install:
- Streamlit (dashboard)
- Pandas (data handling)
- NumPy (numerical computing)
- Plotly (interactive charts)
- scikit-learn (machine learning)
- PyYAML (configuration)
- python-dotenv (environment variables)

**Features Available:**
- ✅ Data upload and validation
- ✅ Utility type detection
- ✅ Simple Moving Average forecasting
- ✅ Monte Carlo valuation
- ✅ Interactive visualizations
- ✅ Export to CSV/JSON

**Features Not Available (require problematic packages):**
- ❌ ARIMA forecasting (requires statsmodels)
- ❌ Prophet forecasting (requires prophet)

## ✅ Solution 2: Install Packages One by One

```bash
# Core packages (required)
pip install streamlit
pip install pandas
pip install numpy
pip install plotly
pip install scikit-learn
pip install python-dotenv
pip install pyyaml

# Optional packages (for advanced features)
pip install matplotlib
pip install seaborn
pip install fastapi
pip install uvicorn
```

## ✅ Solution 3: Upgrade pip and setuptools

Sometimes updating these helps:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-minimal.txt
```

## 🚀 Quick Start After Installation

Once packages are installed, run:

```bash
streamlit run dashboard/app.py
```

## 🎯 Using the Dashboard Without ARIMA/Prophet

The dashboard will work perfectly fine without these packages. When forecasting:

1. **Use "Simple Moving Average"** model
   - No external dependencies
   - Fast and reliable
   - Good for baseline predictions

2. **All other features work normally**:
   - Data upload ✅
   - Data validation ✅
   - Visualization ✅
   - Monte Carlo valuation ✅
   - Report generation ✅

## 📦 Optional: Installing Advanced Models

### For ARIMA (if you really need it):

Try installing with conda instead:
```bash
conda install -c conda-forge statsmodels
```

Or try a newer version:
```bash
pip install statsmodels>=0.14.0 --no-build-isolation
```

### For Prophet (if you really need it):

```bash
# Try with conda
conda install -c conda-forge prophet

# Or try newer version
pip install prophet>=1.1 --no-build-isolation
```

## ⚠️ Known Python 3.12 Issues

Some packages haven't fully updated for Python 3.12 yet:
- `great-expectations` - Skip this (it's optional)
- `pmdarima` - May have issues, use Simple MA instead
- Older versions of `statsmodels` and `prophet` - Use newer versions

## ✅ Verify Installation

Test if core packages are installed:

```bash
python -c "import streamlit, pandas, numpy, plotly, sklearn; print('✅ Core packages working!')"
```

## 🎉 You're Ready!

Once you see "✅ Core packages working!", run:

```bash
streamlit run dashboard/app.py
```

Then:
1. Load "Natural Gas" sample data
2. Generate forecast with "Simple Moving Average"
3. Run valuation with Monte Carlo
4. Export your results

## 💡 Pro Tip

The Simple Moving Average model actually works great for:
- Quick baseline forecasts
- Short-term predictions
- Testing the platform
- Production use when you don't need complex models

## 🆘 Still Having Issues?

1. **Check Python version:**
   ```bash
   python --version
   ```

2. **Try in a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements-minimal.txt
   ```

3. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

4. **Install without dependencies:**
   ```bash
   pip install --no-deps streamlit pandas numpy plotly scikit-learn
   ```

## 📧 What to Do Next

**RIGHT NOW:**
```bash
pip install -r requirements-minimal.txt
streamlit run dashboard/app.py
```

**THEN:**
- Test with sample data
- Use "Simple Moving Average" for forecasting
- All features work except ARIMA/Prophet

**Perfect for Python 3.12! 🐍**
