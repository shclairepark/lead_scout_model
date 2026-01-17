import pandas as pd
import numpy as np

np.random.seed(42)
n_leads = 10000

# 1. Base Signals
months_in_role = np.random.randint(1, 60, n_leads)
funding_amount = np.random.choice([0, 1e6, 5e6, 2e7, 1e8], n_leads, p=[0.4, 0.3, 0.15, 0.1, 0.05])

# 2. Raw Time-Series Activity (The "Messy" Signals)
comp_views_3m = np.random.poisson(2, n_leads)
comp_views_1m = np.random.poisson(0.6, n_leads)
own_views_3m = np.random.poisson(1.5, n_leads)
own_views_1m = np.random.poisson(0.4, n_leads)

# 3. Hidden "Interaction" Logic (What the Transformer will find)
# Interaction A: Funding is only effective if they are new in the role (< 12 months)
new_funding_boost = np.where((months_in_role < 12) & (funding_amount > 0), 2.5, 0)

# Interaction B: Competitor views are only a threat/signal if OWN views are low
competitive_threat = np.where((comp_views_1m > 2) & (own_views_1m == 0), 1.5, 0)

# Interaction C: "The Double Surge" (Both own and competitor views up = active buyer)
double_surge = np.where((own_views_1m > 1) & (comp_views_1m > 1), 3.0, 0)

# 4. Calculate Final Probability (Logit)
logit = (
    (new_funding_boost) + 
    (double_surge) + 
    (competitive_threat) +
    (own_views_1m * 2.0) -       # Individual signal strength
    (0.08 * months_in_role) -    # Decay
    3.0                          # Bias (Hard to get a reply)
)

prob = 1 / (1 + np.exp(-logit))
replied = np.where(prob > np.random.uniform(0, 1, n_leads), 1, 0)

# 5. Build DataFrame
df = pd.DataFrame({
    'months_in_role': months_in_role,
    'funding_amount': funding_amount,
    'comp_views_3m': comp_views_3m,
    'comp_views_1m': comp_views_1m,
    'own_views_3m': own_views_3m,
    'own_views_1m': own_views_1m,
    'replied': replied
})

df.to_csv('data/leads_raw.csv', index=False)
print(f"🚀 Success: 10,000 leads generated in data/leads_raw.csv")
print(f"📊 Average Reply Rate: {df.replied.mean():.2%}")