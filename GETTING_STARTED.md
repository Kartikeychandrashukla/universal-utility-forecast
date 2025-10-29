# 🚀 Getting Started with Universal Utility Risk Analytics Platform

Welcome! This guide will help you set up and run the platform in minutes.

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- (Optional) Docker for containerized deployment

## 🔧 Installation

### Method 1: Local Installation (Recommended for Development)

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\Users\umesh\OneDrive\Desktop\universal detector"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: If you encounter issues installing all packages, install core packages first:
   ```bash
   pip install streamlit pandas numpy plotly scikit-learn
   ```

   Then optionally add forecasting packages:
   ```bash
   pip install statsmodels pmdarima prophet
   ```

4. **Create environment file**
   ```bash
   copy .env.example .env
   ```

## 🚀 Running the Application

### Start the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open automatically in your browser at: http://localhost:8501

### Start the API (Optional)

In a separate terminal:
```bash
uvicorn api.app:app --reload
```

API will be available at: http://localhost:8000

## 📊 Quick Start Guide

### 1. Upload Your Data

1. Navigate to **"📊 Upload Data"** page
2. Click **"Browse files"** and select your CSV file
   - OR -
3. Try **Sample Data**: Select "Natural Gas" and click "Load Sample"

**Required CSV Format:**
```csv
date,price,volume
2022-01-01,3.45,12500
2022-01-02,3.52,13200
2022-01-03,3.48,12800
```

### 2. Generate Forecast

1. Go to **"📈 Forecast"** page
2. Configure:
   - Forecast Horizon (e.g., 90 days)
   - Model type (ARIMA, Prophet, or Simple MA)
   - Confidence level (e.g., 95%)
3. Click **"🚀 Generate Forecast"**
4. View predictions and download results

### 3. Value Storage Contract

1. Visit **"💰 Value Contract"** page
2. Set contract parameters:
   - Storage capacity
   - Injection/withdrawal rates
   - Costs
3. Configure Monte Carlo simulation
4. Click **"🚀 Value Contract"**
5. View valuation results and risk metrics

### 4. Generate Reports

1. Go to **"📋 Reports"** page
2. Select report type and format
3. Choose sections to include
4. Click **"📄 Generate Report"**
5. Download your comprehensive analysis

## 🐛 Troubleshooting

### Issue: Package Installation Fails

**Solution**: Install packages individually:
```bash
pip install streamlit pandas numpy plotly scikit-learn python-dotenv pyyaml
```

### Issue: "Module not found" errors

**Solution**: Make sure you're in the project directory and virtual environment is activated:
```bash
cd "c:\Users\umesh\OneDrive\Desktop\universal detector"
venv\Scripts\activate  # Windows
python -c "import sys; print(sys.path)"
```

### Issue: ARIMA or Prophet not available

**Solution**: These are optional. Use "Simple Moving Average" model instead, or install:
```bash
pip install statsmodels pmdarima prophet
```

### Issue: Port 8501 already in use

**Solution**: Use a different port:
```bash
streamlit run dashboard/app.py --server.port 8502
```

### Issue: Data file not loading

**Solution**: Check your CSV format:
- Must have 'date' and 'price' columns (lowercase)
- Date format: YYYY-MM-DD
- No missing values in price column
- At least 365 days of data

## 📖 Sample Data

Sample datasets are included in `data/sample_data/`:

- **natural_gas_sample.csv**: Natural gas prices with temperature
- **electricity_sample.csv**: Electricity prices with demand
- **crude_oil_sample.csv**: Crude oil prices

Use these to explore platform features!

## 🔒 Configuration

Edit `config.yaml` to customize:
- Forecasting parameters
- Valuation settings
- Data validation rules
- API and dashboard ports

## 🐳 Docker Deployment (Alternative)

### Build and run with Docker Compose:

```bash
cd docker
docker-compose up --build
```

Access:
- Dashboard: http://localhost:8501
- API: http://localhost:8000

## 📚 Next Steps

1. **Read the Documentation**: Check `/docs` folder for detailed guides
2. **Explore Sample Data**: Test with provided sample datasets
3. **Customize Configuration**: Edit `config.yaml` for your needs
4. **API Integration**: Use FastAPI backend for programmatic access

## 🆘 Getting Help

- **Documentation**: See `docs/` folder
- **Sample Data Guide**: `data/sample_data/data_format_guide.md`
- **Issues**: Check console output for error messages
- **Logs**: Enable debug mode in `config.yaml`

## 🎯 Common Use Cases

### Energy Trading Firm
1. Upload historical natural gas prices
2. Generate 90-day forecast with Prophet
3. Value storage contracts with Monte Carlo
4. Export results for client reports

### Risk Management
1. Upload utility price data
2. Validate data quality
3. Run multiple forecast models
4. Calculate VaR and CVaR metrics

### Commodity Analysis
1. Upload crude oil prices
2. Auto-detect seasonality patterns
3. Compare forecast models
4. Optimize storage strategies

## 💡 Tips for Best Results

1. **Data Quality**: Clean data produces better forecasts
   - At least 2 years of history
   - Minimal missing values
   - Remove obvious errors

2. **Model Selection**:
   - **ARIMA**: Best for stationary data
   - **Prophet**: Best for strong seasonality
   - **Simple MA**: Quick baseline

3. **Validation**: Always check the test set performance

4. **Storage Valuation**: Realistic parameters produce reliable results

## 🚀 Quick Commands Reference

```bash
# Start dashboard
streamlit run dashboard/app.py

# Start API
uvicorn api.app:app --reload

# Run tests (if available)
pytest tests/

# Install specific model packages
pip install statsmodels pmdarima prophet

# Update packages
pip install -r requirements.txt --upgrade
```

## 📞 Support

For questions or issues:
1. Check this guide
2. Review documentation in `/docs`
3. Check error messages in console
4. Ensure all requirements are installed

---

**Happy Analyzing! 📊📈💰**
