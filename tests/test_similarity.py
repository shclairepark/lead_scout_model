import unittest
import numpy as np
import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tokenizer import dot_product, cosine_similarity, euclidean_distance


class TestSimilarityFunctions(unittest.TestCase):
    
    def test_dot_product_basic(self):
        """Test basic dot product calculation"""
        vec1 = [1, 2, 3]
        vec2 = [4, 5, 6]
        result = dot_product(vec1, vec2)
        expected = 1*4 + 2*5 + 3*6  # = 32
        self.assertAlmostEqual(result, expected)
    
    def test_dot_product_positive_similar_vectors(self):
        """Test that similar vectors have positive dot product"""
        vec1 = np.array([0.82, 0.35, -0.21, 0.91])
        vec2 = np.array([0.78, 0.40, 0.10, 0.87])
        result = dot_product(vec1, vec2)
        self.assertGreater(result, 0)
    
    def test_dot_product_negative_dissimilar_vectors(self):
        """Test that dissimilar vectors have negative dot product"""
        vec1 = np.array([0.82, 0.35, -0.21, 0.91])
        vec3 = np.array([-0.53, -0.62, 0.89, -0.41])
        result = dot_product(vec1, vec3)
        self.assertLess(result, 0)
    
    def test_cosine_similarity_identical_vectors(self):
        """Test that identical vectors have cosine similarity of 1"""
        vec = np.array([1, 2, 3])
        result = cosine_similarity(vec, vec)
        self.assertAlmostEqual(result, 1.0, places=4)
    
    def test_cosine_similarity_orthogonal_vectors(self):
        """Test that orthogonal vectors have cosine similarity of 0"""
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([0, 1, 0])
        result = cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(result, 0.0, places=4)
    
    def test_cosine_similarity_zero_vector(self):
        """Test that zero vector handling doesn't crash"""
        zero_vec = np.array([0, 0, 0])
        normal_vec = np.array([1, 2, 3])
        
        # Should not crash and should return something reasonable
        result1 = cosine_similarity(zero_vec, normal_vec)
        result2 = cosine_similarity(zero_vec, zero_vec)
        
        self.assertIsInstance(result1, (float, np.floating))
        self.assertIsInstance(result2, (float, np.floating))
        # Depending on implementation, might return 0.0
        self.assertAlmostEqual(result1, 0.0, places=4)
        self.assertAlmostEqual(result2, 0.0, places=4)
    
    def test_cosine_similarity_bounds(self):
        """Test that cosine similarity is always in [-1, 1]"""
        vecX = np.random.randn(10, 5) # Smaller batch for speed
        vecY = np.random.randn(10, 5)
        
        # Test just a few pairs manually since our func handles 1D standard vectors primarily
        # But if it handles 2D, great. Assuming input is simple 1D as per docstring.
        sim = cosine_similarity(vecX[0], vecY[0])
        self.assertGreaterEqual(sim, -1.0 - 1e-5)
        self.assertLessEqual(sim, 1.0 + 1e-5)
    
    def test_euclidean_distance_identical_vectors(self):
        """Test that identical vectors have distance of 0"""
        vec = np.array([1, 2, 3])
        result = euclidean_distance(vec, vec)
        self.assertAlmostEqual(result, 0.0, places=4)
    
    def test_euclidean_distance_triangle(self):
        """Test Euclidean distance with known Pythagorean triple"""
        vec1 = np.array([0, 0, 0])
        vec2 = np.array([3, 4, 0])
        result = euclidean_distance(vec1, vec2)
        self.assertAlmostEqual(result, 5.0, places=4)
    
    def test_euclidean_distance_non_negative(self):
        """Test that Euclidean distance is always non-negative"""
        vec1 = np.array([0.82, 0.35, -0.21, 0.91])
        vec2 = np.array([-0.53, -0.62, 0.89, -0.41])
        
        result = euclidean_distance(vec1, vec2)
        self.assertGreaterEqual(result, 0.0)
    
    def test_euclidean_distance_small_for_similar(self):
        """Test that similar vectors have small Euclidean distance"""
        vec1 = np.array([0.82, 0.35, -0.21, 0.91])
        vec2 = np.array([0.78, 0.40, 0.10, 0.87])
        vec3 = np.array([-0.53, -0.62, 0.89, -0.41])
        
        dist_similar = euclidean_distance(vec1, vec2)
        dist_dissimilar = euclidean_distance(vec1, vec3)
        
        self.assertLess(dist_similar, dist_dissimilar)


if __name__ == '__main__':
    unittest.main()