
import torch.nn as nn
from .attention import MultiHeadAttention


class TransformerBlock(nn.Module):
    """
    Single Transformer block: Multi-Head Attention + Feed-Forward Network.
    
    Architecture:
        x → LayerNorm → MultiHeadAttention → + (residual) → LayerNorm → FFN → + (residual) → output
    
    For Lead Scout Model:
        - embed_dim=128: Embedding dimension
        - num_heads=4: 4 attention heads (each with 32 dimensions)
        - ff_dim=256: Feed-forward hidden dimension (2× embed_dim is common)
    """
    
    def __init__(self, embed_dim=128, num_heads=4, ff_dim=256, dropout=0.1):
        """
        Args:
            embed_dim: Dimension of embeddings (must be divisible by num_heads)
            num_heads: Number of attention heads
            ff_dim: Hidden dimension of feed-forward network
            dropout: Dropout probability for regularization
        """
        super().__init__()
        
        # Multi-Head Self-Attention
        self.attention = MultiHeadAttention(embed_dim, num_heads)
        
        # Feed-Forward Network (2-layer MLP)
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            nn.GELU(),  # GELU activation (used in BERT, GPT)
            nn.Dropout(dropout),
            nn.Linear(ff_dim, embed_dim),
            nn.Dropout(dropout)
        )
        
        # Layer Normalization (Pre-LN architecture for stability)
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        
        # Dropout for attention output
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        """
        Apply transformer block to input embeddings.
        
        Args:
            x: Input embeddings, shape [batch_size, seq_len, embed_dim]
            mask: Optional attention mask
        
        Returns:
            output: Transformed embeddings, same shape as input
        """
        # Pre-LN: Normalize before attention
        normed = self.norm1(x)
        
        # Multi-Head Attention
        attn_output, _ = self.attention(normed, mask=mask)
        
        # Residual connection
        x = x + self.dropout(attn_output)
        
        # Pre-LN: Normalize before FFN
        normed = self.norm2(x)
        
        # Feed-Forward Network
        ffn_output = self.ffn(normed)
        
        # Residual connection
        x = x + ffn_output
        
        return x
