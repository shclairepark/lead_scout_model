import unittest
import torch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.transformer_block import TransformerBlock
from src.model.lead_scout import LeadScoutModel

class TestTransformerBlock(unittest.TestCase):
    def setUp(self):
        self.embed_dim = 128
        self.num_heads = 4
        self.block = TransformerBlock(self.embed_dim, self.num_heads)
        self.batch_size = 2
        self.seq_len = 10

    def test_output_shape(self):
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        output = self.block(x)
        self.assertEqual(output.shape, x.shape)
        
    def test_mask(self):
        x = torch.randn(self.batch_size, self.seq_len, self.embed_dim)
        # 3D mask [batch, 1, seq_len]
        mask = torch.ones(self.batch_size, 1, self.seq_len)
        output = self.block(x, mask=mask)
        self.assertEqual(output.shape, x.shape)


class TestLeadScoutModel(unittest.TestCase):
    def setUp(self):
        self.vocab_size = 17
        self.embed_dim = 128
        self.model = LeadScoutModel(
            vocab_size=self.vocab_size,
            embed_dim=self.embed_dim,
            num_layers=2
        )
        self.batch_size = 2
        self.seq_len = 10

    def test_forward_output_shape(self):
        token_ids = torch.randint(0, self.vocab_size, (self.batch_size, self.seq_len))
        output = self.model(token_ids)
        # Output should be [batch_size, 1] probability
        self.assertEqual(output.shape, (self.batch_size, 1))
        # Probabilities should be in [0, 1]
        self.assertTrue(torch.all(output >= 0))
        self.assertTrue(torch.all(output <= 1))

    def test_masking_integration(self):
        token_ids = torch.randint(0, self.vocab_size, (self.batch_size, self.seq_len))
        # Mask where tokens are padding (e.g. 0)
        # Simply testing it accepts mask argument and runs
        # Correct mask shape for MultiHeadAttention is [batch, 1, 1, seq_len] or [batch, 1, seq_len]
        mask = (token_ids != 0).unsqueeze(1) # [batch, 1, seq]
        output = self.model(token_ids, mask=mask)
        self.assertEqual(output.shape, (self.batch_size, 1))

if __name__ == '__main__':
    unittest.main()
