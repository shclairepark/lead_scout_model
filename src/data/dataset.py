import torch
from torch.utils.data import Dataset
import pandas as pd
import ast
from ..tokenizer.sales_tokenizer import SalesTokenizer

class LeadDataset(Dataset):
    """
    Dataset for loading and tokenizing lead data.
    """
    
    def __init__(self, csv_file, max_len=32):
        """
        Args:
            csv_file: Path to leads_raw.csv
            max_len: Maximum sequence length for padding
        """
        self.data = pd.read_csv(csv_file)
        self.tokenizer = SalesTokenizer()
        self.max_len = max_len
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        
        # Create lead dict expected by tokenizer
        lead_dict = {
            "months_in_role": row["months_in_role"],
            "funding_amount": row["funding_amount"],
            "own_views_3m": row["own_views_3m"],
            "own_views_1m": row["own_views_1m"],
            "comp_views_3m": row["comp_views_3m"],
            "comp_views_1m": row["comp_views_1m"],
        }
        
        # Tokenize
        _, token_ids = self.tokenizer.tokenize_lead(lead_dict)
        
        # Truncate if needed
        if len(token_ids) > self.max_len:
            token_ids = token_ids[:self.max_len]
            
        # Pad if needed
        # Assuming [PAD] is index 0 (SalesTokenizer initializes vocab with PAD first)
        pad_len = self.max_len - len(token_ids)
        if pad_len > 0:
            token_ids = token_ids + [0] * pad_len
            
        # Convert to tensors
        token_tensor = torch.tensor(token_ids, dtype=torch.long)
        label_tensor = torch.tensor([row["replied"]], dtype=torch.float32)
        
        return token_tensor, label_tensor
