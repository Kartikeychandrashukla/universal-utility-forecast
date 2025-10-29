# Data Format Guide

## Overview
This guide explains the expected CSV format for uploading utility data to the Universal Utility Risk Analytics Platform.

## Required Columns

### Minimum Required Fields
Every CSV file must contain at least these two columns:

1. **date** (required)
   - Format: YYYY-MM-DD (e.g., 2022-01-15)
   - Alternative formats supported: YYYY/MM/DD, DD-MM-YYYY, DD/MM/YYYY
   - Must be parseable by pandas

2. **price** (required)
   - Numeric value representing the utility price
   - Can include decimals
   - No currency symbols or commas

## Optional Columns

You can include any of the following optional columns to enhance analysis:

- **volume**: Trading or consumption volume
- **demand**: Demand quantity
- **supply**: Supply quantity
- **temperature**: Temperature data for seasonal analysis
- **storage_level**: Current storage inventory
- **production**: Production quantity
- **consumption**: Consumption quantity

## Example Formats

### Natural Gas Example
```csv
date,price,volume,temperature
2022-01-01,3.45,12500,35
2022-01-02,3.52,13200,32
2022-01-03,3.48,12800,34
```

### Electricity Example
```csv
date,price,demand,temperature
2022-01-01,45.50,85000,35
2022-01-02,46.20,87000,33
2022-01-03,47.10,89000,31
```

### Crude Oil Example
```csv
date,price,volume
2022-01-01,75.25,250000
2022-01-02,75.50,252000
2022-01-03,75.80,255000
```

### Water Utility Example
```csv
date,price,consumption,temperature
2022-01-01,2.15,50000,75
2022-01-02,2.18,51000,76
2022-01-03,2.20,52000,78
```

## Data Requirements

### Quality Requirements
- **No missing dates**: Fill gaps or use interpolation
- **No missing prices**: Price column cannot have null values
- **Consistent frequency**: Daily, weekly, or monthly (daily preferred)
- **Minimum history**: At least 365 days for accurate forecasting

### File Requirements
- **Format**: CSV, XLSX, or JSON
- **Size**: Maximum 100 MB
- **Encoding**: UTF-8
- **Separator**: Comma (,) for CSV files

## Tips for Best Results

1. **More data is better**: At least 2-3 years of history recommended
2. **Include contextual data**: Temperature, demand, etc. improve forecasts
3. **Clean your data**: Remove outliers and errors before upload
4. **Consistent naming**: Use the exact column names specified above
5. **Regular frequency**: Daily data produces the most accurate results

## Auto-Detection

The platform automatically detects:
- Utility type (gas, electricity, oil, water)
- Seasonality patterns
- Data frequency
- Available features

You don't need to specify the utility type manually - the system will identify it based on:
- Price patterns
- Seasonality characteristics
- Column names
- Price range and volatility

## Validation

Upon upload, the system will:
1. Check for required columns
2. Validate date formats
3. Check for missing values
4. Identify outliers
5. Verify minimum data requirements
6. Display data quality report

## Troubleshooting

### Common Issues

**"Date column not found"**
- Ensure your date column is named exactly "date" (lowercase)
- Check for leading/trailing spaces in column names

**"Price column not found"**
- Ensure your price column is named exactly "price" (lowercase)
- Check for leading/trailing spaces

**"Invalid date format"**
- Use YYYY-MM-DD format
- Check for inconsistent date formats within the file

**"Insufficient data"**
- Provide at least 365 days of data
- Check for large gaps in dates

**"Too many missing values"**
- Fill missing prices using interpolation
- Ensure at least 95% of price data is present

## Support

For additional help or questions about data formatting, please refer to the main documentation or open an issue on GitHub.
