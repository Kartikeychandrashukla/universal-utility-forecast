# ⚡ Quick Installation Guide

## 🐍 Python 3.12 Users - READ THIS FIRST!

**If you have Python 3.12**, use the minimal requirements:
```bash
pip install -r requirements-minimal.txt
```

See [PYTHON312_INSTALL.md](PYTHON312_INSTALL.md) for details.

---

## 🚀 Fast Track (3 Steps)

### Step 1: Install Python Packages

**Option A - Minimal Install (Python 3.12 Compatible - RECOMMENDED):**
```bash
pip install -r requirements-minimal.txt
```

**Option B - Full Install (Python 3.9-3.11):**
```bash
pip install -r requirements.txt
```

**Option C - Manual Install (If both fail):**
```bash
pip install streamlit pandas numpy plotly scikit-learn python-dotenv pyyaml
```

### Step 2: Run the Dashboard

**Windows:**
```bash
run_dashboard.bat
```

**Mac/Linux:**
```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

**Or:**
```bash
streamlit run dashboard/app.py
```

### Step 3: Open Browser

Go to: **http://localhost:8501**

That's it! 🎉

---

## 📋 Optional: Advanced Features

### For ARIMA Forecasting:
```bash
pip install statsmodels pmdarima
```

### For Prophet Forecasting:
```bash
pip install prophet
```

### For API Backend:
```bash
pip install fastapi uvicorn
```

---

## 🐛 Troubleshooting

### "pip: command not found"
```bash
python -m pip install streamlit pandas numpy plotly scikit-learn
```

### "Permission denied"
```bash
python -m pip install --user streamlit pandas numpy plotly
```

### "Module not found"
Make sure you're in the correct directory:
```bash
cd "c:\Users\umesh\OneDrive\Desktop\universal detector"
```

### Port already in use
```bash
streamlit run dashboard/app.py --server.port 8502
```

---

## ✅ Verify Installation

Run this command to test:
```bash
python -c "import streamlit, pandas, numpy, plotly; print('✅ All core packages installed!')"
```

---

## 🎯 Next Steps

1. **Load Sample Data**: Try "Natural Gas" sample in the Upload Data page
2. **Generate Forecast**: Use "Simple Moving Average" model (no dependencies needed)
3. **Run Valuation**: Test Monte Carlo simulation with default parameters

---

## 📚 Need More Help?

- See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed guide
- See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for feature overview
- Check console output for error messages
