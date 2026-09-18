# EDA summary — Telco Customer Churn (real data)

- Rows after cleaning: 7032
- Churn rate: 26.578% (class imbalance -- expect this to land ~26-27%, matches the known public benchmark for this dataset)
- Columns: 21

## Churn rate by contract type
- Month-to-month: 42.710% (n=3875)
- One year: 11.277% (n=1472)
- Two year: 2.849% (n=1685)

## Numeric column ranges (real columns only)
- tenure: min=1.00, max=72.00, mean=32.42
- MonthlyCharges: min=18.25, max=118.75, mean=64.80
- TotalCharges: min=18.80, max=8684.80, mean=2283.30