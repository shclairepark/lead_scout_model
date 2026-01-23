import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    """
    Add positional information to token embeddings.
    
    For Lead Scout Model:
    - d_model=128: Each token represented by 128-dimensional vector
    - max_len=32: Can handle sequences up to 32 tokens
                  (Current: 6 tokens, Future with activities: ~20-25 tokens)
    """
    
    def __init__(self, d_model=128, max_len=32):
        super().__init__()
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        
        # Position indices: [0, 1, 2, ..., 31]
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        # Dimension scaling factors
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                            (-math.log(10000.0) / d_model))
        
        # Apply sin to even indices
        pe[:, 0::2] = torch.sin(position * div_term)
        
        # Apply cos to odd indices
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # Add batch dimension: (32, 128) → (1, 32, 128)
        pe = pe.unsqueeze(0)
        
        # Register as buffer (not trainable)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        """
        Add positional encoding to input embeddings.
        
        Args:
            x: Token embeddings, shape [batch_size, seq_len, d_model]
               Example: [2, 6, 128] for 2 leads with 6 tokens each
        
        Returns:
            x + positional encodings, same shape as input
        """
        # x.shape: [batch_size, seq_len, d_model]
        # self.pe[:, :x.size(1)]: Take first seq_len positions from 32
        
        return x + self.pe[:, :x.size(1), :]
