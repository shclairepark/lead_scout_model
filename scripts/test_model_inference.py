"""
Test Model Inference
Quick script to validate that the LeadScoutModel is producing varied outputs.
"""
import sys
import os
import torch

sys.path.append(os.getcwd())

from src.model.lead_scout import LeadScoutModel
from src.tokenizer.sales_tokenizer import SalesTokenizer

def test_model_variance():
    """Test if model produces varied outputs for different inputs."""
    
    tokenizer = SalesTokenizer()
    vocab_size = len(tokenizer.vocab)
    
    # Load model
    model = LeadScoutModel(
        vocab_size=vocab_size,
        embed_dim=64,
        num_heads=2,
        num_layers=2,
        ff_dim=128
    )
    
    checkpoint_path = "checkpoints/lead_scout_best.pth"
    if os.path.exists(checkpoint_path):
        model.load_state_dict(torch.load(checkpoint_path))
        model.eval()
        print("✅ Model loaded successfully")
    else:
        print("❌ No checkpoint found")
        return
    
    # Test cases
    test_cases = [
        # Case 1: No signals (should be low)
        {
            "lead_data": {"months_in_role": 12, "funding_amount": 0, "own_views_3m": 0},
            "signals": []
        },
        # Case 2: Demo request (should be high)
        {
            "lead_data": {"months_in_role": 12, "funding_amount": 0, "own_views_3m": 0},
            "signals": [{"type": "demo_request"}]
        },
        # Case 3: Funding (should be medium-high)
        {
            "lead_data": {"months_in_role": 12, "funding_amount": 15000000, "own_views_3m": 0},
            "signals": [{"type": "funding_round"}]
        },
        # Case 4: Just content engagement (should be low-medium)
        {
            "lead_data": {"months_in_role": 12, "funding_amount": 0, "own_views_3m": 0},
            "signals": [{"type": "content_engagement"}]
        },
        # Case 5: Multiple signals
        {
            "lead_data": {"months_in_role": 12, "funding_amount": 0, "own_views_3m": 0},
            "signals": [{"type": "content_engagement"}, {"type": "profile_visit"}]
        },
    ]
    
    print("\n" + "=" * 60)
    print("TESTING MODEL INFERENCE VARIANCE")
    print("=" * 60)
    
    results = []
    for i, case in enumerate(test_cases):
        tokens, token_ids = tokenizer.tokenize_lead(
            case["lead_data"], 
            case["signals"]
        )
        
        input_tensor = torch.tensor([token_ids], dtype=torch.long)
        
        with torch.no_grad():
            prob = model(input_tensor).item()
        
        results.append(prob)
        
        print(f"\nTest Case {i+1}:")
        print(f"  Signals: {[s['type'] for s in case['signals']]}")
        print(f"  Tokens: {tokens}")
        print(f"  Prediction: {prob*100:.1f}%")
    
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    
    variance = torch.tensor(results).var().item()
    print(f"Variance: {variance:.4f}")
    print(f"Min: {min(results)*100:.1f}%")
    print(f"Max: {max(results)*100:.1f}%")
    print(f"Range: {(max(results) - min(results))*100:.1f}%")
    
    if variance < 0.01:
        print("\n⚠️  WARNING: Model has very low variance!")
        print("   The model may be collapsed or overtrained.")
    else:
        print("\n✅ Model shows reasonable variance")

if __name__ == "__main__":
    test_model_variance()
