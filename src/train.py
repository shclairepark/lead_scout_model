import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import argparse
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.lead_scout import LeadScoutModel
from src.data.dataset import LeadDataset

def train(args):
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # 1. Load Data
    print("Loading data...")
    dataset = LeadDataset(args.data_path)
    
    # Train/Val split (80/20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    print(f"Train samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")
    
    # 2. Initialize Model
    model = LeadScoutModel(
        vocab_size=17,
        embed_dim=args.embed_dim,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        dropout=args.dropout
    ).to(device)
    
    # Weights & Criterion
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    
    # 3. Training History for visualization
    history = {
        'train_loss': [],
        'val_loss': [],
        'train_acc': [],
        'val_acc': [],
        'train_precision': [],
        'val_precision': [],
        'train_recall': [],
        'val_recall': [],
        'train_f1': [],
        'val_f1': []
    }
    
    # 4. Training Loop
    print("\nStarting training...")
    best_val_loss = float('inf')
    
    for epoch in range(args.epochs):
        # --- Training ---
        model.train()
        train_loss = 0.0
        train_preds = []
        train_labels_list = []
        
        for tokens, labels in train_loader:
            tokens, labels = tokens.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(tokens)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * tokens.size(0)
            
            # Collect predictions and labels
            predicted = (outputs > 0.5).float()
            train_preds.extend(predicted.cpu().numpy().flatten())
            train_labels_list.extend(labels.cpu().numpy().flatten())
        
        # Calculate training metrics
        train_preds_np = [int(p) for p in train_preds]
        train_labels_np = [int(l) for l in train_labels_list]
        
        avg_train_loss = train_loss / len(train_labels_list)
        train_acc = sum(1 for p, l in zip(train_preds_np, train_labels_np) if p == l) / len(train_labels_np)
        train_precision = precision_score(train_labels_np, train_preds_np, zero_division=0)
        train_recall = recall_score(train_labels_np, train_preds_np, zero_division=0)
        train_f1 = f1_score(train_labels_np, train_preds_np, zero_division=0)
        
        # --- Validation ---
        model.eval()
        val_loss = 0.0
        val_preds = []
        val_labels_list = []
        
        with torch.no_grad():
            for tokens, labels in val_loader:
                tokens, labels = tokens.to(device), labels.to(device)
                
                outputs = model(tokens)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * tokens.size(0)
                
                predicted = (outputs > 0.5).float()
                val_preds.extend(predicted.cpu().numpy().flatten())
                val_labels_list.extend(labels.cpu().numpy().flatten())
        
        # Calculate validation metrics
        val_preds_np = [int(p) for p in val_preds]
        val_labels_np = [int(l) for l in val_labels_list]
        
        avg_val_loss = val_loss / len(val_labels_list)
        val_acc = sum(1 for p, l in zip(val_preds_np, val_labels_np) if p == l) / len(val_labels_np)
        val_precision = precision_score(val_labels_np, val_preds_np, zero_division=0)
        val_recall = recall_score(val_labels_np, val_preds_np, zero_division=0)
        val_f1 = f1_score(val_labels_np, val_preds_np, zero_division=0)
        
        # Record history
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        history['train_precision'].append(train_precision)
        history['val_precision'].append(val_precision)
        history['train_recall'].append(train_recall)
        history['val_recall'].append(val_recall)
        history['train_f1'].append(train_f1)
        history['val_f1'].append(val_f1)
        
        print(f"Epoch {epoch+1}/{args.epochs} | "
              f"Train Loss: {avg_train_loss:.4f} Acc: {train_acc:.4f} F1: {train_f1:.4f} | "
              f"Val Loss: {avg_val_loss:.4f} Acc: {val_acc:.4f} F1: {val_f1:.4f}")
        
        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            os.makedirs(args.checkpoint_dir, exist_ok=True)
            torch.save(model.state_dict(), os.path.join(args.checkpoint_dir, 'lead_scout_best.pth'))

    # 5. Save training history
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    history_path = os.path.join(args.checkpoint_dir, 'training_history.json')
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"\nTraining history saved to {history_path}")

    # 6. Plot loss curves
    plot_training_curves(history, args.checkpoint_dir)

    print(f"\nTraining complete! Best validation loss: {best_val_loss:.4f}")
    print(f"Model saved to {args.checkpoint_dir}")
    
    # Print final metrics summary
    print("\n=== Final Metrics Summary ===")
    print(f"Train - Loss: {history['train_loss'][-1]:.4f}, Acc: {history['train_acc'][-1]:.4f}, "
          f"P: {history['train_precision'][-1]:.4f}, R: {history['train_recall'][-1]:.4f}, F1: {history['train_f1'][-1]:.4f}")
    print(f"Val   - Loss: {history['val_loss'][-1]:.4f}, Acc: {history['val_acc'][-1]:.4f}, "
          f"P: {history['val_precision'][-1]:.4f}, R: {history['val_recall'][-1]:.4f}, F1: {history['val_f1'][-1]:.4f}")


def plot_training_curves(history, output_dir):
    """Plot and save training curves for loss and metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    epochs = range(1, len(history['train_loss']) + 1)
    
    # Loss curve
    axes[0, 0].plot(epochs, history['train_loss'], 'b-', label='Train Loss')
    axes[0, 0].plot(epochs, history['val_loss'], 'r-', label='Val Loss')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Loss Curve')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Accuracy curve
    axes[0, 1].plot(epochs, history['train_acc'], 'b-', label='Train Acc')
    axes[0, 1].plot(epochs, history['val_acc'], 'r-', label='Val Acc')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Accuracy')
    axes[0, 1].set_title('Accuracy Curve')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Precision/Recall curve
    axes[1, 0].plot(epochs, history['train_precision'], 'b-', label='Train Precision')
    axes[1, 0].plot(epochs, history['val_precision'], 'r-', label='Val Precision')
    axes[1, 0].plot(epochs, history['train_recall'], 'b--', label='Train Recall')
    axes[1, 0].plot(epochs, history['val_recall'], 'r--', label='Val Recall')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Score')
    axes[1, 0].set_title('Precision & Recall Curves')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # F1 Score curve
    axes[1, 1].plot(epochs, history['train_f1'], 'b-', label='Train F1')
    axes[1, 1].plot(epochs, history['val_f1'], 'r-', label='Val F1')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('F1 Score')
    axes[1, 1].set_title('F1 Score Curve')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'training_curves.png')
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Training curves saved to {plot_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train Lead Scout Model')
    parser.add_argument('--data-path', type=str, default='data/leads_raw.csv', help='Path to CSV data')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--embed-dim', type=int, default=128, help='Embedding dimension')
    parser.add_argument('--num-heads', type=int, default=4, help='Number of attention heads')
    parser.add_argument('--num-layers', type=int, default=3, help='Number of transformer layers')
    parser.add_argument('--dropout', type=float, default=0.1, help='Dropout rate')
    parser.add_argument('--checkpoint-dir', type=str, default='checkpoints', help='Directory to save checkpoints')
    
    args = parser.parse_args()
    
    # Resolve absolute path for data default
    if not os.path.isabs(args.data_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.data_path = os.path.join(base_dir, args.data_path)
        
    train(args)
