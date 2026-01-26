import torch
import torch.nn as nn
from .positional_encoding import PositionalEncoding
from .transformer_block import TransformerBlock

class LeadScoutModel(nn.Module):
    """
    Lead Scout Model: Predicts likelihood of a lead replying.
    
    Architecture:
    1. Embeddings: Convert tokens to vectors
    2. Positional Encoding: Add sequence order information
    3. Transformer Encoder: Stack of TransformerBlocks (Self-Attention + FFN)
    4. Pooling: Use [START] token representation
    5. Classifier: Predict probability (0-1)
    """
    
    def __init__(self, vocab_size=17, embed_dim=128, num_heads=4, num_layers=3, ff_dim=256, dropout=0.1):
        super().__init__()
        
        # Phase 1: Embeddings
        # padding_idx=0 ensures [PAD] token (index 0) always has zero vector
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        # Phase 2: Positional encoding
        self.pos_encoding = PositionalEncoding(embed_dim, max_len=32)
        
        # Phase 3-4: Stack Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, ff_dim, dropout)
            for _ in range(num_layers)
        ])
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )
        
        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize weights for better convergence"""
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, token_ids, mask=None):
        """
        Forward pass.
        
        Args:
            token_ids: [batch_size, seq_len]
            mask: Optional [batch_size, seq_len, seq_len] or [batch_size, 1, seq_len]
            
        Returns:
            probability: [batch_size, 1] - Probability of reply
        """
        # Phase 1: Token embeddings
        x = self.embedding(token_ids)  # [batch, seq_len, embed_dim]
        
        # Phase 2: Add positional encoding
        x = self.pos_encoding(x)
        
        # Phase 3-4: Pass through all Transformer blocks
        for block in self.transformer_blocks:
            x = block(x, mask=mask)
        
        # Pool: Use [START] token (position 0) for classification
        # This token aggregates information from the whole sequence via attention
        cls_token = x[:, 0, :]  # [batch, embed_dim]
        
        # Classify
        logits = self.classifier(cls_token)  # [batch, 1]
        
        return torch.sigmoid(logits)  # [batch, 1] - reply probability
