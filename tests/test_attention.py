import unittest
import torch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.attention import SelfAttention, MultiHeadAttention


class TestSelfAttention(unittest.TestCase):
    
    def setUp(self):
        self.embed_dim = 128
        self.batch_size = 2
        self.seq_len = 6
        self.attention = SelfAttention(self.embed_dim)
    
    def test_output_shape(self):
        """Test that output shape matches input shape"""
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        
        output, attention_weights = self.attention(x)
        
        # Output should have same shape as input
        self.assertEqual(output.shape, (self.batch_size, self.seq_len, self.embed_dim))
        
        # Attention weights should be [batch, seq, seq]
        self.assertEqual(attention_weights.shape, (self.batch_size, self.seq_len, self.seq_len))
    
    def test_attention_weights_sum_to_one(self):
        """Test that attention weights sum to 1 for each token"""
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        
        _, attention_weights = self.attention(x)
        
        # For each token, attention weights should sum to 1
        sums = attention_weights.sum(dim=-1)  # Sum over last dimension
        expected = torch.ones(self.batch_size, self.seq_len)
        
        self.assertTrue(torch.allclose(sums, expected, atol=1e-6))
    
    def test_attention_weights_in_range(self):
        """Test that attention weights are between 0 and 1"""
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        
        _, attention_weights = self.attention(x)
        
        self.assertTrue(torch.all(attention_weights >= 0))
        self.assertTrue(torch.all(attention_weights <= 1))
    
    def test_with_mask(self):
        """Test attention with masking (e.g., for padding)"""
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        
        # Create mask: first 4 tokens are real, last 2 are padding
        mask = torch.ones(self.batch_size, self.seq_len, self.seq_len)
        mask[:, :, 4:] = 0  # Mask out positions 4 and 5
        
        output, attention_weights = self.attention(x, mask=mask)
        
        # Attention weights to masked positions should be ~0
        masked_weights = attention_weights[:, :, 4:]
        self.assertTrue(torch.all(masked_weights < 1e-6))
    
    def test_self_attention_property(self):
        """Test that tokens attend to themselves (self-attention)"""
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        
        _, attention_weights = self.attention(x)
        
        # Diagonal should have non-zero values (tokens attend to themselves)
        for b in range(self.batch_size):
            diagonal = torch.diagonal(attention_weights[b])
            self.assertTrue(torch.all(diagonal > 0))


class TestMultiHeadAttention(unittest.TestCase):
    
    def setUp(self):
        self.embed_dim = 128
        self.num_heads = 4
        self.batch_size = 2
        self.seq_len = 6
        self.attention = MultiHeadAttention(self.embed_dim, self.num_heads)
    
    def test_output_shape(self):
        """Test that output shape matches input shape"""
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        
        output, attention_weights = self.attention(x)
        
        self.assertEqual(output.shape, (self.batch_size, self.seq_len, self.embed_dim))
        self.assertEqual(attention_weights.shape, (self.batch_size, self.seq_len, self.seq_len))
    
    def test_embed_dim_divisibility(self):
        """Test that embed_dim must be divisible by num_heads"""
        with self.assertRaises(AssertionError):
            MultiHeadAttention(embed_dim=127, num_heads=4)  # 127 not divisible by 4
    
    def test_attention_weights_properties(self):
        """Test attention weights sum to 1 and are in [0, 1]"""
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        
        _, attention_weights = self.attention(x)
        
        # Sum to 1
        sums = attention_weights.sum(dim=-1)
        expected = torch.ones(self.batch_size, self.seq_len)
        self.assertTrue(torch.allclose(sums, expected, atol=1e-6))
        
        # In range [0, 1]
        self.assertTrue(torch.all(attention_weights >= 0))
        self.assertTrue(torch.all(attention_weights <= 1))
    
    def test_different_from_single_head(self):
        """Test that multi-head is different from single-head"""
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        
        # Multi-head attention
        mh_attention = MultiHeadAttention(self.embed_dim, num_heads=4)
        mh_output, _ = mh_attention(x)
        
        # Single-head attention (equivalent to num_heads=1)
        sh_attention = MultiHeadAttention(self.embed_dim, num_heads=1)
        sh_output, _ = sh_attention(x)
        
        # Outputs should be different (different architectures)
        self.assertFalse(torch.allclose(mh_output, sh_output))


if __name__ == '__main__':
    unittest.main()