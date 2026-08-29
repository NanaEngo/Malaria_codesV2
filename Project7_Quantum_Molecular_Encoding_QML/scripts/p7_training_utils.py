"""
P7 — Training Utilities for Hybrid QML Models

Provides training loops, evaluation functions, and logging utilities
for hybrid quantum-classical models.

Key functions:
  - train_hybrid_model(): End-to-end training with validation
  - evaluate_model(): Compute metrics (AUC, accuracy, F1)
  - train_epoch(): Single epoch training
  - validate_epoch(): Single epoch validation
  - log_metrics(): Save metrics to JSON

Usage:
    from p7_training_utils import train_hybrid_model
    
    history = train_hybrid_model(
        model=hybrid_qnn,
        train_loader=train_loader,
        val_loader=val_loader,
        n_epochs=50,
        lr=0.01
    )
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import (
    roc_auc_score, accuracy_score, f1_score,
    precision_score, recall_score, confusion_matrix
)
from tqdm import tqdm


def train_epoch(
    model: nn.Module,
    train_loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
    epoch: int,
    verbose: bool = True
) -> Dict[str, float]:
    """
    Train model for one epoch.
    
    Args:
        model: Hybrid QML model
        train_loader: Training data loader
        criterion: Loss function (e.g., BCELoss)
        optimizer: Optimizer (e.g., Adam)
        device: torch.device ('cpu' or 'cuda')
        epoch: Current epoch number
        verbose: Print progress
    
    Returns:
        Dict with epoch metrics
    """
    model.train()
    
    running_loss = 0.0
    all_preds = []
    all_labels = []
    
    iterator = tqdm(train_loader, desc=f"Epoch {epoch}") if verbose else train_loader
    
    for batch_idx, (features, labels) in enumerate(iterator):
        features = features.to(device)
        labels = labels.to(device).float().unsqueeze(1)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(features)
        
        # Compute loss
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        
        # Update weights
        optimizer.step()
        
        # Track metrics
        running_loss += loss.item()
        all_preds.extend(outputs.detach().cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        
        if verbose and batch_idx % 10 == 0:
            iterator.set_postfix({'loss': loss.item()})
    
    # Compute epoch metrics
    all_preds = np.array(all_preds).flatten()
    all_labels = np.array(all_labels).flatten()
    
    avg_loss = running_loss / len(train_loader)
    
    # Binary predictions
    binary_preds = (all_preds >= 0.5).astype(int)
    
    metrics = {
        'loss': avg_loss,
        'accuracy': float(accuracy_score(all_labels, binary_preds)),
        'f1': float(f1_score(all_labels, binary_preds, zero_division=0))
    }
    
    # AUC (only if both classes present)
    if len(np.unique(all_labels)) > 1:
        metrics['auc'] = float(roc_auc_score(all_labels, all_preds))
    else:
        metrics['auc'] = 0.0
    
    return metrics


def validate_epoch(
    model: nn.Module,
    val_loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
    verbose: bool = False
) -> Dict[str, float]:
    """
    Validate model for one epoch.
    
    Args:
        model: Hybrid QML model
        val_loader: Validation data loader
        criterion: Loss function
        device: torch.device
        verbose: Print progress
    
    Returns:
        Dict with validation metrics
    """
    model.eval()
    
    running_loss = 0.0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        iterator = tqdm(val_loader, desc="Validation") if verbose else val_loader
        
        for features, labels in iterator:
            features = features.to(device)
            labels = labels.to(device).float().unsqueeze(1)
            
            # Forward pass
            outputs = model(features)
            
            # Compute loss
            loss = criterion(outputs, labels)
            
            # Track metrics
            running_loss += loss.item()
            all_preds.extend(outputs.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Compute metrics
    all_preds = np.array(all_preds).flatten()
    all_labels = np.array(all_labels).flatten()
    
    avg_loss = running_loss / len(val_loader)
    binary_preds = (all_preds >= 0.5).astype(int)
    
    metrics = {
        'loss': avg_loss,
        'accuracy': float(accuracy_score(all_labels, binary_preds)),
        'f1': float(f1_score(all_labels, binary_preds, zero_division=0)),
        'precision': float(precision_score(all_labels, binary_preds, zero_division=0)),
        'recall': float(recall_score(all_labels, binary_preds, zero_division=0))
    }
    
    # AUC
    if len(np.unique(all_labels)) > 1:
        metrics['auc'] = float(roc_auc_score(all_labels, all_preds))
    else:
        metrics['auc'] = 0.0
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, binary_preds)
    if cm.shape == (2, 2):
        metrics['tn'] = int(cm[0, 0])
        metrics['fp'] = int(cm[0, 1])
        metrics['fn'] = int(cm[1, 0])
        metrics['tp'] = int(cm[1, 1])
    
    return metrics


def train_hybrid_model(
    model: nn.Module,
    train_loader: torch.utils.data.DataLoader,
    val_loader: Optional[torch.utils.data.DataLoader] = None,
    n_epochs: int = 50,
    lr: float = 0.01,
    weight_decay: float = 1e-4,
    early_stopping_patience: int = 10,
    checkpoint_dir: Optional[Path] = None,
    device: Optional[torch.device] = None,
    verbose: bool = True
) -> Dict:
    """
    Train hybrid quantum-classical model with early stopping.
    
    Args:
        model: Hybrid QML model
        train_loader: Training data loader
        val_loader: Validation data loader (optional)
        n_epochs: Maximum number of epochs
        lr: Learning rate
        weight_decay: L2 regularization
        early_stopping_patience: Epochs to wait for improvement
        checkpoint_dir: Directory to save checkpoints
        device: torch.device (auto-detect if None)
        verbose: Print training progress
    
    Returns:
        Dict with training history
    """
    # Device
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = model.to(device)
    
    # Loss function
    criterion = nn.BCELoss()
    
    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=verbose
    )
    
    # Training history
    history = {
        'train_loss': [],
        'train_auc': [],
        'train_accuracy': [],
        'val_loss': [],
        'val_auc': [],
        'val_accuracy': [],
        'lr': [],
        'epoch_time': []
    }
    
    best_val_loss = float('inf')
    patience_counter = 0
    best_epoch = 0
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Training Hybrid QML Model")
        print(f"{'='*60}")
        print(f"Device: {device}")
        print(f"Epochs: {n_epochs}")
        print(f"Learning rate: {lr}")
        print(f"Batch size: {train_loader.batch_size}")
        print(f"Training samples: {len(train_loader.dataset)}")
        if val_loader:
            print(f"Validation samples: {len(val_loader.dataset)}")
        print(f"{'='*60}\n")
    
    # Training loop
    for epoch in range(1, n_epochs + 1):
        epoch_start = time.time()
        
        # Train
        train_metrics = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch, verbose
        )
        
        # Validate (if validation set provided)
        if val_loader:
            val_metrics = validate_epoch(
                model, val_loader, criterion, device, verbose
            )
        else:
            val_metrics = {'loss': 0.0, 'auc': 0.0, 'accuracy': 0.0}
        
        epoch_time = time.time() - epoch_start
        
        # Update history
        history['train_loss'].append(train_metrics['loss'])
        history['train_auc'].append(train_metrics['auc'])
        history['train_accuracy'].append(train_metrics['accuracy'])
        history['val_loss'].append(val_metrics['loss'])
        history['val_auc'].append(val_metrics['auc'])
        history['val_accuracy'].append(val_metrics['accuracy'])
        history['lr'].append(optimizer.param_groups[0]['lr'])
        history['epoch_time'].append(epoch_time)
        
        # Learning rate scheduling
        if val_loader:
            scheduler.step(val_metrics['loss'])
        else:
            scheduler.step(train_metrics['loss'])
        
        # Print epoch summary
        if verbose:
            print(f"\nEpoch {epoch}/{n_epochs} ({epoch_time:.1f}s)")
            print(f"  Train - Loss: {train_metrics['loss']:.4f}, "
                  f"AUC: {train_metrics['auc']:.4f}, "
                  f"Acc: {train_metrics['accuracy']:.4f}")
            if val_loader:
                print(f"  Val   - Loss: {val_metrics['loss']:.4f}, "
                      f"AUC: {val_metrics['auc']:.4f}, "
                      f"Acc: {val_metrics['accuracy']:.4f}")
        
        # Early stopping (on validation loss)
        if val_loader:
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                patience_counter = 0
                best_epoch = epoch
                
                # Save best model
                if checkpoint_dir:
                    checkpoint_dir.mkdir(parents=True, exist_ok=True)
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'val_loss': val_metrics['loss'],
                        'val_auc': val_metrics['auc']
                    }, checkpoint_dir / 'best_model.pt')
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    if verbose:
                        print(f"\nEarly stopping at epoch {epoch}")
                        print(f"Best epoch: {best_epoch} (val_loss: {best_val_loss:.4f})")
                    break
        
        # Check for gradient vanishing (if model has quantum layers)
        if hasattr(model, 'check_gradient_vanishing'):
            grad_stats = model.check_gradient_vanishing()
            if grad_stats['is_vanishing'] and verbose:
                print(f"  ⚠️  WARNING: Quantum gradients vanishing (norm: {grad_stats['norm']:.2e})")
    
    # Load best model
    if checkpoint_dir and val_loader:
        best_checkpoint = checkpoint_dir / 'best_model.pt'
        if best_checkpoint.exists():
            checkpoint = torch.load(best_checkpoint)
            model.load_state_dict(checkpoint['model_state_dict'])
            if verbose:
                print(f"\nLoaded best model from epoch {checkpoint['epoch']}")
    
    # Final summary
    if verbose:
        print(f"\n{'='*60}")
        print(f"Training Complete")
        print(f"{'='*60}")
        print(f"Best epoch: {best_epoch}")
        if val_loader:
            print(f"Best val loss: {best_val_loss:.4f}")
            print(f"Final val AUC: {history['val_auc'][best_epoch-1]:.4f}")
        print(f"Total time: {sum(history['epoch_time']):.1f}s")
        print(f"{'='*60}\n")
    
    return history


def evaluate_model(
    model: nn.Module,
    test_loader: torch.utils.data.DataLoader,
    device: Optional[torch.device] = None,
    return_predictions: bool = False
) -> Dict:
    """
    Evaluate trained model on test set.
    
    Args:
        model: Trained model
        test_loader: Test data loader
        device: torch.device
        return_predictions: Return predictions and labels
    
    Returns:
        Dict with test metrics (and predictions if requested)
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for features, labels in tqdm(test_loader, desc="Evaluating"):
            features = features.to(device)
            outputs = model(features)
            
            all_preds.extend(outputs.cpu().numpy())
            all_labels.extend(labels.numpy())
    
    # Convert to arrays
    all_preds = np.array(all_preds).flatten()
    all_labels = np.array(all_labels).flatten()
    binary_preds = (all_preds >= 0.5).astype(int)
    
    # Compute metrics
    metrics = {
        'auc': float(roc_auc_score(all_labels, all_preds)) if len(np.unique(all_labels)) > 1 else 0.0,
        'accuracy': float(accuracy_score(all_labels, binary_preds)),
        'f1': float(f1_score(all_labels, binary_preds, zero_division=0)),
        'precision': float(precision_score(all_labels, binary_preds, zero_division=0)),
        'recall': float(recall_score(all_labels, binary_preds, zero_division=0))
    }
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, binary_preds)
    if cm.shape == (2, 2):
        metrics['tn'] = int(cm[0, 0])
        metrics['fp'] = int(cm[0, 1])
        metrics['fn'] = int(cm[1, 0])
        metrics['tp'] = int(cm[1, 1])
    
    if return_predictions:
        metrics['predictions'] = all_preds.tolist()
        metrics['labels'] = all_labels.tolist()
    
    return metrics


def log_metrics(
    metrics: Dict,
    output_file: Path,
    metadata: Optional[Dict] = None
):
    """
    Save metrics to JSON file with timestamp and metadata.
    
    Args:
        metrics: Dict of metrics to save
        output_file: Path to output JSON file
        metadata: Optional metadata (model config, hyperparameters, etc.)
    """
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics
    }
    
    if metadata:
        log_data['metadata'] = metadata
    
    with open(output_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"Metrics saved: {output_file}")


def save_model(
    model: nn.Module,
    output_file: Path,
    metadata: Optional[Dict] = None
):
    """
    Save model checkpoint with metadata.
    
    Args:
        model: Trained model
        output_file: Path to output .pt file
        metadata: Optional metadata
    """
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    checkpoint = {
        'timestamp': datetime.now().isoformat(),
        'model_state_dict': model.state_dict()
    }
    
    if metadata:
        checkpoint['metadata'] = metadata
    
    # Save quantum weights separately if available
    if hasattr(model, 'get_quantum_weights'):
        checkpoint['quantum_weights'] = model.get_quantum_weights().tolist()
    
    torch.save(checkpoint, output_file)
    print(f"Model saved: {output_file}")


def load_model(
    model: nn.Module,
    checkpoint_file: Path,
    device: Optional[torch.device] = None
) -> nn.Module:
    """
    Load model from checkpoint.
    
    Args:
        model: Model instance (architecture must match)
        checkpoint_file: Path to checkpoint .pt file
        device: torch.device
    
    Returns:
        Loaded model
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    checkpoint = torch.load(checkpoint_file, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    print(f"Model loaded: {checkpoint_file}")
    if 'timestamp' in checkpoint:
        print(f"  Timestamp: {checkpoint['timestamp']}")
    
    return model


if __name__ == "__main__":
    print("=" * 60)
    print("P7 Training Utilities Test")
    print("=" * 60)
    
    # Create dummy data
    from torch.utils.data import TensorDataset, DataLoader
    
    X_train = torch.randn(100, 2048)
    y_train = torch.randint(0, 2, (100,))
    X_val = torch.randn(20, 2048)
    y_val = torch.randint(0, 2, (20,))
    
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16)
    
    # Import model
    from p7_quantum_layers import HybridQNN
    
    # Create model
    model = HybridQNN(n_features=2048, n_qubits=4, n_layers=1)
    
    print("\nTraining for 5 epochs (test)...")
    history = train_hybrid_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        n_epochs=5,
        lr=0.01,
        verbose=True
    )
    
    print("\nEvaluating...")
    metrics = evaluate_model(model, val_loader)
    print(f"  AUC: {metrics['auc']:.4f}")
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ Training utilities test complete!")
    print("=" * 60)
