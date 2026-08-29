"""
P7 — Test Hybrid QML Implementation

Comprehensive test suite to verify all components work correctly
before running on real data (P1 Set A or P3 benchmark).

Tests:
  1. Quantum layers (VQC, QuantumFeatureExtractor, HybridQNN)
  2. Training utilities (training loop, evaluation, logging)
  3. End-to-end hybrid model training (dummy data)
  4. Gradient computation and vanishing check
  5. Model saving and loading
  6. Integration test (data → train → evaluate → save)

Usage:
    python scripts/test_hybrid_implementation.py
    
Expected output:
    ✅ All tests passed! (Ready for Phase 1 execution)
"""

import sys
import tempfile
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

# Import P7 modules
try:
    from p7_quantum_layers import (
        VQCLayer,
        QuantumFeatureExtractor,
        HybridQNN,
        DualPathQuantumNet,
        count_quantum_parameters
    )
    from p7_training_utils import (
        train_hybrid_model,
        evaluate_model,
        log_metrics,
        save_model,
        load_model
    )
    print("✅ Successfully imported P7 modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure you're in the correct directory:")
    print("  cd /home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML")
    sys.exit(1)


def test_quantum_layers():
    """Test 1: Quantum layer forward passes and gradient flow."""
    print("\n" + "=" * 60)
    print("Test 1: Quantum Layers")
    print("=" * 60)
    
    # Test VQCLayer
    print("\n1.1 VQCLayer...")
    try:
        vqc = VQCLayer(n_qubits=4, n_layers=2, entangling='cnot')
        x = torch.randn(2, 4)  # batch_size=2, n_qubits=4
        y = vqc(x)
        
        assert y.shape == (2, 4), f"Expected (2, 4), got {y.shape}"
        assert y.min() >= -1.0 and y.max() <= 1.0, f"Output out of range [-1, 1]: [{y.min():.3f}, {y.max():.3f}]"
        print(f"  ✅ Forward pass OK: {x.shape} → {y.shape}")
        
        # Test gradient
        loss = y.sum()
        loss.backward()
        assert vqc.weights.grad is not None, "Gradients not computed"
        grad_norm = torch.norm(vqc.weights.grad).item()
        print(f"  ✅ Gradient OK: norm = {grad_norm:.6f}")
        
    except Exception as e:
        print(f"  ❌ VQCLayer failed: {e}")
        raise
    
    # Test QuantumFeatureExtractor
    print("\n1.2 QuantumFeatureExtractor...")
    try:
        qfe = QuantumFeatureExtractor(n_features=2048, n_qubits=4, n_layers=2)
        x = torch.randn(2, 2048)  # ECFP4-like
        y = qfe(x)
        
        assert y.shape == (2, 4), f"Expected (2, 4), got {y.shape}"
        print(f"  ✅ Forward pass OK: {x.shape} → {y.shape}")
        
    except Exception as e:
        print(f"  ❌ QuantumFeatureExtractor failed: {e}")
        raise
    
    # Test HybridQNN
    print("\n1.3 HybridQNN (full model)...")
    try:
        model = HybridQNN(n_features=2048, n_qubits=4, n_layers=2, hidden_dim=64)
        x = torch.randn(2, 2048)
        y = model(x)
        
        assert y.shape == (2, 1), f"Expected (2, 1), got {y.shape}"
        assert (y >= 0).all() and (y <= 1).all(), f"Output not in [0, 1]: [{y.min():.3f}, {y.max():.3f}]"
        print(f"  ✅ Forward pass OK: {x.shape} → {y.shape}")
        print(f"  ✅ Output range: [{y.min():.3f}, {y.max():.3f}]")
        
        # Parameter count
        params = count_quantum_parameters(model)
        print(f"  ✅ Parameters: Total={params['total']}, Quantum={params['quantum']}, Classical={params['classical']}")
        
    except Exception as e:
        print(f"  ❌ HybridQNN failed: {e}")
        raise
    
    # Test DualPathQuantumNet
    print("\n1.4 DualPathQuantumNet (ablation model)...")
    try:
        # With quantum
        model_quantum = DualPathQuantumNet(n_features=2048, n_qubits=4, use_quantum=True)
        x = torch.randn(2, 2048)
        y_quantum = model_quantum(x)
        assert y_quantum.shape == (2, 1), f"Expected (2, 1), got {y_quantum.shape}"
        print(f"  ✅ With quantum: {x.shape} → {y_quantum.shape}")
        
        # Without quantum
        model_classical = DualPathQuantumNet(n_features=2048, n_qubits=4, use_quantum=False)
        y_classical = model_classical(x)
        assert y_classical.shape == (2, 1), f"Expected (2, 1), got {y_classical.shape}"
        print(f"  ✅ Without quantum: {x.shape} → {y_classical.shape}")
        
    except Exception as e:
        print(f"  ❌ DualPathQuantumNet failed: {e}")
        raise
    
    print("\n✅ All quantum layer tests passed!")
    return True


def test_training_utilities():
    """Test 2: Training and evaluation utilities."""
    print("\n" + "=" * 60)
    print("Test 2: Training Utilities")
    print("=" * 60)
    
    # Create dummy data
    print("\n2.1 Creating dummy dataset...")
    X_train = torch.randn(50, 2048)
    y_train = torch.randint(0, 2, (50,))
    X_val = torch.randn(20, 2048)
    y_val = torch.randint(0, 2, (20,))
    
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16)
    
    print(f"  ✅ Train: {len(train_dataset)} samples")
    print(f"  ✅ Val: {len(val_dataset)} samples")
    
    # Create model
    print("\n2.2 Creating HybridQNN...")
    model = HybridQNN(n_features=2048, n_qubits=4, n_layers=1, hidden_dim=32)  # Small for speed
    print(f"  ✅ Model created")
    
    # Train
    print("\n2.3 Training for 3 epochs (test)...")
    try:
        history = train_hybrid_model(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            n_epochs=3,
            lr=0.01,
            early_stopping_patience=5,
            verbose=False
        )
        
        assert 'train_loss' in history, "Missing train_loss in history"
        assert 'val_auc' in history, "Missing val_auc in history"
        assert len(history['train_loss']) <= 3, f"Expected ≤3 epochs, got {len(history['train_loss'])}"
        
        print(f"  ✅ Training complete: {len(history['train_loss'])} epochs")
        print(f"  ✅ Final train loss: {history['train_loss'][-1]:.4f}")
        print(f"  ✅ Final val AUC: {history['val_auc'][-1]:.4f}")
        
    except Exception as e:
        print(f"  ❌ Training failed: {e}")
        raise
    
    # Evaluate
    print("\n2.4 Evaluating on validation set...")
    try:
        metrics = evaluate_model(model, val_loader, return_predictions=False)
        
        assert 'auc' in metrics, "Missing AUC in metrics"
        assert 'accuracy' in metrics, "Missing accuracy in metrics"
        assert 'f1' in metrics, "Missing F1 in metrics"
        
        print(f"  ✅ AUC: {metrics['auc']:.4f}")
        print(f"  ✅ Accuracy: {metrics['accuracy']:.4f}")
        print(f"  ✅ F1: {metrics['f1']:.4f}")
        
    except Exception as e:
        print(f"  ❌ Evaluation failed: {e}")
        raise
    
    # Gradient check
    print("\n2.5 Checking gradient vanishing...")
    try:
        grad_stats = model.check_gradient_vanishing()
        
        assert 'status' in grad_stats, "Missing status in grad_stats"
        assert 'norm' in grad_stats, "Missing norm in grad_stats"
        
        print(f"  ✅ Gradient status: {grad_stats['status']}")
        print(f"  ✅ Gradient norm: {grad_stats['norm']:.6f}")
        
        if grad_stats['is_vanishing']:
            print(f"  ⚠️  WARNING: Gradients vanishing (but test passed)")
        
    except Exception as e:
        print(f"  ❌ Gradient check failed: {e}")
        raise
    
    print("\n✅ All training utility tests passed!")
    return model, metrics


def test_model_io():
    """Test 3: Model saving and loading."""
    print("\n" + "=" * 60)
    print("Test 3: Model I/O")
    print("=" * 60)
    
    # Create model
    print("\n3.1 Creating model...")
    model = HybridQNN(n_features=2048, n_qubits=4, n_layers=1)
    
    # Get quantum weights
    weights_before = model.get_quantum_weights()
    print(f"  ✅ Quantum weights shape: {weights_before.shape}")
    
    # Save
    print("\n3.2 Saving model...")
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "test_model.pt"
        
        try:
            save_model(
                model=model,
                output_file=model_path,
                metadata={'test': True, 'qubits': 4}
            )
            assert model_path.exists(), f"Model file not created: {model_path}"
            print(f"  ✅ Model saved: {model_path}")
            
        except Exception as e:
            print(f"  ❌ Save failed: {e}")
            raise
        
        # Load
        print("\n3.3 Loading model...")
        try:
            model_new = HybridQNN(n_features=2048, n_qubits=4, n_layers=1)
            model_loaded = load_model(model_new, model_path, device=torch.device('cpu'))
            
            # Check weights match
            weights_after = model_loaded.get_quantum_weights()
            assert np.allclose(weights_before, weights_after), "Weights don't match after loading"
            print(f"  ✅ Model loaded successfully")
            print(f"  ✅ Weights match: {np.allclose(weights_before, weights_after)}")
            
        except Exception as e:
            print(f"  ❌ Load failed: {e}")
            raise
    
    print("\n✅ Model I/O tests passed!")
    return True


def test_metrics_logging():
    """Test 4: Metrics logging."""
    print("\n" + "=" * 60)
    print("Test 4: Metrics Logging")
    print("=" * 60)
    
    # Create dummy metrics
    metrics = {
        'auc': 0.8523,
        'accuracy': 0.7850,
        'f1': 0.7234
    }
    
    metadata = {
        'model': 'HybridQNN',
        'qubits': 4,
        'depth': 2,
        'test': True
    }
    
    # Save
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_path = Path(tmpdir) / "test_metrics.json"
        
        try:
            log_metrics(metrics, metrics_path, metadata)
            assert metrics_path.exists(), f"Metrics file not created: {metrics_path}"
            print(f"  ✅ Metrics saved: {metrics_path}")
            
            # Load and verify
            import json
            with open(metrics_path, 'r') as f:
                logged = json.load(f)
            
            assert 'metrics' in logged, "Missing 'metrics' key"
            assert 'metadata' in logged, "Missing 'metadata' key"
            assert 'timestamp' in logged, "Missing 'timestamp' key"
            
            assert logged['metrics']['auc'] == 0.8523, "AUC mismatch"
            assert logged['metadata']['qubits'] == 4, "Metadata mismatch"
            
            print(f"  ✅ Metrics verified")
            
        except Exception as e:
            print(f"  ❌ Logging failed: {e}")
            raise
    
    print("\n✅ Metrics logging tests passed!")
    return True


def test_end_to_end():
    """Test 5: End-to-end integration test."""
    print("\n" + "=" * 60)
    print("Test 5: End-to-End Integration")
    print("=" * 60)
    
    print("\n5.1 Creating synthetic dataset...")
    # Create realistic synthetic data
    n_train = 80
    n_test = 20
    
    X_train = torch.randn(n_train, 2048) * 0.3  # Normalized features
    y_train = torch.randint(0, 2, (n_train,))
    X_test = torch.randn(n_test, 2048) * 0.3
    y_test = torch.randint(0, 2, (n_test,))
    
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=16)
    
    print(f"  ✅ Train: {n_train} samples, Test: {n_test} samples")
    
    print("\n5.2 Creating hybrid QML model...")
    model = HybridQNN(n_features=2048, n_qubits=4, n_layers=1, hidden_dim=32)
    print(f"  ✅ Model created")
    
    print("\n5.3 Training (5 epochs)...")
    try:
        history = train_hybrid_model(
            model=model,
            train_loader=train_loader,
            val_loader=None,  # No validation for simplicity
            n_epochs=5,
            lr=0.01,
            verbose=False
        )
        print(f"  ✅ Training complete: {len(history['train_loss'])} epochs")
        print(f"  ✅ Final train loss: {history['train_loss'][-1]:.4f}")
        
    except Exception as e:
        print(f"  ❌ Training failed: {e}")
        raise
    
    print("\n5.4 Evaluating on test set...")
    try:
        metrics = evaluate_model(model, test_loader, return_predictions=True)
        print(f"  ✅ Test AUC: {metrics['auc']:.4f}")
        print(f"  ✅ Test Accuracy: {metrics['accuracy']:.4f}")
        print(f"  ✅ Test F1: {metrics['f1']:.4f}")
        
    except Exception as e:
        print(f"  ❌ Evaluation failed: {e}")
        raise
    
    print("\n5.5 Checking gradient behavior...")
    grad_stats = model.check_gradient_vanishing()
    print(f"  ✅ Gradient status: {grad_stats['status']}")
    print(f"  ✅ Gradient norm: {grad_stats['norm']:.6f}")
    
    if grad_stats['is_vanishing']:
        print(f"  ⚠️  WARNING: Gradients are vanishing")
        print(f"      This may affect training on real data")
        print(f"      Solutions: reduce depth, change entangling gate, increase LR")
    
    print("\n5.6 Saving results...")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save model
        model_path = Path(tmpdir) / "final_model.pt"
        save_model(model, model_path, metadata={'test': 'end_to_end'})
        print(f"  ✅ Model saved: {model_path.name}")
        
        # Save metrics
        metrics_path = Path(tmpdir) / "final_metrics.json"
        log_metrics(metrics, metrics_path, metadata={'test': 'end_to_end'})
        print(f"  ✅ Metrics saved: {metrics_path.name}")
    
    print("\n✅ End-to-end integration test passed!")
    return True


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 60)
    print("P7 HYBRID QML IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    print("\nVerifying all components before Phase 1 execution...")
    
    tests = [
        ("Quantum Layers", test_quantum_layers),
        ("Training Utilities", test_training_utilities),
        ("Model I/O", test_model_io),
        ("Metrics Logging", test_metrics_logging),
        ("End-to-End Integration", test_end_to_end)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🚀 System is ready for Phase 1 execution!")
        print("\nNext steps:")
        print("  1. Prepare data: python scripts/p7_data_preparation.py --p1-only")
        print("  2. Run Phase 1: python scripts/p7_hybrid_vqc.py --p1-set-a --qubits 4 --depth 2 --epochs 50")
        print("\nExpected time: ~30-60 minutes (CPU), ~10-20 minutes (GPU)")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the issues before running Phase 1.")
        print("Check error messages above for details.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
