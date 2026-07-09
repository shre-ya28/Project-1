# Customer Engagement & Product Utilization Analytics for Retention Strategy

Behavioral churn analytics for a retail bank (Unified Mentor / "The European Central Bank" case study). Instead of asking *who has money*, this project asks *who is engaged* — and shows that engagement and product depth predict churn far better than balance or salary alone.

## 🔑 Key Result

| KPI | Result |
|---|---|
| Overall churn rate | 20.4% |
| Engagement Retention Ratio (inactive ÷ active churn) | **1.88x** |
| Stickiest segment (active, 2 products) | 7.6% churn |
| At-risk premium customers (top-quartile balance, inactive) | 1,247 customers · 30.5% churn |
| Highest-churn geography | Germany (32.4%) |
| Highest-risk age band | 50–60 (56.2% churn) |

Full write-up in [`research_paper/Research_Paper.docx`](research_paper/Research_Paper.docx).

## 📁 Repository Structure

```
customer-engagement-retention-analytics/
├── app/
│   ├── streamlit_app.py       # Live dashboard (4 modules, sidebar filters)
│   ├── requirements.txt
│   └── European_Bank.csv      # (or point the app at /data via sidebar path input)
├── data/
│   ├── European_Bank.csv      # Raw dataset (10,000 customers)
│   └── eda_script.py          # Standalone EDA / KPI computation script
├── research_paper/
│   ├── Research_Paper.docx    # Full EDA, methodology, insights, recommendations
│   └── Executive_Summary.docx # 1-page summary for stakeholders
├── docs/
│   └── chart*.png             # Exported chart images used in the report
├── README.md
└── LICENSE
```

## 🚀 Running the Dashboard

```bash
cd app
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app has four modules, matching the project brief:

1. **Engagement vs Churn Overview** — churn by engagement profile and activity status
2. **Product Utilization Impact** — churn by product count, single- vs multi-product retention
3. **High-Value Disengaged Customer Detector** — ranked list + scatter of at-risk premium customers
4. **Retention Strength Scoring** — Relationship Strength Index distribution and churn-by-tier

Sidebar filters: geography, gender, engagement profile, product-count slider, balance/salary thresholds, activity status.

## 📊 Methodology (short version)

1. **Ingestion & validation** — schema check, null check, binary-field and churn-label validation
2. **Engagement classification** — Active Engaged (Multi-Product) / Active but Low-Product / Inactive Disengaged
3. **Product utilization analysis** — churn by `NumOfProducts`, single vs multi-product retention
4. **Financial commitment vs engagement** — balance-tier × activity cross-analysis, at-risk premium detection
5. **Retention strength assessment** — composite Relationship Strength Index (RSI) and its correlation with churn

See `data/eda_script.py` for the reproducible analysis and `research_paper/Research_Paper.docx` for the full narrative.

## 🧮 KPI Definitions

- **Engagement Retention Ratio** = inactive-customer churn rate ÷ active-customer churn rate
- **Product Depth Index** = churn rate at each `NumOfProducts` level
- **High-Balance Disengagement Rate** = churn rate among top-quartile-balance, inactive customers
- **Credit Card Stickiness Score** = churn-rate gap between non-card and card holders
- **Relationship Strength Index** = `2×IsActiveMember + NumOfProducts + HasCrCard + (Tenure / max Tenure)`

## 🛠️ Tech Stack

Python · pandas · NumPy · Streamlit · Plotly · matplotlib/seaborn (report charts) · python-docx/docx-js (report generation)

## 📌 GitHub Repo Ideas

**Repo name options** (pick one — all are available-style, descriptive, and SEO-friendly for a portfolio):
- `customer-engagement-retention-analytics`
- `bank-churn-engagement-dashboard`
- `retention-strategy-analytics` (short, punchy)
- `silent-churn-detector` (leads with the most interesting finding)
- `european-bank-retention-insights`

**Suggested repo description:**
> Behavioral churn analytics for retail banking — identifies "silent churn" among high-balance, disengaged customers using engagement profiling, product-depth analysis, and a custom Relationship Strength Index. Includes a live Streamlit dashboard.

**Suggested GitHub topics/tags:**
`churn-prediction` `customer-retention` `streamlit-dashboard` `banking-analytics` `eda` `plotly` `pandas` `data-storytelling` `customer-engagement` `fintech`

**README badges to add once pushed:**
- Streamlit Cloud "Open in Streamlit" badge (deploy `app/streamlit_app.py` directly)
- Python version badge
- License badge

**Nice-to-have follow-ups for the repo (stretch goals, good for commit history / portfolio depth):**
- Add a `notebooks/` folder with a Jupyter notebook version of the EDA for reviewers who prefer notebooks over scripts
- Add a simple churn-prediction model (logistic regression / XGBoost) with SHAP explainability as a v2 branch
- Deploy the dashboard on Streamlit Community Cloud and link it at the top of the README
- Add GitHub Actions to lint (`ruff`/`flake8`) and smoke-test the Streamlit app on push
