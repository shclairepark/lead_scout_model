"""
Analyze Score Distribution from Demo Run
Quick script to understand what AI scores are being generated.
"""
import subprocess
import re
from collections import Counter

def run_demo_and_analyze(seed):
    """Run demo with given seed and extract AI scores."""
    cmd = f"python scripts/interactive_demo.py --auto-input data/customer_inputs.json --seed {seed}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=".")
    
    # Extract AI scores using regex
    pattern = r"AI Model Confidence: (\d+)%"
    scores = [int(match) for match in re.findall(pattern, result.stdout)]
    
    return scores

def main():
    print("Running demo with multiple seeds to analyze score distribution...")
    print("=" * 60)
    
    all_scores = []
    seeds = [12345, 42, 99999, 777, 54321]
    
    for seed in seeds:
        print(f"\nSeed {seed}:")
        scores = run_demo_and_analyze(seed)
        print(f"  Found {len(scores)} matches")
        if scores:
            print(f"  Scores: {scores}")
            all_scores.extend(scores)
        else:
            print("  No matches found")
    
    print("\n" + "=" * 60)
    print("AGGREGATE ANALYSIS")
    print("=" * 60)
    
    if all_scores:
        score_distribution = Counter(all_scores)
        print(f"\nTotal matched leads: {len(all_scores)}")
        print(f"\nScore Distribution:")
        for score in sorted(score_distribution.keys(), reverse=True):
            count = score_distribution[score]
            pct = count / len(all_scores) * 100
            bar = "█" * int(pct / 2)
            print(f"  {score}%: {count:2d} ({pct:5.1f}%) {bar}")
        
        print(f"\nStatistics:")
        print(f"  Min: {min(all_scores)}%")
        print(f"  Max: {max(all_scores)}%")
        print(f"  Avg: {sum(all_scores)/len(all_scores):.1f}%")
        print(f"  Unique scores: {len(score_distribution)}")
        
        # Check success criteria
        print(f"\n✅ Success Criteria:")
        high_count = sum(1 for s in all_scores if s >= 90)
        high_pct = high_count / len(all_scores) * 100
        print(f"  High (90-100%): {high_count}/{len(all_scores)} ({high_pct:.1f}%) - Target: ~10%")
        
        if high_pct > 15:
            print("  ⚠️  Too many high scores - need more tuning")
        else:
            print("  ✅ Within acceptable range")
    else:
        print("No scores found - demo may not be finding matches")

if __name__ == "__main__":
    main()
