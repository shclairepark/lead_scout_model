import unittest
import torch
import math
import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.positional_encoding import PositionalEncoding

class TestPositionalEncoding(unittest.TestCase):
    
    def setUp(self):
        self.d_model = 128
        self.max_len = 32
        self.pe_layer = PositionalEncoding(d_model=self.d_model, max_len=self.max_len)
    
    def test_output_shape(self):
        """Test that output shape matches input shape"""
        batch_size = 2
        seq_len = 6
        x = torch.zeros(batch_size, seq_len, self.d_model)
        output = self.pe_layer(x)
        self.assertEqual(output.shape, x.shape)
    
    def test_positions_deterministic(self):
        """Test that encoding is deterministic (same position gives same encoding)"""
        batch_size = 1
        seq_len = 10
        x = torch.zeros(batch_size, seq_len, self.d_model)
        output1 = self.pe_layer(x)
        output2 = self.pe_layer(x)
        self.assertTrue(torch.allclose(output1, output2))
    
    def test_decay_property(self):
        """Test that relative positions have consistent relationship (sanity check for frequencies)"""
        # We can verify that PE varies across positions
        # Take just the first position's encoding vs second position
        x = torch.zeros(1, 2, self.d_model)
        output = self.pe_layer(x)
        pos0 = output[0, 0, :]
        pos1 = output[0, 1, :]
        
        # They should not be equal
        self.assertFalse(torch.allclose(pos0, pos1))
        
        # Norm should be 1.0 ideally if it was pure sin/cos embeddings, 
        # but our implementation adds it to X (which is 0 here).
        # Our implementation uses PE + X.
        # Since X is 0, Output IS PE.
        # PE values are sin/cos, so they are bounded [-1, 1].
        self.assertTrue((pos0 >= -1).all() and (pos0 <= 1).all())

    def test_values_match_formula(self):
        """Verify a specific value against the formula manually"""
        # Formula: 
        # PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
        # Check pos=1, i=0 (index 0)
        # PE(1, 0) = sin(1 / 10000^(0)) = sin(1)
        
        x = torch.zeros(1, 5, self.d_model)
        output = self.pe_layer(x)
        
        expected = math.sin(1.0)
        actual = output[0, 1, 0].item()
        
        self.assertAlmostEqual(actual, expected, places=4)

if __name__ == '__main__':
    unittest.main()
