# 🔋 Universal Utility Risk Analytics Platform (UURAP)

**From historical data to optimized storage strategies - for any utility**

## 📋 Overview

UURAP is a production-ready platform that provides comprehensive forecasting, valuation, and optimization for ANY utility commodity including electricity, natural gas, oil, water, and more.

## ✨ Key Features

- 📊 **Auto-detect utility type and seasonality**
- 📈 **Multi-model forecasting engine** (ARIMA, Prophet, Regression, Ensemble)
- 💰 **Generic storage contract valuation** with Monte Carlo simulation
- 🎯 **Strategy optimization** for any commodity
- 📱 **Interactive web dashboard** built with Streamlit
- 📄 **Automated reporting** and analytics
- 🔌 **RESTful API** for integration

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd utility_analytics_platform

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

### Running the Dashboard

```bash
streamlit run dashboard/app.py
```

### Running the API

```bash
uvicorn api.app:app --reload
```

### Using Docker

```bash
docker-compose up
```

## 📊 Data Format

Upload CSV files with the following columns:
- `date` (YYYY-MM-DD format)
- `price` (numeric)
- Optional: `volume`, `temperature`, `demand`, etc.

See [CSV_FORMAT_SPEC.md](docs/CSV_FORMAT_SPEC.md) for detailed specifications.

## 🎯 Use Cases

- **Energy Trading**: Optimize natural gas and electricity storage strategies
- **Commodity Trading**: Value crude oil storage contracts
- **Risk Management**: Assess portfolio risk and exposure
- **Forecasting**: Predict future prices with multiple models
- **Scenario Analysis**: Test different market conditions

## 📖 Documentation

- [User Guide](docs/USER_GUIDE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [CSV Format Specification](docs/CSV_FORMAT_SPEC.md)
- [Examples](docs/EXAMPLES.md)

## 🛠️ Technology Stack

- **Python 3.9+**
- **FastAPI**: RESTful API
- **Streamlit**: Interactive dashboard
- **pandas**: Data manipulation
- **scikit-learn**: Machine learning
- **Prophet**: Time series forecasting
- **statsmodels**: Statistical models
- **plotly**: Interactive visualizations
- **Docker**: Containerization

## 📁 Project Structure

```
utility_analytics_platform/
├── src/              # Core source code
├── api/              # FastAPI backend
├── dashboard/        # Streamlit frontend
├── data/             # Data files
├── tests/            # Unit tests
├── notebooks/        # Jupyter notebooks
└── docs/             # Documentation
```

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

## 📄 License

MIT License

## 🙋 Support

For issues and questions, please open a GitHub issue.
