# Lead Scout Model 

The model is to determine whether data lead would reply (positive) to the sender (sales, saas founder are target users).

## Phase 0: The Logistic Regression model (The Baseline model).

## Detailed Weekly Breakdown

### Block 1: The Signal Foundation (Weeks 1-2)

**Phase 1: Build your SalesTokenizer.**
Instead of "Lead Score = 80," represent a lead as a coordinate in space.

**Phase 2: Add the "Time" element.**
Implement Positional Encoding so the model knows a signal from 2 hours ago is worth more than one from 2 months ago.

### Block 2: The Logic Deep-Dive (Weeks 3-5)

**Phase 3: This is the "Aha!" moment.**
Implement Self-Attention.

**Phase 4: Stack your layers.**
Build a Mini-Transformer for sales.

### Block 3: The Outreach Strategy (Weeks 6-8)

**Phase 5-6: Control the output.**
Implement a Sampler to adjust "Creativity" (Temperature) so your outreach doesn't sound like a bot.

**Phase 7-9: Optimization.**
Implement KV Caching and Mixture of Experts.
*   **Goal:** The Agent should route "SaaS Founders" to a different logic path than "Enterprise VPs."

### Block 4: Brand Alignment (Weeks 9-11)

**Phase 10: Stability.**
Implement LayerNorm so your model doesn't "explode" (outputting gibberish) when training.

**Phase 11-12: The "Human Touch."**
Perform Instruction Tuning.

### Block 5: The Stress Test (Weeks 12-14)

**Phase 13-14: Speed.**
Quantize your model.
*   **Goal:** Make the model small enough to run on your laptop rather than a $2,000/mo cloud GPU.

**Phase 15-16: Final.**
Generate Synthetic Leads designed to trick the model.
*   **Success Metric:** Your "Credit Waste" (Loss) should drop by at least 50% compared to your Phase 0 baseline.

## Directory Structure

```
lead-scout-model/
├── data/           # Raw signals, CSVs, synthetic lead data
├── notebooks/      # Where you build the basic Logistic Regression (Scorer)
├── src/            # The "Hard Way" implementation
│   ├── tokenizer/  # Phase 1: BPE / Vocab files
│   ├── model/      # Phase 3-10: Transformer Blocks, QKV logic
│   ├── inference/  # Phase 6: KV Cache & Sampling
│   └── trainer.py  # Phase 11-12: Training loops & RLHF logic
├── configs/        # Model hyperparameters (n_layers, n_heads)
└── README.md       # Your roadmap and "insight" logs
```
