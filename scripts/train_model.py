import json
import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Add project root to path
sys.path.append(os.getcwd())

from src.model.lead_scout import LeadScoutModel
from src.tokenizer.sales_tokenizer import SalesTokenizer

class LeadDataset(Dataset):
    def __init__(self, data_path):
        with open(data_path, 'r') as f:
            self.data = json.load(f)
            
    def __len__(self):
        return len(self.data)
        
    def __getitem__(self, idx):
        item = self.data[idx]
        return {
            "token_ids": torch.tensor(item["token_ids"], dtype=torch.long),
            "label": torch.tensor([item["label"]], dtype=torch.float32)
        }

def collate_fn(batch):
    # Dynamic padding
    max_len = max([len(x["token_ids"]) for x in batch])
    
    padded_ids = []
    labels = []
    
    for x in batch:
        ids = x["token_ids"]
        pad_len = max_len - len(ids)
        # Pad with 0
        padded = torch.cat([ids, torch.zeros(pad_len, dtype=torch.long)])
        padded_ids.append(padded)
        labels.append(x["label"])
        
    return torch.stack(padded_ids), torch.stack(labels)

def train():
    print("🚀 Starting LeadScout Model Training...")
    
    # 1. Load Data
    data_path = "data/training_data.json"
    if not os.path.exists(data_path):
        print("❌ Data not found. Run generate_training_data.py first.")
        return
        
    dataset = LeadDataset(data_path)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True, collate_fn=collate_fn)
    
    # 2. Init Model
    tokenizer = SalesTokenizer()
    vocab_size = len(tokenizer.vocab)
    print(f"   Vocab Size: {vocab_size}")
    
    model = LeadScoutModel(
        vocab_size=vocab_size,
        embed_dim=64,  # Small model for demo
        num_heads=2,
        num_layers=2,
        ff_dim=128
    )
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 3. Training Loop
    epochs = 5
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_ids, batch_labels in dataloader:
            optimizer.zero_grad()
            
            outputs = model(batch_ids)
            loss = criterion(outputs, batch_labels)
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        print(f"   Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f}")
        
    # 4. Save
    os.makedirs("checkpoints", exist_ok=True)
    save_path = "checkpoints/lead_scout_best.pth"
    torch.save(model.state_dict(), save_path)
    print(f"✅ Model saved to {save_path}")

if __name__ == "__main__":
    train()
