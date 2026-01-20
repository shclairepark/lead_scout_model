import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import os

def load_data(filepath):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Data file not found at {filepath}. Please run data/data_generator.py first.")
        return None

def preprocess_data(df):
    """Log transform funding amount."""
    df = df.copy()
    df['funding_amount'] = np.log1p(df['funding_amount'])
    return df

def feature_engineering(df):
    """Create momentum and competitive intensity features."""
    df = df.copy()
    
    # 1. Feature: "Momentum" (Recency Bias)
    # Adding 1 to denominator to avoid division by zero if views are 0
    df['own_surge_ratio'] = df['own_views_1m'] / (df['own_views_3m'] / 3 + 1)
    
    # 2. Feature: "Competitive Intensity"
    df['comp_intensity'] = df['comp_views_1m'] + df['comp_views_3m']
    
    return df

def train_model(X, y):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression()
    model.fit(X_scaled, y)
    
    return model, scaler

if __name__ == "__main__":
    # Get the path to the data file relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'leads_raw.csv')

    df = load_data(data_path)
    if df is not None:
        df = preprocess_data(df)
        df = feature_engineering(df)

        # 3. Standardize as before
        features = ['months_in_role', 'funding_amount', 'own_surge_ratio', 'comp_intensity']
        X = df[features]
        y = df['replied']

        model, scaler = train_model(X, y)

        # 5. Output Results
        weights = dict(zip(features, model.coef_[0]))
        print("--- MODEL INTERPRETATION ---")
        for feature, weight in weights.items():
            direction = "INCREASES" if weight > 0 else "DECREASES"
            print(f"Signal: {feature:15} | Weight: {weight:6.2f} | Impact: {direction} reply chance")

        # 6. Predict on a New "Secret" Lead
        # [3 months in role, $1M funding, 1.0 surge ratio, 0.9 intensity]
        test_lead = np.array([[3, np.log1p(1000000), 1.0, 0.9]])
        test_lead_scaled = scaler.transform(test_lead)
        prob = model.predict_proba(test_lead_scaled)[0][1]

        print(f"\n--- INFERENCE ---")
        print(f"New Lead Reply Probability: {prob:.2%}")
        if prob > 0.65:
            print("ACTION: 🔥 Spend Credit - High Likelihood!")
        else:
            print("ACTION: ❄️ Ignore - Low Intent.")
