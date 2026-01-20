import unittest
import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tokenizer import SalesTokenizer


class TestSalesTokenizer(unittest.TestCase):
    
    def setUp(self):
        """Run before each test - create a fresh tokenizer"""
        self.tokenizer = SalesTokenizer()
    
    def test_vocab_size(self):
        """Test that vocabulary has correct size"""
        self.assertEqual(len(self.tokenizer.vocab), 17)
    
    def test_vocab_contains_special_tokens(self):
        """Test that special tokens are in vocab"""
        self.assertIn("[PAD]", self.tokenizer.vocab)
        self.assertIn("[START]", self.tokenizer.vocab)
        self.assertIn("[END]", self.tokenizer.vocab)
    
    def test_tenure_buckets(self):
        """Test tenure tokenization with different values"""
        # Test TENURE_NEW (< 3 months)
        lead = {"months_in_role": 2, "funding_amount": 0, "own_views_3m": 1, "own_views_1m": 0, "comp_views_3m": 0, "comp_views_1m": 0}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("TENURE_NEW", tokens)
        
        # Test TENURE_SHORT (3-6 months)
        lead["months_in_role"] = 5
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("TENURE_SHORT", tokens)
        
        # Test TENURE_MID (7-17 months)
        lead["months_in_role"] = 10
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("TENURE_MID", tokens)
        
        # Test TENURE_LONG (18+ months)
        lead["months_in_role"] = 39
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("TENURE_LONG", tokens)
    
    def test_funding_buckets(self):
        """Test funding tokenization"""
        base_lead = {"months_in_role": 5, "own_views_3m": 1, "own_views_1m": 0, "comp_views_3m": 0, "comp_views_1m": 0}
        
        # Bootstrap
        lead = {**base_lead, "funding_amount": 50000}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("FUNDING_BOOTSTRAP", tokens)
        
        # Seed
        lead = {**base_lead, "funding_amount": 500000}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("FUNDING_SEED", tokens)
        
        # Series A
        lead = {**base_lead, "funding_amount": 5000000}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("FUNDING_SERIES_A", tokens)
        
        # Growth
        lead = {**base_lead, "funding_amount": 50000000}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("FUNDING_GROWTH", tokens)
    
    def test_momentum_calculation(self):
        """Test momentum tokenization"""
        base_lead = {"months_in_role": 5, "funding_amount": 1000000, "comp_views_3m": 0, "comp_views_1m": 0}
        
        # Zero views
        # Declining (surge < 0.8) -> 0 / (0 + eps) = 0
        lead = {**base_lead, "own_views_3m": 0, "own_views_1m": 0}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("MOMENTUM_DECLINING", tokens)

        # Declining (surge < 0.8)
        lead = {**base_lead, "own_views_3m": 6, "own_views_1m": 1}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("MOMENTUM_DECLINING", tokens)
        
        # Stable (0.8 <= surge < 1.2)
        # Denom = 3/3 = 1. To get 1.0, own_views_1m must be 1.
        lead = {**base_lead, "own_views_3m": 3, "own_views_1m": 1}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("MOMENTUM_STABLE", tokens)
        
        # Accelerating (surge >= 1.2)
        lead = {**base_lead, "own_views_3m": 1, "own_views_1m": 3}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("MOMENTUM_ACCELERATING", tokens)
    
    def test_competition_intensity(self):
        """Test competition tokenization"""
        base_lead = {"months_in_role": 5, "funding_amount": 1000000, "own_views_3m": 1, "own_views_1m": 1}
        
        # Low
        lead = {**base_lead, "comp_views_3m": 1, "comp_views_1m": 1}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("COMP_LOW", tokens)
        
        # Med
        lead = {**base_lead, "comp_views_3m": 3, "comp_views_1m": 2}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("COMP_MED", tokens)
        
        # High
        lead = {**base_lead, "comp_views_3m": 8, "comp_views_1m": 5}
        tokens, _ = self.tokenizer.tokenize_lead(lead)
        self.assertIn("COMP_HIGH", tokens)
    
    def test_full_tokenization_no_padding(self):
        """Test complete tokenization for sample lead 1"""
        lead = {
            "months_in_role": 39,
            "funding_amount": 0.0,
            "comp_views_3m": 0,
            "comp_views_1m": 0,
            "own_views_3m": 1,
            "own_views_1m": 0
        }
        
        tokens, token_ids = self.tokenizer.tokenize_lead(lead)
        # Current implementation should NOT have [PAD]
        self.assertNotIn('[PAD]', tokens)
        self.assertEqual(tokens[0], "[START]")
        self.assertEqual(tokens[-1], "[END]")
        
        expected_tokens = ['[START]', 'TENURE_LONG', 'FUNDING_BOOTSTRAP', 'MOMENTUM_DECLINING', 'COMP_LOW', '[END]']
        self.assertEqual(tokens, expected_tokens)
        self.assertEqual(len(token_ids), 6)
    
    def test_round_trip_conversion(self):
        """Test that token -> ID -> token conversion works"""
        lead = {
            "months_in_role": 5,
            "funding_amount": 1000000,
            "comp_views_3m": 2,
            "comp_views_1m": 0,
            "own_views_3m": 1,
            "own_views_1m": 0
        }
        
        tokens, token_ids = self.tokenizer.tokenize_lead(lead)
        reconstructed = self.tokenizer.ids_to_tokens(token_ids)
        
        self.assertEqual(tokens, reconstructed)

if __name__ == '__main__':
    unittest.main()