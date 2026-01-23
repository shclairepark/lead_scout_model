# Phase 3 Retrospective: Attention Mechanism

## 🚨 Diagnosis: Why Heatmaps Look "Meaningless"
You correctly identified that the current attention patterns (e.g., high attention between `[END]` tokens) are artifacts of an **untrained model**.

1.  **Random Initialization**: The `W_q`, `W_k`, `W_v` projection matrices contains random weights. They have not learned to map "Tenure" and "Funding" into correlated subspaces yet.
2.  **Self-Similarity**: In a random vector space, a token is most similar to itself. Softmax amplifies this, creating a strong diagonal line or strong connections between identical tokens like `[END]` $\leftrightarrow$ `[END]`.
3.  **No Optimization**: Without a Loss Function (e.g., "Predict Reply") and Backpropagation, the model has no incentive to look at "Funding" when it sees "Tenure".

---

## ✅ Immediate To-Do List

### 1. Training Infrastructure (Critical)
The model needs to learn from the data in `leads_raw.csv`.
- [ ] **Define Objective**: deciding between *Next Token Prediction* (Generative) or *Classification* ("Will Reply?").
- [ ] **Create Training Loop**: Implement `forward` $\rightarrow$ `loss` $\rightarrow$ `backward` $\rightarrow$ `optimizer.step()`.
- [ ] **Save/Load Weights**: Ability to save `model.state_dict()` after training.

### 2. Model Refinement
- [ ] **Padding Masks**: Ensure the model ignores `[PAD]` tokens so they don't dilute the attention scores.
- [ ] **Model Depth**: Stack multiple layers (Transformer Block) to learn complex non-linear patterns (simple dot-product might be too linear for raw features).

### 3. Visualization Updates
- [ ] **Filter Special Tokens**: Update `phase3_attention.ipynb` to exclude `[START]` and `[END]` from heatmaps to zoom in on feature interactions.
- [ ] **Compare Epochs**: Visualize attention at Epoch 0 vs Epoch 10 to show the "emergence" of logic.
