# 🚀 INSTALL NOW - Copy & Paste These Commands

## Step 1: Install Packages (Pick ONE method)

### Method A: Auto Installation Script (EASIEST!)
```bash
install_python312.bat
```

### Method B: Install Minimal Requirements
```bash
pip install -r requirements-minimal.txt
```

### Method C: Install Core Packages
```bash
pip install streamlit pandas numpy plotly scikit-learn python-dotenv pyyaml
```

---

## Step 2: Run the Dashboard
```bash
streamlit run dashboard/app.py
```

---

## Step 3: Open Browser
Go to: **http://localhost:8501**

---

## That's It! 🎉

Now in the dashboard:
1. Click **"📊 Upload Data"**
2. Select **"Natural Gas"** sample
3. Click **"Load Sample"**
4. Go to **"📈 Forecast"**
5. Choose **"Simple Moving Average"**
6. Click **"🚀 Generate Forecast"**

---

## ✅ Quick Verification

Test if packages installed correctly:
```bash
python -c "import streamlit, pandas, numpy, plotly; print('✅ Ready!')"
```

---

## 🆘 If You Get Errors

Try installing packages one at a time:
```bash
pip install streamlit
pip install pandas
pip install numpy
pip install plotly
pip install scikit-learn
```

Then run:
```bash
streamlit run dashboard/app.py
```

---

## 📞 Still Stuck?

1. Check Python version: `python --version` (should be 3.9+)
2. Update pip: `python -m pip install --upgrade pip`
3. Try in virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install streamlit pandas numpy plotly scikit-learn
   ```

---

**Copy the commands above and paste in your terminal! 🚀**
