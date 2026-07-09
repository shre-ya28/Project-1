"""
Customer Engagement & Product Utilization Analytics for Retention Strategy
----------------------------------------------------------------------------
Streamlit dashboard for The European Central Bank retention project.

Run locally:
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Engagement & Retention Analytics",
    page_icon="🏦",
    layout="wide",
)

# --------------------------------------------------------------------------
# Data loading & feature engineering
# --------------------------------------------------------------------------
@st.cache_data
def load_data(path="European_Bank.csv"):
    df = pd.read_csv(path)

    # Engagement profile classification
    conditions = [
        (df["IsActiveMember"] == 1) & (df["NumOfProducts"] >= 2),
        (df["IsActiveMember"] == 0),
        (df["IsActiveMember"] == 1) & (df["NumOfProducts"] == 1),
    ]
    choices = [
        "Active Engaged (Multi-Product)",
        "Inactive Disengaged",
        "Active but Low-Product",
    ]
    df["EngagementProfile"] = np.select(conditions, choices, default="Other")

    # Balance tiers (quartiles)
    df["BalanceTier"] = pd.qcut(
        df["Balance"].rank(method="first"), 4, labels=["Q1-Low", "Q2", "Q3", "Q4-High"]
    )

    # High-balance disengaged flag ("at-risk premium customers")
    balance_p75 = df["Balance"].quantile(0.75)
    df["AtRiskPremium"] = ((df["Balance"] >= balance_p75) & (df["IsActiveMember"] == 0)).astype(int)

    # Relationship Strength Index (simple composite, higher = stickier)
    df["RelationshipStrengthIndex"] = (
        df["IsActiveMember"] * 2
        + df["NumOfProducts"]
        + df["HasCrCard"]
        + (df["Tenure"] / df["Tenure"].max())
    )

    return df


DATA_PATH = st.sidebar.text_input(
    "Dataset path (CSV)", value="European_Bank.csv",
    help="Point this at European_Bank.csv, or place it next to this script."
)

try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Couldn't find '{DATA_PATH}'. Upload the file below or fix the path.")
    uploaded = st.file_uploader("Upload European_Bank.csv", type="csv")
    if uploaded is None:
        st.stop()
    df = load_data(uploaded)

# --------------------------------------------------------------------------
# Sidebar filters (User Capabilities: engagement filters, product sliders,
# balance / salary thresholds)
# --------------------------------------------------------------------------
st.sidebar.header("🔍 Filters")

geo_filter = st.sidebar.multiselect(
    "Geography", options=sorted(df["Geography"].unique()), default=sorted(df["Geography"].unique())
)
gender_filter = st.sidebar.multiselect(
    "Gender", options=sorted(df["Gender"].unique()), default=sorted(df["Gender"].unique())
)
engagement_filter = st.sidebar.multiselect(
    "Engagement Profile",
    options=sorted(df["EngagementProfile"].unique()),
    default=sorted(df["EngagementProfile"].unique()),
)
product_range = st.sidebar.slider(
    "Number of Products", int(df["NumOfProducts"].min()), int(df["NumOfProducts"].max()),
    (int(df["NumOfProducts"].min()), int(df["NumOfProducts"].max()))
)
balance_range = st.sidebar.slider(
    "Balance range", float(df["Balance"].min()), float(df["Balance"].max()),
    (float(df["Balance"].min()), float(df["Balance"].max()))
)
salary_range = st.sidebar.slider(
    "Estimated salary range", float(df["EstimatedSalary"].min()), float(df["EstimatedSalary"].max()),
    (float(df["EstimatedSalary"].min()), float(df["EstimatedSalary"].max()))
)
active_only = st.sidebar.selectbox("Activity status", ["All", "Active only", "Inactive only"])

f = df[
    df["Geography"].isin(geo_filter)
    & df["Gender"].isin(gender_filter)
    & df["EngagementProfile"].isin(engagement_filter)
    & df["NumOfProducts"].between(*product_range)
    & df["Balance"].between(*balance_range)
    & df["EstimatedSalary"].between(*salary_range)
]
if active_only == "Active only":
    f = f[f["IsActiveMember"] == 1]
elif active_only == "Inactive only":
    f = f[f["IsActiveMember"] == 0]

st.title("🏦 Customer Engagement & Product Utilization Analytics")
st.caption("Retention strategy dashboard — The European Central Bank")

if f.empty:
    st.warning("No customers match the current filters.")
    st.stop()

# --------------------------------------------------------------------------
# KPI row
# --------------------------------------------------------------------------
active_churn = f.loc[f.IsActiveMember == 1, "Exited"].mean() if (f.IsActiveMember == 1).any() else np.nan
inactive_churn = f.loc[f.IsActiveMember == 0, "Exited"].mean() if (f.IsActiveMember == 0).any() else np.nan
err = inactive_churn / active_churn if active_churn and active_churn > 0 else np.nan
hbdr = f.loc[f.AtRiskPremium == 1, "Exited"].mean() if (f.AtRiskPremium == 1).any() else np.nan
card_yes = f.loc[f.HasCrCard == 1, "Exited"].mean() if (f.HasCrCard == 1).any() else np.nan
card_no = f.loc[f.HasCrCard == 0, "Exited"].mean() if (f.HasCrCard == 0).any() else np.nan
rsi_corr = f["RelationshipStrengthIndex"].corr(f["Exited"])

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Overall Churn Rate", f"{f['Exited'].mean()*100:.1f}%")
k2.metric("Engagement Retention Ratio", f"{err:.2f}x" if pd.notna(err) else "N/A",
          help="Inactive churn rate ÷ active churn rate. >1 means inactive members churn more.")
k3.metric("High-Balance Disengagement Rate", f"{hbdr*100:.1f}%" if pd.notna(hbdr) else "N/A",
          help="Churn rate among top-quartile-balance customers who are inactive.")
k4.metric("Credit Card Stickiness", f"{(card_no - card_yes)*100:+.1f} pp" if pd.notna(card_yes) else "N/A",
          help="Churn-rate gap (no-card minus card) — positive means card holders churn less.")
k5.metric("Relationship Strength ↔ Churn", f"{rsi_corr:.2f}",
          help="Correlation between the Relationship Strength Index and churn (negative = stronger relationship, lower churn).")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Engagement vs Churn",
    "📦 Product Utilization",
    "💰 High-Value Disengaged Detector",
    "🧭 Retention Strength Scoring",
])

# --------------------------------------------------------------------------
# TAB 1 — Engagement vs churn overview
# --------------------------------------------------------------------------
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        eng = f.groupby("EngagementProfile")["Exited"].mean().reset_index()
        eng["Exited"] *= 100
        fig = px.bar(eng, x="EngagementProfile", y="Exited", color="EngagementProfile",
                     text_auto=".1f", title="Churn Rate by Engagement Profile (%)")
        fig.update_layout(showlegend=False, yaxis_title="Churn Rate (%)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        act = f.groupby("IsActiveMember")["Exited"].mean().reset_index()
        act["IsActiveMember"] = act["IsActiveMember"].map({0: "Inactive", 1: "Active"})
        act["Exited"] *= 100
        fig2 = px.bar(act, x="IsActiveMember", y="Exited", color="IsActiveMember",
                      text_auto=".1f", title="Churn Rate: Active vs Inactive (%)",
                      color_discrete_map={"Active": "#2a9d8f", "Inactive": "#e76f51"})
        fig2.update_layout(showlegend=False, yaxis_title="Churn Rate (%)", xaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        "**Reading this tab:** compare churn across engagement segments. Inactive customers "
        "consistently show the highest churn — engagement, not balance, is the leading indicator."
    )
    st.dataframe(
        f.groupby("EngagementProfile").agg(
            Customers=("CustomerId", "count"),
            ChurnRate=("Exited", "mean"),
            AvgBalance=("Balance", "mean"),
            AvgProducts=("NumOfProducts", "mean"),
        ).style.format({"ChurnRate": "{:.1%}", "AvgBalance": "€{:,.0f}", "AvgProducts": "{:.2f}"}),
        use_container_width=True,
    )

# --------------------------------------------------------------------------
# TAB 2 — Product utilization impact
# --------------------------------------------------------------------------
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        prod = f.groupby("NumOfProducts")["Exited"].agg(["mean", "count"]).reset_index()
        prod["mean"] *= 100
        fig3 = px.bar(prod, x="NumOfProducts", y="mean", text_auto=".1f",
                      title="Churn Rate by Number of Products (%)",
                      labels={"mean": "Churn Rate (%)", "NumOfProducts": "Number of Products"})
        st.plotly_chart(fig3, use_container_width=True)
    with c2:
        f["ProductMix"] = np.where(f["NumOfProducts"] == 1, "Single-Product", "Multi-Product")
        mix = f.groupby("ProductMix")["Exited"].mean().reset_index()
        mix["Exited"] *= 100
        fig4 = px.bar(mix, x="ProductMix", y="Exited", color="ProductMix", text_auto=".1f",
                      title="Single- vs Multi-Product Churn (%)")
        fig4.update_layout(showlegend=False, yaxis_title="Churn Rate (%)", xaxis_title="")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown(
        "**Insight:** 2-product holders are the stickiest segment. Churn rises sharply at "
        "3–4 products in this dataset — often a symptom of forced/bundled cross-sell rather "
        "than genuine engagement, and worth validating against sales-process data."
    )

# --------------------------------------------------------------------------
# TAB 3 — High-value disengaged customer detector
# --------------------------------------------------------------------------
with tab3:
    st.subheader("At-Risk Premium Customers")
    st.markdown(
        "Customers in the **top balance quartile** who are **currently inactive** — "
        "high value, low engagement, and the highest silent-churn risk."
    )
    at_risk_df = f[f["AtRiskPremium"] == 1].sort_values("Balance", ascending=False)
    c1, c2, c3 = st.columns(3)
    c1.metric("At-Risk Premium Customers", f"{len(at_risk_df):,}")
    c2.metric("Their Churn Rate", f"{at_risk_df['Exited'].mean()*100:.1f}%" if len(at_risk_df) else "N/A")
    c3.metric("Total Balance at Risk", f"€{at_risk_df['Balance'].sum():,.0f}")

    fig5 = px.scatter(
        f, x="Balance", y="EstimatedSalary", color="EngagementProfile",
        symbol="Exited", size="NumOfProducts",
        title="Balance vs Salary, colored by Engagement Profile (shape = churned)",
        opacity=0.6,
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("#### Ranked list of at-risk premium customers")
    st.dataframe(
        at_risk_df[["CustomerId", "Surname", "Geography", "Balance", "EstimatedSalary",
                    "NumOfProducts", "Tenure", "Exited"]].head(200),
        use_container_width=True,
    )

# --------------------------------------------------------------------------
# TAB 4 — Retention strength scoring
# --------------------------------------------------------------------------
with tab4:
    st.subheader("Relationship Strength Index (RSI)")
    st.markdown(
        "RSI = `2×IsActiveMember + NumOfProducts + HasCrCard + (Tenure / max Tenure)`. "
        "Higher scores indicate a deeper, stickier relationship."
    )
    fig6 = px.histogram(
        f, x="RelationshipStrengthIndex", color=f["Exited"].map({0: "Retained", 1: "Churned"}),
        barmode="overlay", nbins=30, title="RSI Distribution: Retained vs Churned",
        opacity=0.6,
    )
    st.plotly_chart(fig6, use_container_width=True)

    f["RSI_Bucket"] = pd.qcut(f["RelationshipStrengthIndex"].rank(method="first"), 4,
                               labels=["Weakest", "Weak", "Strong", "Strongest"])
    bucket = f.groupby("RSI_Bucket")["Exited"].mean().reset_index()
    bucket["Exited"] *= 100
    fig7 = px.bar(bucket, x="RSI_Bucket", y="Exited", text_auto=".1f",
                  title="Churn Rate by Relationship Strength Tier (%)")
    st.plotly_chart(fig7, use_container_width=True)

    st.markdown(
        "**Sticky customer profile:** active, holds 2 products, has a credit card, and longer "
        "tenure. This segment shows the lowest churn across the whole portfolio."
    )

st.divider()
st.caption(
    "Unified Mentor · Customer Engagement & Product Utilization Analytics for Retention Strategy · "
    "The European Central Bank"
)
