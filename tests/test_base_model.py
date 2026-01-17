import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add the notebooks directory to the path so we can import base_model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../notebooks')))

from base_model import preprocess_data, feature_engineering, train_model

class TestBaseModel(unittest.TestCase):

    def setUp(self):
        # Create a tiny dummy dataset
        self.raw_data = pd.DataFrame({
            'months_in_role': [10, 20],
            'funding_amount': [0, 100],
            'comp_views_3m': [6, 1],
            'comp_views_1m': [2, 0],
            'own_views_3m': [3, 0],
            'own_views_1m': [1, 0],
            'replied': [1, 0]
        })

    def test_preprocess_data(self):
        """Test log transformation of funding."""
        df = preprocess_data(self.raw_data)
        self.assertTrue('funding_amount' in df.columns)
        # log1p(0) should be 0
        self.assertAlmostEqual(df.loc[0, 'funding_amount'], 0.0)
        # log1p(100) should be approx 4.615
        self.assertAlmostEqual(df.loc[1, 'funding_amount'], np.log1p(100))

    def test_feature_engineering_momentum(self):
        """Test momentum calculation."""
        # Row 0: own_views_1m=1, own_views_3m=3
        # Denom = 3 / 3 + 1 = 2
        # Ratio = 1 / 2 = 0.5
        df = feature_engineering(self.raw_data)
        self.assertAlmostEqual(df.loc[0, 'own_surge_ratio'], 0.5)

    def test_feature_engineering_comp_intensity(self):
        """Test competitive intensity calculation."""
        # Row 0: comp_views_1m=2, comp_views_3m=6 -> 8
        df = feature_engineering(self.raw_data)
        self.assertEqual(df.loc[0, 'comp_intensity'], 8)

    def test_model_training(self):
        """Test that the model trains and returns a scaler."""
        df = preprocess_data(self.raw_data)
        df = feature_engineering(df)
        
        features = ['months_in_role', 'funding_amount', 'own_surge_ratio', 'comp_intensity']
        X = df[features]
        y = df['replied']
        
        model, scaler = train_model(X, y)
        
        self.assertIsNotNone(model)
        self.assertIsNotNone(scaler)
        # Check if we can make a prediction
        test_pred = model.predict_proba(scaler.transform(X))
        self.assertEqual(test_pred.shape, (2, 2))
        self.assertTrue((test_pred >= 0).all() and (test_pred <= 1).all())
        total_prob = test_pred.sum(axis=1)
        np.testing.assert_allclose(total_prob, 1.0)

if __name__ == '__main__':
    unittest.main()
