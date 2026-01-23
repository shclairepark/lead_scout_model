import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    """
    Self-Attention mechanism for Lead Scout Model.
    
    Allows each token to "attend to" (look at) other tokens in the sequence
    to gather contextual information.
    
    Example:
        When processing "TENURE_SHORT", the model can learn to also look at
        "FUNDING_SERIES_A" because they're often correlated in high-reply leads.
    """
    
    def __init__(self, embed_dim):
        """
        Args:
            embed_dim: Dimension of token embeddings (e.g., 128)
        """
        super().__init__()
        
        self.embed_dim = embed_dim
        
        # Linear layers to create Query, Key, Value
        # These are learned during training
        self.W_q = nn.Linear(embed_dim, embed_dim)  # Query projection
        self.W_k = nn.Linear(embed_dim, embed_dim)  # Key projection
        self.W_v = nn.Linear(embed_dim, embed_dim)  # Value projection
        
        # Scaling factor for dot products
        self.scale = math.sqrt(embed_dim)
    
    def forward(self, x, mask=None):
        """
        Apply self-attention to input embeddings.
        
        Args:
            x: Input embeddings, shape [batch_size, seq_len, embed_dim]
               Example: [8, 6, 128] - 8 leads, 6 tokens each, 128 dims
            mask: Optional attention mask, shape [batch_size, seq_len, seq_len]
                  Used to prevent attending to padding tokens
        
        Returns:
            output: Attention output, shape [batch_size, seq_len, embed_dim]
                   Same shape as input!
            attention_weights: Attention scores, shape [batch_size, seq_len, seq_len]
                              Useful for visualization
        """
        batch_size, seq_len, embed_dim = x.shape
        
        # Step 1: Create Queries, Keys, Values
        # Q: "What am I looking for?"
        # K: "What do I offer?"
        # V: "What information do I contain?"
        Q = self.W_q(x)  # [batch_size, seq_len, embed_dim]
        K = self.W_k(x)  # [batch_size, seq_len, embed_dim]
        V = self.W_v(x)  # [batch_size, seq_len, embed_dim]
        
        # Step 2: Calculate attention scores
        # Q × K^T: "How much does each query match each key?"
        attention_scores = torch.matmul(Q, K.transpose(-2, -1))
        # Shape: [batch_size, seq_len, seq_len]
        # attention_scores[i, j] = how much token i attends to token j
        
        # Step 3: Scale scores
        # Prevents gradients from becoming too large
        attention_scores = attention_scores / self.scale
        
        # Step 4: Apply mask (if provided)
        # Used to ignore padding tokens
        if mask is not None:
            # Set masked positions to large negative value
            # so softmax makes them ~0
            attention_scores = attention_scores.masked_fill(mask == 0, float('-inf'))
        
        # Step 5: Apply softmax
        # Convert scores to probabilities (sum to 1 for each token)
        attention_weights = torch.softmax(attention_scores, dim=-1)
        # Shape: [batch_size, seq_len, seq_len]
        # attention_weights[i, j] = probability of token i attending to token j
        
        # Step 6: Apply attention to values
        # Weighted sum: gather information from all tokens
        output = torch.matmul(attention_weights, V)
        # Shape: [batch_size, seq_len, embed_dim]
        # output[i] = weighted combination of all tokens' values
        
        return output, attention_weights


class MultiHeadAttention(nn.Module):
    """
    Multi-Head Self-Attention.
    
    Instead of one attention mechanism, use multiple "heads" that learn
    different types of relationships.
    
    Example:
        - Head 1: Learns "tenure → funding" relationships
        - Head 2: Learns "momentum → competition" relationships
        - Head 3: Learns "recency → activity" relationships
        - Head 4: Learns other patterns
    """
    
    def __init__(self, embed_dim, num_heads):
        """
        Args:
            embed_dim: Dimension of embeddings (must be divisible by num_heads)
            num_heads: Number of attention heads (e.g., 4)
        """
        super().__init__()
        
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads  # Dimension per head
        
        # Linear layers for all heads (computed in parallel)
        self.W_q = nn.Linear(embed_dim, embed_dim)
        self.W_k = nn.Linear(embed_dim, embed_dim)
        self.W_v = nn.Linear(embed_dim, embed_dim)
        
        # Output projection (combines all heads)
        self.W_o = nn.Linear(embed_dim, embed_dim)
        
        self.scale = math.sqrt(self.head_dim)
    
    def forward(self, x, mask=None):
        """
        Apply multi-head self-attention.
        
        Args:
            x: Input embeddings, shape [batch_size, seq_len, embed_dim]
            mask: Optional mask, shape [batch_size, 1, seq_len] or [batch_size, seq_len, seq_len]
        
        Returns:
            output: Attention output, shape [batch_size, seq_len, embed_dim]
            attention_weights: Average attention across heads, [batch_size, seq_len, seq_len]
        """
        batch_size, seq_len, embed_dim = x.shape
        
        # Step 1: Create Q, K, V for all heads at once
        Q = self.W_q(x)  # [batch_size, seq_len, embed_dim]
        K = self.W_k(x)
        V = self.W_v(x)
        
        # Step 2: Reshape to split into multiple heads
        # [batch_size, seq_len, embed_dim] → [batch_size, seq_len, num_heads, head_dim]
        Q = Q.view(batch_size, seq_len, self.num_heads, self.head_dim)
        K = K.view(batch_size, seq_len, self.num_heads, self.head_dim)
        V = V.view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        # Step 3: Transpose to [batch_size, num_heads, seq_len, head_dim]
        # Now each head processes independently
        Q = Q.transpose(1, 2)
        K = K.transpose(1, 2)
        V = V.transpose(1, 2)
        
        # Step 4: Calculate attention scores for all heads
        attention_scores = torch.matmul(Q, K.transpose(-2, -1))
        # Shape: [batch_size, num_heads, seq_len, seq_len]
        
        # Step 5: Scale
        attention_scores = attention_scores / self.scale
        
        # Step 6: Apply mask (if provided)
        if mask is not None:
            # Expand mask for multiple heads
            if mask.dim() == 3:  # [batch_size, 1, seq_len]
                mask = mask.unsqueeze(1)  # [batch_size, 1, 1, seq_len]
            attention_scores = attention_scores.masked_fill(mask == 0, float('-inf'))
        
        # Step 7: Softmax
        attention_weights = torch.softmax(attention_scores, dim=-1)
        # Shape: [batch_size, num_heads, seq_len, seq_len]
        
        # Step 8: Apply attention to values
        output = torch.matmul(attention_weights, V)
        # Shape: [batch_size, num_heads, seq_len, head_dim]
        
        # Step 9: Concatenate heads
        # [batch_size, num_heads, seq_len, head_dim] → [batch_size, seq_len, num_heads, head_dim]
        output = output.transpose(1, 2).contiguous()
        
        # [batch_size, seq_len, num_heads, head_dim] → [batch_size, seq_len, embed_dim]
        output = output.view(batch_size, seq_len, embed_dim)
        
        # Step 10: Final linear projection
        output = self.W_o(output)
        
        # Average attention weights across heads (for visualization)
        attention_weights_avg = attention_weights.mean(dim=1)  # [batch_size, seq_len, seq_len]
        
        return output, attention_weights_avg