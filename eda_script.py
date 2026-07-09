import pandas as pd, numpy as np

df = pd.read_csv('/mnt/user-data/uploads/European_Bank.csv')
print(df.shape)
print(df.dtypes)
print(df.isnull().sum())
print(df['Exited'].value_counts(normalize=True))

# Engagement profiles
df['EngagementProfile'] = np.select(
    [
        (df['IsActiveMember']==1) & (df['NumOfProducts']>=2),
        (df['IsActiveMember']==0),
        (df['IsActiveMember']==1) & (df['NumOfProducts']==1),
    ],
    ['Active Engaged (Multi-Product)', 'Inactive Disengaged', 'Active but Low-Product'],
    default='Other'
)
# Inactive high balance flag
df['InactiveHighBalance'] = ((df['IsActiveMember']==0) & (df['Balance'] > df['Balance'].median())).astype(int)

print("\n--- Churn by Engagement Profile ---")
print(df.groupby('EngagementProfile')['Exited'].agg(['mean','count']))

print("\n--- Churn by NumOfProducts ---")
print(df.groupby('NumOfProducts')['Exited'].agg(['mean','count']))

print("\n--- Churn by IsActiveMember ---")
print(df.groupby('IsActiveMember')['Exited'].agg(['mean','count']))

print("\n--- Churn by HasCrCard ---")
print(df.groupby('HasCrCard')['Exited'].agg(['mean','count']))

print("\n--- Balance vs Activity crosstab (mean churn) ---")
df['BalanceTier'] = pd.qcut(df['Balance'].rank(method='first'), 4, labels=['Q1-Low','Q2','Q3','Q4-High'])
print(df.groupby(['BalanceTier','IsActiveMember'])['Exited'].mean())

print("\n--- High balance disengaged (premium at risk) ---")
premium_thresh = df['Balance'].quantile(0.75)
salary_thresh = df['EstimatedSalary'].quantile(0.75)
at_risk = df[(df['Balance']>=premium_thresh) & (df['IsActiveMember']==0)]
print("At-risk premium customers:", len(at_risk), "Churn rate:", at_risk['Exited'].mean())

print("\n--- Geography churn ---")
print(df.groupby('Geography')['Exited'].agg(['mean','count']))

print("\n--- Gender churn ---")
print(df.groupby('Gender')['Exited'].agg(['mean','count']))

print("\n--- Age vs churn (bins) ---")
df['AgeBin'] = pd.cut(df['Age'], [17,30,40,50,60,100])
print(df.groupby('AgeBin')['Exited'].agg(['mean','count']))

print("\n--- Tenure vs churn ---")
print(df.groupby('Tenure')['Exited'].agg(['mean','count']))

# KPI computations
active_churn = df[df.IsActiveMember==1]['Exited'].mean()
inactive_churn = df[df.IsActiveMember==0]['Exited'].mean()
err = inactive_churn/active_churn if active_churn>0 else np.nan
print("\nEngagement Retention Ratio (inactive/active churn):", err)

pdi = df.groupby('NumOfProducts')['Exited'].mean()
print("Product Depth Index (churn by product count):\n", pdi)

hbdr = at_risk['Exited'].mean()
print("High-Balance Disengagement Rate:", hbdr)

card_churn_yes = df[df.HasCrCard==1]['Exited'].mean()
card_churn_no = df[df.HasCrCard==0]['Exited'].mean()
print("Credit Card Stickiness -> churn w/ card:", card_churn_yes, " w/o card:", card_churn_no)

df['RelationshipStrengthIndex'] = df['IsActiveMember']*2 + df['NumOfProducts'] + df['HasCrCard'] + (df['Tenure']/df['Tenure'].max())
print("\nRSI vs churn correlation:", df['RelationshipStrengthIndex'].corr(df['Exited']))

df.to_csv('/home/claude/analysis/enriched_dataset.csv', index=False)
print("\nSaved enriched dataset")
