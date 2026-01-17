# Lead Scout Agents: TDD & Implementation Plan

This document outlines the Test-Driven Development (TDD) strategy for building the Lead Scout Model. We treat each phase as a distinct "Agent" or module that must pass rigorous tests before integration.

## 🛠 Phase 0: The Baseline (Logistic Regression)
**Current Status:** ✅ Implemented (`base_model.py`)
**Review:**
- `data_generator.py`: Generates synthetic signal data.
- `base_model.py`: Implements rudimentary feature engineering and Logistic Regression.
- **Action Item:** Ensure `base_model.py` uses consistent transformations (e.g., log-transform funding) during both training and inference.

---

## 🏗 Block 1: The Signal Foundation (Weeks 1-2)

### Agent 1: The SalesTokenizer (Phase 1)
**Goal:** Represent leads as dense vectors (embeddings) rather than raw scores.
**Hard Way Task:** Implement Cosine Similarity from scratch.

#### TDD Specs (`tests/test_tokenizer.py`)
*   **Test 1: Vectorization**
    *   Input: `{"title": "VP of Sales", "funding": 1e6}`
    *   Expected: A numpy array of shape `(d_model,)`.
*   **Test 2: Cosine Similarity**
    *   Input: Vector A ("Profile View"), Vector B ("Hiring")
    *   Assertion: `similarity(A, B)` should return a float between -1 and 1.
    *   Assertion: `similarity(A, A)` should be approx `1.0`.
*   **Test 3: Orthogonality (Sanity Check)**
    *   Input: Two completely unrelated signals.
    *   Expected: Similarity near 0.

### Agent 2: Chronos (Signal Timing) (Phase 2)
**Goal:** Implement Positional Encoding to weight recent signals higher.

#### TDD Specs (`tests/test_chronos.py`)
*   **Test 1: Decay Function**
    *   Input: Signal A (T=0 hours), Signal B (T=24 hours).
    *   Expected: Weight(A) > Weight(B).
*   **Test 2: Positional Encoding Matrix**
    *   Input: Sequence length `L`.
    *   Expected: Matrix `PE` of shape `(L, d_model)` where values follow sine/cosine frequencies.

---

## 🧠 Block 2: The Logic Deep-Dive (Weeks 3-5)

### Agent 3: Attention Mechanism (Phase 3)
**Goal:** Hand-code Self-Attention to find relationships between signals (e.g., Funding -> Title).

#### TDD Specs (`tests/test_attention.py`)
*   **Test 1: Scaled Dot-Product**
    *   Input: Query `Q`, Key `K`, Value `V`.
    *   Expected: Output matrix matching `softmax(QK^T / sqrt(d_k))V`.
*   **Test 2: Heatmap Visuals**
    *   Action: Generate attention weights.
    *   Verification: Weights sum to 1 over the last dimension.
*   **Test 3: Signal Masking**
    *   Input: A sequence with padding.
    *   Expected: Attention score for padded positions should be `0` (or `-inf` before softmax).

### Agent 4: The Transformer Block (Phase 4)
**Goal:** Stack attention and feed-forward layers.

#### TDD Specs (`tests/test_transformer.py`)
*   **Test 1: Feed-Forward Network**
    *   Input: Vector `x`.
    *   Expected: `ReLU(xW1 + b1)W2 + b2`.
*   **Test 2: Residual Connections**
    *   Input: `x`, Sublayer `F(x)`.
    *   Expected: Output is `x + F(x)`.

---

## 🎯 Block 3: The Outreach Strategy (Weeks 6-8)

### Agent 5: The Sampler (Phase 5-6)
**Goal:** Adjust "creativity" using Temperature.

#### TDD Specs (`tests/test_sampler.py`)
*   **Test 1: Temperature Scaling**
    *   Input: Logits `[1.0, 2.0, 3.0]`, Temp=2.0.
    *   Expected: Distribution becomes flatter (more uniform).
    *   Input: Temp=0.1.
    *   Expected: Distribution becomes sharper (argmax).
*   **Test 2: Top-K Filtering**
    *   Input: Logits `[0.1, 0.4, 0.5]`, K=1.
    *   Expected: Only 0.5 remains available for sampling.

### Agent 6: The Router (Mixture of Experts) (Phase 7-9)
**Goal:** Route different personas (Founder vs. VP) to different logic paths.

#### TDD Specs (`tests/test_router.py`)
*   **Test 1: Gating Network**
    *   Input: "SaaS Founder" embedding.
    *   Expected: High probability for `Expert_A` (Founder Logic).
    *   Input: "Enterprise VP" embedding.
    *   Expected: High probability for `Expert_B` (Corporate Logic).
*   **Test 2: Load Balancing (Optional)**
    *   Check that experts are utilized roughly evenly if inputs are balanced.

---

## 🛡 Block 4: Brand Alignment (Weeks 9-11)

### Agent 7: Stability (LayerNorm) (Phase 10)
**Goal:** Prevent exploding gradients.

#### TDD Specs (`tests/test_layernorm.py`)
*   **Test 1: Normalization**
    *   Input: A batch of vectors.
    *   Expected: Each vector has Mean ≈ 0, Std ≈ 1.
*   **Test 2: Scale and Shift**
    *   Input: Normalized vector.
    *   Expected: Multiplied by `gamma` and added `beta`.

### Agent 8: Instruction Tuner (Phase 11-12)
**Goal:** Align model output with brand voice ("Helpful peer").

#### TDD Specs (`tests/test_tuning.py`)
*   **Test 1: Dataset Formatting**
    *   Input: `(Instruction, Response)` pair.
    *   Expected: Formatted prompt string (e.g., `[INST] ... [/INST]`).
*   **Test 2: Loss Calculation**
    *   Action: Compute loss on instruction tokens vs. response tokens.
    *   Expected: Loss masked for instruction (only train on response).

---

## 🚀 Block 5: The Stress Test (Weeks 12-14)

### Agent 9: Optimizer (Quantization) (Phase 13-14)
**Goal:** Reduce model size.

#### TDD Specs (`tests/test_quantization.py`)
*   **Test 1: FP32 to Int8**
    *   Input: Float weight matrix.
    *   Expected: Int8 matrix + scaling factor.
*   **Test 2: Degradation Check**
    *   Action: Compare output of FP32 vs Int8 model on test set.
    *   Expected: Accuracy drop < 1%.
