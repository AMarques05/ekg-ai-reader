import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
callbacks = keras.callbacks
from backend.model.autoencoder import build_autoencoder

def train_autoencoder(X_train, X_val, save_path="backend/models/autoencoder.h5"):

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
    # Load datasets relative to the repo root when running: python -m backend.training.train_autoencoder
    X_train = np.load("backend/data/processed/X_train.npy")
    X_val   = np.load("backend/data/processed/X_val.npy")

    # Train and save
    _ = train_autoencoder(X_train, X_val)
