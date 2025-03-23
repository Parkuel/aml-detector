# 🔍 Suspicious Transaction Detector App (Mini AML System)

An interactive AML tool built with Streamlit and Python that detects and visualizes suspicious financial transactions. Designed to showcase data analysis, Python automation, and compliance knowledge.

---

## 🚀 Features

- Upload transaction CSV files
- Flag suspicious transactions using:
  - 💰 Large transaction threshold
  - 🧩 Structuring detection
  - 🌍 High-risk country screening
- View flagged transactions in a table
- Interactive dashboard with metrics, bar & pie charts
- Auto-generated summary of suspicious activity
- Download results as CSV

---

## 📊 Detection Logic

| Rule | Description |
|------|-------------|
| Large Transaction | Flags any transaction over $10,000 |
| Structuring | Detects multiple transactions from the same sender in 24 hours that total over $10,000 |
| High-Risk Country | Flags transactions from/to countries like Iran, Syria, North Korea |

---

## 📁 Sample CSV Format

Make sure your CSV contains the following columns:

```csv
transaction_id,sender_id,receiver_id,amount,country,date
T001,A100,B200,12000,USA,2025-03-20 10:00:00
...
