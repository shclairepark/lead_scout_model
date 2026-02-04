import json
import random
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from src.tokenizer.sales_tokenizer import SalesTokenizer

def generate_dataset(num_samples=5000, output_file="data/training_data.json"):
    """
    Generate synthetic training data for LeadScoutModel.
    Combines 'Real-ish' profile stats with 'Synthetic' signals.
    """
    
    tokenizer = SalesTokenizer()
    dataset = []
    
    print(f"Generating {num_samples} samples...")
    
    for i in range(num_samples):
        # 1. Random Profile State (Features)
        # We simulate the lead_data dict expected by tokenizer
        lead_data = {
            "months_in_role": random.randint(1, 48),
            "funding_amount": random.choice([0, 500000, 2000000, 15000000, 50000000]),
            "own_views_3m": random.randint(0, 500),
            "own_views_1m": random.randint(0, 200),
            "comp_views_3m": random.randint(0, 50),
            "comp_views_1m": random.randint(0, 20),
        }
        
        # 2. Random Signals
        signals = []
        
        # Logic for Ground Truth Label
        # Base probability is low
        has_high_intent = False
        
        # Chance of signals
        if random.random() < 0.4: # 40% have signals
            # Pick a random signal type
            sig_types = [
                "content_engagement", "profile_visit", "funding_round", 
                "role_change", "demo_request", "pricing_page_visit"
            ]
            
            # Weighted choice
            chosen_sig = random.choices(sig_types, weights=[30, 30, 10, 10, 5, 15], k=1)[0]
            signals.append({"type": chosen_sig})
            
            # Logic: Demo or Pricing -> High Intent
            if chosen_sig in ["demo_request", "pricing_page_visit"]:
                has_high_intent = True
            
            # Logic: Funding -> Medium/High Intent
            if chosen_sig == "funding_round":
                has_high_intent = random.random() < 0.7
                
            # Multiple signals?
            if random.random() < 0.3:
                signals.append({"type": "content_engagement"})
                # Two signals -> Boost intent
                if random.random() < 0.5:
                    has_high_intent = True

        # 3. Determine Label
        label = 1.0 if has_high_intent else 0.0
        
        # 4. Tokenize
        tokens, token_ids = tokenizer.tokenize_lead(lead_data, signals)
        
        dataset.append({
            "tokens": tokens,
            "token_ids": token_ids,
            "label": label
        })
        
    # Save
    with open(output_file, "w") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"✅ Saved {len(dataset)} examples to {output_file}")
    
    # Analyze balance
    positives = sum(1 for d in dataset if d['label'] == 1.0)
    print(f"   Positive labels: {positives} ({positives/num_samples*100:.1f}%)")

if __name__ == "__main__":
    generate_dataset()
