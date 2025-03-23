import pandas as pd
from datetime import timedelta

# Load dataset
df = pd.read_csv("transactions.csv", parse_dates=["date"])

# Rule thresholds/config
LARGE_TX_THRESHOLD = 10000
STRUCTURING_WINDOW_HOURS = 24
HIGH_RISK_COUNTRIES = ["North Korea", "Iran", "Syria", "Afghanistan"]

# Add flag columns
df["flag_large_tx"] = df["amount"] > LARGE_TX_THRESHOLD
df["flag_high_risk_country"] = df["country"].isin(HIGH_RISK_COUNTRIES)
df["flag_structuring"] = False  # Initialize

# Structuring Rule: Multiple small tx in short window from same sender
df_sorted = df.sort_values(by=["sender_id", "date"])

# Loop through each sender
for sender in df_sorted["sender_id"].unique():
    sender_tx = df_sorted[df_sorted["sender_id"] == sender]
    for i in range(len(sender_tx)):
        window_tx = sender_tx[
            (sender_tx["date"] >= sender_tx.iloc[i]["date"]) &
            (sender_tx["date"] <= sender_tx.iloc[i]["date"] + timedelta(hours=STRUCTURING_WINDOW_HOURS))
        ]
        total_amount = window_tx["amount"].sum()
        if total_amount > LARGE_TX_THRESHOLD and len(window_tx) > 1:
            df.loc[window_tx.index, "flag_structuring"] = True

# Final flag: any rule triggered
df["suspicious"] = df[["flag_large_tx", "flag_high_risk_country", "flag_structuring"]].any(axis=1)

# Save results
df.to_csv("flagged_transactions.csv", index=False)

# Print summary
print("Suspicious Transactions Summary:")
print(df["suspicious"].value_counts())
print("Flagged transactions saved to flagged_transactions.csv")
