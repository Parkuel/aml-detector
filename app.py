import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# App Title
st.title("🔍 Suspicious Transaction Detector (Mini AML App)")

# File Upload
uploaded_file = st.file_uploader("Upload your transactions CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=["date"])
    st.success("File uploaded successfully!")

    # Show preview
    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head())

    # Detection Rules
    LARGE_TX_THRESHOLD = 10000
    STRUCTURING_WINDOW_HOURS = 24
    HIGH_RISK_COUNTRIES = ["North Korea", "Iran", "Syria", "Afghanistan"]

    df["flag_large_tx"] = df["amount"] > LARGE_TX_THRESHOLD
    df["flag_high_risk_country"] = df["country"].isin(HIGH_RISK_COUNTRIES)
    df["flag_structuring"] = False

    df_sorted = df.sort_values(by=["sender_id", "date"])

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

    df["suspicious"] = df[["flag_large_tx", "flag_high_risk_country", "flag_structuring"]].any(axis=1)
    flagged = df[df["suspicious"]]

    # 🚩 Flagged Transactions Table
    st.subheader("🚩 Flagged Transactions")
    st.dataframe(flagged)

    # 📊 Summary Count
    st.subheader("📊 Suspicious Transaction Summary")
    st.write(flagged["suspicious"].value_counts())

    # 📈 Dashboard Overview
    st.subheader("📈 Transaction Overview Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Transactions", len(df))

    with col2:
        st.metric("Total Volume ($)", f"${df['amount'].sum():,.2f}")

    with col3:
        suspicious_count = df["suspicious"].sum()
        suspicious_percent = (suspicious_count / len(df)) * 100
        st.metric("Suspicious Transactions", f"{suspicious_count} ({suspicious_percent:.1f}%)")

    # 📊 Suspicious by Rule (Bar Chart)
    st.subheader("🧠 Suspicious Transactions by Rule")

    rule_counts = {
        "Large Transaction": df["flag_large_tx"].sum(),
        "Structuring": df["flag_structuring"].sum(),
        "High-Risk Country": df["flag_high_risk_country"].sum()
    }

    rule_df = pd.DataFrame.from_dict(rule_counts, orient='index', columns=["Count"]).reset_index()
    rule_df.columns = ["Rule", "Count"]

    fig = px.bar(rule_df, x="Rule", y="Count", title="Suspicious Transactions per Rule", color="Rule")
    st.plotly_chart(fig)

    # 🌍 Suspicious by Country (Pie Chart)
    st.subheader("🌍 Suspicious Transactions by Country")
    suspicious_by_country = df[df["suspicious"]].groupby("country")["transaction_id"].count().reset_index()
    suspicious_by_country.columns = ["Country", "Suspicious Count"]

    if not suspicious_by_country.empty:
        fig2 = px.pie(suspicious_by_country, values="Suspicious Count", names="Country", title="Suspicious Activity by Country")
        st.plotly_chart(fig2)
    else:
        st.info("No suspicious transactions to display by country.")

    # 📝 Narrative Summary
    st.subheader("📝 Data Narrative Summary")

    total_tx = len(df)
    suspicious_tx = flagged.shape[0]
    suspicious_pct = (suspicious_tx / total_tx) * 100

    top_countries = (
        flagged["country"]
        .value_counts()
        .head(3)
        .to_dict()
    )

    summary_text = f"""
    Out of **{total_tx}** transactions, **{suspicious_tx}** ({suspicious_pct:.1f}%) were flagged as suspicious.

    🔸 **Flagged by Rule**:
    - Large Transactions: {rule_counts['Large Transaction']}
    - Structuring: {rule_counts['Structuring']}
    - High-Risk Countries: {rule_counts['High-Risk Country']}

    🌍 **Top Countries with Suspicious Activity**:
    """

    for country, count in top_countries.items():
        summary_text += f"- {country}: {count} cases\n"

    st.markdown(summary_text)

    # 📥 Download Button
    st.subheader("📥 Download Results")
    st.download_button("Download Flagged CSV", data=flagged.to_csv(index=False), file_name="flagged_transactions.csv")
