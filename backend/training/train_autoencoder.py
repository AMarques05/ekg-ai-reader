import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
callbacks = keras.callbacks
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from backend
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.model.autoencoder import build_autoencoder

def train_autoencoder(X_train, X_val, save_path="autoencoder.h5"):

    input_len = X_train.shape[1]  # number of samples per window

    # Build a fresh model
    model = build_autoencoder(input_len)

    # Early stopping: stop training if val_loss doesn't improve for 5 epochs
    es = callbacks.EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True
    )

    # Log shapes for visibility
    print(f"Training on: X_train {X_train.shape}, validating on: X_val {X_val.shape}")

    # Fit the model: input = X, target = X (reconstruction)
    history = model.fit(
        X_train, X_train,              
        validation_data=(X_val, X_val),
        epochs=50,
        batch_size=128,
        callbacks=[es],
        verbose=2
    )

    # Save trained model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    print(f"Model saved to {save_path}")

    return history


if __name__ == "__main__":
    # Get paths relative to this script
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data" / "processed"
    
    # Load datasets
    X_train = np.load(data_dir / "X_train.npy")
    X_val   = np.load(data_dir / "X_val.npy")

    # Set save path for the trained model
    model_save_path = script_dir.parent / "model" / "saved" / "autoencoder.h5"

    # Train and save
    _ = train_autoencoder(X_train, X_val, save_path=str(model_save_path))
