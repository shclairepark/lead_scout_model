
import json
import os

class SalesTokenizer:
    def __init__(self):
        """
        Tokenizer for lead data.
        Strategy:
        - Buckets only (no quantized values)
        - Engineered features for momentum
        - Raw features for funding and tenure
        """
        self.vocab = self._build_vocab() # Token -> ID
        self.id_to_token = {v: k for k, v in self.vocab.items()} 
    
    def _build_vocab(self):
        """Build the vocabulary mapping token -> ID"""
        vocab = {}
        idx = 0
        
        # Special tokens
        for token in ["[PAD]", "[START]", "[END]"]:
            vocab[token] = idx
            idx += 1
        
        # Tenure buckets
        for token in ["TENURE_NEW", "TENURE_SHORT", "TENURE_MID", "TENURE_LONG"]:
            vocab[token] = idx
            idx += 1
        
        # Funding buckets
        for token in ["FUNDING_BOOTSTRAP", "FUNDING_SEED", "FUNDING_SERIES_A", "FUNDING_GROWTH"]:
            vocab[token] = idx
            idx += 1
        
        # Momentum buckets
        for token in ["MOMENTUM_DECLINING", "MOMENTUM_STABLE", "MOMENTUM_ACCELERATING"]:
            vocab[token] = idx
            idx += 1
        
        # Competition buckets
        for token in ["COMP_LOW", "COMP_MED", "COMP_HIGH"]:
            vocab[token] = idx
            idx += 1
        
        # Signal Type buckets
        # mapped from SignalType enum values + "SIGNAL_" prefix
        signal_types = [
            "signal_funding_round",
            "signal_job_posting", 
            "signal_role_change",
            "signal_news_mention",
            "signal_content_engagement",
            "signal_profile_visit",
            "signal_event_attendance",
            "signal_demo_request",
            "signal_pricing_page_visit",
            "signal_competitor_interaction",
            "signal_social_connection"
        ]
        for token in signal_types:
            vocab[token.upper()] = idx
            idx += 1
            
        return vocab
    
    def tokenize_lead(self, lead_data, signals=None):
        """
        Convert lead dict + signals to list of token strings.
        
        Args:
            lead_data: dict with lead attributes
            signals: optional list of SignalEvent objects or dicts
        
        Returns:
            tokens: list of token strings
            token_ids: list of token IDs
        """
        tokens = ["[START]"]
        
        # ===================================
        # Tokenize months_in_role
        # ===================================
        months = lead_data.get("months_in_role", 0)
        
        if months < 3:
            tokens.append("TENURE_NEW")
        elif 3 <= months < 6:
            tokens.append("TENURE_SHORT")
        elif 6 <= months < 18:
            tokens.append("TENURE_MID")
        else:
            tokens.append("TENURE_LONG")
        
        # ===================================
        # Tokenize funding_amount
        # ===================================
        funding = lead_data.get("funding_amount", 0)

        if funding < 100000:
            tokens.append("FUNDING_BOOTSTRAP")
        elif 100000 <= funding < 1000000:
            tokens.append("FUNDING_SEED")
        elif 1000000 <= funding < 10000000:
            tokens.append("FUNDING_SERIES_A")
        else:
            tokens.append("FUNDING_GROWTH")
        
        # ===================================
        # Calculate and tokenize momentum
        # ===================================
        own_views_3m = lead_data.get("own_views_3m", 0)
        own_views_1m = lead_data.get("own_views_1m", 0)
        
        epsilon = 1e-8
        # Formula: ratio = current / (average + epsilon)
        avg_views_per_month = own_views_3m / 3.0
        own_surge_ratio = own_views_1m / (avg_views_per_month + epsilon)
        if own_surge_ratio < 0.8:
            tokens.append("MOMENTUM_DECLINING")
        elif 0.8 <= own_surge_ratio < 1.2:
            tokens.append("MOMENTUM_STABLE")
        else:
            tokens.append("MOMENTUM_ACCELERATING")        
        
        # ===================================
        # Calculate and tokenize competition
        # ===================================
        comp_views_3m = lead_data.get("comp_views_3m", 0)
        comp_views_1m = lead_data.get("comp_views_1m", 0)
        
        comp_intensity = comp_views_1m + comp_views_3m
        if comp_intensity < 3:
            tokens.append("COMP_LOW")
        elif comp_intensity < 10:
            tokens.append("COMP_MED")
        else:
            tokens.append("COMP_HIGH")
            
        # ===================================
        # Tokenize Signals
        # ===================================
        if signals:
            for sig in signals:
                # Handle both SignalEvent objects and dicts (from synthetic data)
                if hasattr(sig, 'type'):
                    # It's a SignalEvent enum
                    t_val = sig.type.value
                elif isinstance(sig, dict):
                    t_val = sig.get('type', '')
                else:
                    continue
                    
                # Construct token: SIGNAL_TYPE
                # e.g. funding_round -> SIGNAL_FUNDING_ROUND
                token_name = f"SIGNAL_{t_val}".upper()
                
                # Add if in vocab, otherwise ignore
                if token_name in self.vocab:
                    tokens.append(token_name)
        
        tokens.append("[END]")
        
        # Convert tokens to IDs
        token_ids = self._tokens_to_ids(tokens)
        
        return tokens, token_ids
    
    def _tokens_to_ids(self, tokens):
        """Convert token strings to IDs using self.vocab"""
        return [self.vocab[token] for token in tokens]
    
    def ids_to_tokens(self, token_ids):
        """Convert token IDs back to strings"""
        return [self.id_to_token[idx] for idx in token_ids]
    
    def save_vocab(self, filepath):
        """Save vocabulary to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.vocab, f, indent=2)
        print(f"Vocabulary saved to {filepath}")
    
    def load_vocab(self, filepath):
        """Load vocabulary from JSON file"""
        with open(filepath, 'r') as f:
            self.vocab = json.load(f)
        self.id_to_token = {v: k for k, v in self.vocab.items()}
        print(f"Vocabulary loaded from {filepath}")